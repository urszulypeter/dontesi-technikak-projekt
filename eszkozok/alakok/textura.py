"""Rocketbox TGA textúrák → webes WebP. A katonai ACU-mintát magyaros zöld-barnára színezi.

Munkakönyvtárból futtatandó (a repón kívül — a forrás ~1 GB):
    bash letolt.sh && python3 textura.py && node glb.mjs <repo>/assets/alak
Bemenet: ./rbsrc/<alak>/*.tga, kimenet: ./tex/<alak>/*.webp"""
import pathlib, re, sys
import numpy as np
from PIL import Image

FORRAS = pathlib.Path.cwd() / "rbsrc"
CEL = pathlib.Path.cwd() / "tex"

MERET_SZIN = {"body": 1024, "head": 1024}
MERET_NORM = {"body": 512, "head": 512}

# luminancia-sávok → 2015M-szerű paletta (sötét olajzöld, barnászöld, fakó homok)
PALETTA = np.array([[52, 58, 38], [86, 88, 58], [118, 104, 72], [150, 140, 104]], dtype=np.float32)

def atszinez(rgb):
    a = rgb.astype(np.float32) / 255
    mx, mn = a.max(2), a.min(2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    lum = 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    # zászló és telített felvarrók: piros vagy kék, erősen telített
    piros = (sat > 0.55) & (r > g * 2.3) & (r > b * 2.0) & (r > 0.35)
    kek = (sat > 0.35) & (b > r * 1.25) & (b > g * 1.05)
    # a terepszín zöldesszürke: a vörös csatorna nem emelkedik ki (a bőr és a bakancs igen)
    terepszin = (sat < 0.20) & (lum > 0.12) & ((r - g) < 0.025)
    # zászló és felvarró: a telített foltot kitágítjuk, és a helyére a fölötte lévő mintát másoljuk
    folt = piros | kek
    if folt.any():
        from PIL import ImageFilter
        tag = np.asarray(Image.fromarray((folt * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(41))) > 0
        felette = np.roll(a, -260, axis=0)
        a = np.where(tag[..., None], felette, a)
        mx, mn = a.max(2), a.min(2)
        sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
        lum = 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
        r, g, b = a[..., 0], a[..., 1], a[..., 2]
        terepszin = (sat < 0.20) & (lum > 0.12) & ((r - g) < 0.025)
    maszk = terepszin
    l = lum
    # sávhatárok az ACU három tónusához igazítva, lágy átmenettel
    t = np.clip((l - 0.30) / 0.42, 0, 1) * (len(PALETTA) - 1)
    i0 = np.floor(t).astype(int).clip(0, len(PALETTA) - 2)
    f = (t - i0)[..., None]
    uj = PALETTA[i0] * (1 - f) + PALETTA[i0 + 1] * f
    # a szövet árnyékait megtartjuk: a helyi fényesség finom modulációja
    uj *= (0.80 + 0.40 * lum)[..., None]
    ki = np.where(maszk[..., None], uj, a * 255)
    return ki.clip(0, 255).astype(np.uint8)

def main(nevek):
    for d in sorted(FORRAS.iterdir()):
        if not d.is_dir() or (nevek and d.name not in nevek): continue
        cel = CEL / d.name; cel.mkdir(parents=True, exist_ok=True)
        for f in sorted(d.glob("*.tga")):
            m = re.match(r"([a-z]+\d+)_(\w+?)_(color|normal)(_acu)?\.tga$", f.name)
            if not m:
                print("kihagyva", f); continue
            elotag, resz, fajta, acu = m.groups()
            img = Image.open(f)
            if fajta == "color":
                meret = MERET_SZIN.get(resz, 512)
                if resz == "opacity":
                    img = img.convert("RGBA").resize((meret, meret), Image.LANCZOS)
                    img.save(cel / f"{resz}_c.webp", quality=85, method=6)
                    continue
                rgb = np.asarray(img.convert("RGB"))
                if acu: rgb = atszinez(rgb)
                Image.fromarray(rgb).resize((meret, meret), Image.LANCZOS).save(cel / f"{resz}_c.webp", quality=82, method=6)
            else:
                meret = MERET_NORM.get(resz, 256)
                img.convert("RGB").resize((meret, meret), Image.LANCZOS).save(cel / f"{resz}_n.webp", quality=88, method=6)
        print(d.name, sum(p.stat().st_size for p in cel.iterdir()) // 1024, "KB")

if __name__ == "__main__":
    main(sys.argv[1:])
