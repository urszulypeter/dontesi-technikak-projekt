"""Poly Haven (CC0) modellek letöltése 1k glTF-ként a munkakönyvtárba.

    python3 polyhaven_letolt.py metal_office_desk dining_chair_02 …
Utána: gltf-transform optimize <nev>.gltf <nev>.glb --compress meshopt --texture-compress webp --texture-size 512 --simplify false"""
import json, urllib.request, pathlib, sys, concurrent.futures as cf
UA = {"User-Agent": "vezetoi-bizalom-asset-pipeline/1.0"}
def nyit(url): return urllib.request.urlopen(urllib.request.Request(url, headers=UA))
def ment(url, p):
    with nyit(url) as r: p.write_bytes(r.read())
NEVEK = sys.argv[1:]
def egy(nev):
    if pathlib.Path(nev).exists(): return nev, "megvan"
    d = json.load(nyit(f"https://api.polyhaven.com/files/{nev}"))
    if "gltf" not in d: return nev, "nincs glTF (" + ",".join(d) + ")"
    g = d["gltf"].get("1k") or d["gltf"][sorted(d["gltf"])[0]]
    g = g["gltf"]
    cel = pathlib.Path(nev); cel.mkdir(exist_ok=True)
    ment(g["url"], cel / pathlib.Path(g["url"]).name)
    for ut, inf in g.get("include", {}).items():
        p = cel / ut; p.parent.mkdir(parents=True, exist_ok=True)
        ment(inf["url"], p)
    return nev, sum(f.stat().st_size for f in cel.rglob("*") if f.is_file())//1024
with cf.ThreadPoolExecutor(8) as ex:
    for nev, kb in ex.map(egy, NEVEK): print(nev, kb, "KB")
