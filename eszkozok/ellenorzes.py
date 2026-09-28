#!/usr/bin/env python3
"""A kérdésadatbázis (adatok/*.json) szabályainak ellenőrzése.

Futtatás a projekt gyökeréből:  python3 eszkozok/ellenorzes.py
Hibánál nem nullával lép ki, így CI-ben is használható."""
import json, sys, re, collections, pathlib

GYOKER = pathlib.Path(__file__).resolve().parent.parent
FAJLOK = ["politikai", "vallalati", "katonai"]
PONTKULCSOK = ["kovetkezetesseg", "atlathatosag", "dontesi_minoseg", "felelossegvallalas", "erintettek_bevonasa"]
SULY = dict(zip(PONTKULCSOK, [0.22, 0.22, 0.20, 0.18, 0.18]))   # ugyanaz, mint a játékban

# A helyzetleírásban és a válaszokban tilos a szakzsargon: a tesztet laikusnak is ki kell tudnia tölteni.
TILTOTT = ["proact", "simon", "mintzberg", "halo", "attribúci", "snowden", "cynefin", "boone",
           "érintett-térkép", "érintetterőtér", "stakeholder", "dominanci", "racionalit", "strukturált",
           "torzítás", "heurisztik", "trade-off", "alternatív", "kritérium", "szcenári", "inkrementál",
           "pygmalion", "sztereotíp", "diszkontál", "reflektív", "autokratikus", "konzultatív", "drucker",
           "önbeteljesítő", "ezredes-hatás", "prioritási mátrix", "szelektív"]

hibak = []
def hiba(hol, mi): hibak.append(f"{hol}: {mi}")

for nev in FAJLOK:
    ut = GYOKER / "adatok" / f"{nev}.json"
    try:
        d = json.loads(ut.read_text(encoding="utf-8"))
    except Exception as e:
        hiba(nev, f"nem érvényes JSON ({e})"); continue
    for k in ["szerep", "tortenet_szinopszisa", "szituaciok"]:
        if k not in d: hiba(nev, f"hiányzó kulcs: {k}")
    sz = d.get("szituaciok", [])
    if len(sz) != 10: hiba(nev, f"{len(sz)} szituáció van, 10 kell")
    fogalmak = collections.Counter()
    legjobb, legrosszabb = collections.Counter(), collections.Counter()
    for i, s in enumerate(sz, 1):
        hol = f"{nev} #{i}"
        if s.get("id") != i: hiba(hol, f"az id {s.get('id')}, {i} kellene")
        for k in ["cim", "szituacio_leirasa", "opciok"]:
            if not s.get(k): hiba(hol, f"hiányzó mező: {k}")
        laikus = (s.get("szituacio_leirasa", "") + " " + " ".join(o.get("opcio_leirasa", "") for o in s.get("opciok", []))).lower()
        for t in TILTOTT:
            if t in laikus: hiba(hol, f"szakszó a laikus szövegben: „{t}”")
        ops = s.get("opciok", [])
        if [o.get("jel") for o in ops] != ["A", "B", "C", "D"]: hiba(hol, "a jelek nem A, B, C, D sorrendűek")
        osszegek = []
        for o in ops:
            oh = f"{hol}{o.get('jel')}"
            for k in ["opcio_leirasa", "fogalom", "kiertekeles", "pontok"]:
                if not o.get(k): hiba(oh, f"hiányzó mező: {k}")
            p = o.get("pontok", {})
            if sorted(p) != sorted(PONTKULCSOK): hiba(oh, f"a pontkulcsok hibásak: {sorted(p)}")
            for k, v in p.items():
                if not isinstance(v, int) or isinstance(v, bool) or not -3 <= v <= 3:
                    hiba(oh, f"{k} = {v!r}: egész szám kell −3 és 3 között")
            ertekek = list(p.values())
            if not any(v > 0 for v in ertekek): hiba(oh, "nincs pozitív hatása — minden opciónak kell racionális érv")
            if not any(v < 0 for v in ertekek): hiba(oh, "nincs negatív hatása — minden opciónak áldozattal kell járnia")
            fogalmak[o.get("fogalom", "")] += 1
            osszegek.append(sum(SULY[k] * p.get(k, 0) for k in PONTKULCSOK))
        if osszegek:
            legjobb[max(range(len(osszegek)), key=lambda j: osszegek[j])] += 1
            legrosszabb[min(range(len(osszegek)), key=lambda j: osszegek[j])] += 1
            if max(osszegek) - min(osszegek) < 0.8: hiba(hol, "az opciók súlyozott összege túl közel van egymáshoz")
    ismetlodo = {f: n for f, n in fogalmak.items() if n > 1}
    print(f"{nev:10s} {len(sz)} szituáció, {sum(fogalmak.values())} opció, {len(fogalmak)} különböző fogalom"
          + (f" | ismétlődik: {ismetlodo}" if ismetlodo else ""))
    print(f"{'':10s} a legjobb opció betűje: " + ", ".join(f"{'ABCD'[k]}×{v}" for k, v in sorted(legjobb.items())))
    # A felhasználó kifejezetten kérte, hogy ne legyen mindig ugyanaz a betű a jó válasz.
    for k, v in legjobb.items():
        if v > 4: hiba(nev, f"a legjobb válasz {v} szituációban is a(z) {'ABCD'[k]} betű — túl kiszámítható")

if hibak:
    print("\nHIBÁK:"); [print("  -", h) for h in hibak]; sys.exit(1)
print("\nMinden szabály teljesül.")
