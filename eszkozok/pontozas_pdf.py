#!/usr/bin/env python3
"""A pontozási szempontok PDF-be: mi alapján kap egy válasz pontot az öt bizalmi dimenzióban.

Futtatás a projekt gyökeréből:  python3 eszkozok/pontozas_pdf.py
Kimenet: szerkesztes/pontozasi_szempontok.pdf
A statisztikák (eloszlás, tartományok, fogalom-profilok, példák) a kérdésbankból
(adatok/*.json) számolódnak, így a kérdések változása után újragenerálható."""
import collections, json, pathlib, random, statistics
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

GYOKER = pathlib.Path(__file__).resolve().parent.parent
KIMENET = GYOKER / "szerkesztes" / "pontozasi_szempontok.pdf"

# --- betűk: az ő/ű miatt TrueType kell, a beépített Helvetica nem tudja ---
FONT = "/System/Library/Fonts/Supplemental/"
pdfmetrics.registerFont(TTFont("Arial", FONT + "Arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", FONT + "Arial Bold.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Italic", FONT + "Arial Italic.ttf"))
pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold", italic="Arial-Italic")

ZOLD, ARANY, KREM, SZURKE = colors.HexColor("#13291F"), colors.HexColor("#B8933F"), colors.HexColor("#F6F1E7"), colors.HexColor("#5A5A5A")
JO, ROSSZ = colors.HexColor("#E3F1E6"), colors.HexColor("#F8E3E1")
st = {
    "cim": ParagraphStyle("cim", fontName="Arial-Bold", fontSize=20, leading=24, textColor=ZOLD, spaceAfter=4),
    "alcim": ParagraphStyle("alcim", fontName="Arial", fontSize=10.5, leading=14, textColor=SZURKE, spaceAfter=14),
    "h1": ParagraphStyle("h1", fontName="Arial-Bold", fontSize=14, leading=18, textColor=ZOLD, spaceBefore=14, spaceAfter=6),
    "h2": ParagraphStyle("h2", fontName="Arial-Bold", fontSize=11.5, leading=15, textColor=ZOLD, spaceBefore=10, spaceAfter=4),
    "p": ParagraphStyle("p", fontName="Arial", fontSize=9.6, leading=13.4, spaceAfter=6, alignment=TA_LEFT),
    "kicsi": ParagraphStyle("kicsi", fontName="Arial", fontSize=8.4, leading=11, textColor=SZURKE, spaceAfter=4),
    "cella": ParagraphStyle("cella", fontName="Arial", fontSize=8.6, leading=11),
    "cellab": ParagraphStyle("cellab", fontName="Arial-Bold", fontSize=8.6, leading=11),
    "fej": ParagraphStyle("fej", fontName="Arial-Bold", fontSize=8.6, leading=11, textColor=colors.white),
}
P = lambda s, stilus="p": Paragraph(s, st[stilus])

def tabla(sorok, szelessegek, fejlec=True, kiemel=None):
    adat = [[c if not isinstance(c, str) else P(c, "fej" if (fejlec and i == 0) else "cella") for c in sor]
            for i, sor in enumerate(sorok)]
    t = Table(adat, colWidths=[w * mm for w in szelessegek], repeatRows=1 if fejlec else 0)
    stilus = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C9C2B3")),
              ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
              ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    if fejlec: stilus.append(("BACKGROUND", (0, 0), (-1, 0), ZOLD))
    for (r, c, szin) in (kiemel or []): stilus.append(("BACKGROUND", (c, r), (c, r), szin))
    t.setStyle(TableStyle(stilus))
    return t

# --- adatok ---
K = ["kovetkezetesseg", "atlathatosag", "dontesi_minoseg", "felelossegvallalas", "erintettek_bevonasa"]
NEV = ["Következetesség", "Átláthatóság és kommunikáció", "Döntési minőség", "Felelősségvállalás", "Érintettek bevonása"]
ROVID = ["Köv", "Átl", "Dönt", "Fel", "Bev"]
SULY = [0.22, 0.22, 0.20, 0.18, 0.18]
W = dict(zip(K, SULY))
PALYA = {"politikai": "Politikai", "vallalati": "Vállalati", "katonai": "Katonai"}
D = {p: json.loads((GYOKER / "adatok" / f"{p}.json").read_text(encoding="utf-8")) for p in PALYA}
ws = lambda o: sum(W[k] * o["pontok"][k] for k in K)
OPC = [(p, s, o) for p, d in D.items() for s in d["szituaciok"] for o in s["opciok"]]
elojel = lambda v: ("+" if v > 0 else "−" if v < 0 else "") + str(abs(v))
hely = lambda p, s, o: f"{PALYA[p]} {s['id']}{o['jel']}"

def peldak(k, ertek, db=2):
    """Egy-egy példa pályánként, amíg van: hely, fogalom, a válasz eleje."""
    ki, latott = [], set()
    for p, s, o in OPC:
        if o["pontok"][k] == ertek and p not in latott:
            latott.add(p)
            szoveg = o["opcio_leirasa"]
            if len(szoveg) > 150: szoveg = szoveg[:150].rsplit(" ", 1)[0] + " …"
            ki.append(f"<b>{hely(p, s, o)}</b> ({elojel(ertek)}) — <i>{o['fogalom']}</i>: „{szoveg}”")
        if len(ki) >= db: break
    return ki

def szimulal(d, valaszt):
    p = {k: 50 for k in K}
    for s in d["szituaciok"]:
        o = valaszt(s["opciok"])
        for k in K: p[k] = max(0, min(100, p[k] + 3 * o["pontok"][k]))
    return round(sum(W[k] * p[k] for k in K)), p

# --- tartalom ---
t = []
t += [P("Pontozási szempontok", "cim"),
      P("Vezetői Bizalom — döntési szimuláció · Döntési technikák (BCE) · mi alapján kap egy válasz pontot "
        "az öt bizalmi dimenzióban", "alcim")]

t += [P("Röviden", "h1"),
      P(f"A játékban {len(OPC)} válasz van (3 pálya × 10 helyzet × 4 válasz). Mindegyik mind az öt dimenzióban kap egy "
        "egész számot −3 és +3 között. A szám azt méri, <b>mit tesz a döntés azoknak a bizalmával, akik a vezetőt "
        "figyelik</b> — beosztottak, felettesek, érintettek —, nem azt, hogy a döntés „helyes-e”. A döntés mögötti "
        "döntéselméleti fogalmat a válasz utáni kiértékelés nevezi meg; a pont ettől függetlenül, a viselkedés alapján "
        "születik.")]

t += [P("A skála", "h2"),
      tabla([["Pont", "Jelentés", "Mikor adjuk"],
             ["+3", "meghatározó erősítés", "a döntés ennek a dimenziónak a lényegét mutatja, és látható ára van (pl. nyilvánosan vállalt hiba)"],
             ["+2", "egyértelmű erősítés", "a dimenzió viselkedése tisztán megjelenik, kockázatvállalás nélkül"],
             ["+1", "enyhe erősítés", "közvetett vagy részleges: jó irányba mozdít, de nem ez a döntés lényege"],
             ["0", "nem érinti", "a döntésnek nincs érdemi hatása erre a dimenzióra"],
             ["−1", "enyhe sérülés", "elmulasztott lehetőség, kisebb következetlenség, valaki kimarad — de semmi nem rejtett"],
             ["−2", "egyértelmű sérülés", "a dimenzióval szemben megy (pl. fontos érintettet szándékosan megkerül)"],
             ["−3", "aktív rombolás", "eltitkol, nyíltan megszeg egy korábbi szót, másra hárítja a felelősséget"]],
            [14, 38, 118])]

t += [P("Hogyan lesz ebből Bizalomindex", "h2"),
      P("Mind az öt dimenzió 50 pontról indul, és 0 és 100 között mozoghat. Minden válasz pontjait a játék "
        "<b>háromszorozza</b>: egy +2 az adott dimenzióban +6 pontot jelent. A Bizalomindex az öt dimenzió súlyozott átlaga:"),
      tabla([["Dimenzió", "JSON-kulcs", "Súly"]] + [[n, k, f"{s:.2f}".replace(".", ",")] for n, k, s in zip(NEV, K, SULY)],
            [70, 60, 20])]

t += [P("Alapelvek", "h1")]
for i, (cim, szoveg) in enumerate([
    ("Nincs ingyen jó döntés.", "Minden válasznak megvan az ára, és a kiértékelés szövege ki is mondja. A tervezési szabály "
     "szerint ennek a pontokban is meg kell jelennie (legalább egy pozitív és egy negatív érték) — hogy hol nem teljesül, azt az „Egyoldalú válaszok” rész sorolja fel."),
    ("A viselkedést pontozzuk, nem a szerencsét.", "A pont azt tükrözi, ami a döntés pillanatában látható. Ha egy elsietett "
     "döntés véletlenül beválik, a döntési minőség akkor is mínusz."),
    ("A dimenziók függetlenek.", "Egy döntés lehet egyszerre átlátható (+2) és kirekesztő (−2). Mind az öt oszlopot külön kérdezzük meg, nem átlagolunk fejben."),
    ("A vállalt ár a felelősséget emeli.", "Ha a válasz kimondja, mit áldoz fel („a pártod ezt árulásnak fogja tekinteni”), "
     "az a felelősségvállalást növeli: a vezető tudja és vállalja a következményt."),
    ("A következetesség = szótartás és egyforma mérce.", "Nem azt jelenti, hogy a vezető nem változtat irányt. Aki megáll "
     "elemezni, újragondolja a döntését vagy beismeri a hibáját, az nem következetlen (0, legfeljebb −1). Aki eltitkol, kitér "
     "vagy halogat, az nem következetes (0 vagy mínusz). Pluszt az kap, aki betartja a szavát, és mindenkire ugyanazt a szabályt alkalmazza."),
    ("A fogalom nem dönti el a pontot.", "A kiértékelés fogalma azt magyarázza, mi történik a döntésben; a pont azt, hogyan hat "
     "a bizalomra. Ugyanaz a fogalom más helyzetben más pontot kaphat."),
], 1):
    t.append(P(f"<b>{i}. {cim}</b> {szoveg}"))

# --- az öt dimenzió ---
t += [P("Az öt dimenzió", "h1"),
      P("Minden válasznál ugyanezt az öt kérdést tesszük fel. A példák a végleges kérdésbankból valók "
        "(pálya, helyzet sorszáma és a válasz betűjele, zárójelben a kapott pont).")]
DIM = [
    ("„Számíthatnak-e rá, hogy holnap is így dönt?”",
     [("ugyanazt a szabályt mindenkire alkalmazza, kivételt nem tesz", "kivételt tesz egy hangos vagy fontos szereplőnek"),
      ("betartja, amit korábban ígért vagy kimondott", "olyat ígér, amit később nem tud tartani"),
      ("előre kimondott, kiszámítható elvet követ", "halogat, a határidőt vagy a vállalást elcsúsztatja")],
     "Az átgondolt irányváltás (új adat miatt), az elemzésre kért idő vagy a hiba beismerése 0, legfeljebb −1 — "
     "ez nem szószegés. A nyomásra tett kivétel −3."),
    ("„Tudják-e, mi történik és miért?”",
     [("nyilvánosan, időben megosztja a rossz hírt is", "elhallgat, négyszemközt intéz, késleltet"),
      ("a döntés okait is elmondja, nem csak az eredményt", "szépen csomagol, a kedvezőtlen számot hátra teszi"),
      ("a lényeget teszi előre (a romló mutató a jelentés elején)", "nem reagál, kivárja, hogy elcsendesedjen")],
     "Az ideiglenes hallgatás ellenőrzésig −1; a tudatos eltitkolás −3."),
    ("„Tényekre és végiggondolt lehetőségekre épül-e?”",
     [("előbb a problémát és a célokat tisztázza (PrOACT)", "kész megoldást fogad el kérdés nélkül"),
      ("több lehetőséget vet össze, kiszűri a dominált változatokat", "egyetlen szempontot (pénz, gyorsaság) emel ki"),
      ("ellenőrzi a számokat, a saját szemével nézi meg", "torzítás vezeti: halo, sztereotípia, elsőségi hatás")],
     "Az időnyomás alatt hozott „elég jó” döntés (Simon kielégítő döntése) csak −1; ha lett volna idő, −2. "
     "A döntési minőségben nincs −3: a rossz döntés itt „csak” rossz, az aktív rombolás a többi dimenzióban jelenik meg."),
    ("„Vállalja-e a döntést és a következményét?”",
     [("a saját nevével áll ki, akkor is, ha ez kockázat", "másra, bizottságra, szakértőre hárítja a döntést"),
      ("a hibáját kimondja, nem a körülményekre fogja", "a siker az övé, a kudarc a körülményeké (énmegerősítő attribúció)"),
      ("kimondja a választása árát", "elkerüli a döntést, kivár")],
     "A szakértő bevonása nem hárítás, ha a döntés nála marad (0 vagy +1); ha a döntést is átadja, −2 vagy −3."),
    ("„Meghallgatta-e azokat, akiket a döntés érint?”",
     [("a döntés előtt kérdez, nem utána tájékoztat", "egyedül dönt, a kész eredményt közli"),
      ("a gyengébb hangú érintettet is megkeresi", "csak a hangosat vagy a hatalmasat hallgatja meg"),
      ("valódi befolyást ad (pl. saját javaslatot tehetnek)", "látszatbevonás: meghallgat, de a döntés már kész")],
     "A válsághelyzetben hozott egyszemélyes döntés −1, ha utána elmagyarázza; −2…−3, ha nyugodt helyzetben teszi."),
]
for (kerdes, sorok, hatar), nev, k in zip(DIM, NEV, K):
    blokk = [P(f"{nev} — {kerdes}", "h2"),
             tabla([["Pluszt kap", "Mínuszt kap"]] + [list(s) for s in sorok], [85, 85],
                   kiemel=[(r, 0, JO) for r in range(1, 4)] + [(r, 1, ROSSZ) for r in range(1, 4)]),
             Spacer(1, 4), P(f"<b>Határeset:</b> {hatar}")]
    for v in (3, -3) if any(o["pontok"][k] == -3 for _, _, o in OPC) else (3, -2):
        for pl in peldak(k, v): blokk.append(P("• " + pl, "kicsi"))
    t.append(KeepTogether(blokk))

# --- mintázatok ---
profil = collections.defaultdict(list)
for _, _, o in OPC: profil[o["fogalom"]].append([o["pontok"][k] for k in K])
gyakori = sorted(((f, l) for f, l in profil.items() if len(l) >= 3), key=lambda x: -sum(sum(r) for r in x[1]) / len(x[1]))
t += [PageBreak(), P("Gyakori mintázatok", "h1"),
      P(f"A {len(OPC)} válasz {len(profil)} különböző fogalomhoz tartozik. Az alábbiak mindhárom pályán előfordulnak; "
        "a számok a három előfordulás átlagos pontjai. Ebből látszik, melyik dimenzióban szokott nyerni és melyikben fizetni "
        "egy-egy döntéstípus. A sorrend: elöl a bizalmat leginkább építők.")]
fmt = lambda x: ("+" if x > 0 else "−" if x < 0 else "") + f"{abs(x):.1f}".replace(".", ",") if abs(x) >= 0.05 else "0"
sorok = [["Fogalom"] + ROVID]
kiemel = []
for i, (f, l) in enumerate(gyakori, 1):
    atl = [sum(c) / len(c) for c in zip(*l)]
    sorok.append([f] + [fmt(a) for a in atl])
    for j, a in enumerate(atl, 1):
        if a >= 1.5: kiemel.append((i, j, JO))
        elif a <= -1.5: kiemel.append((i, j, ROSSZ))
t.append(tabla(sorok, [80] + [18] * 5, kiemel=kiemel))
t.append(P("Két szabályszerűség: a nyilvánosságot vállaló döntések (napfény teszt, szóvivő, vezető szerep, reflektív gondolkodás) "
           "az átláthatóságban és a felelősségben nyernek, és többnyire a bevonásban fizetnek, mert gyorsan, egyszemélyesen "
           "születnek. A kitérő vagy hárító döntések (döntés elhárítása, problémakerülés, ezredes-hatás, énmegerősítő attribúció) "
           "a felelősségben veszítenek a legtöbbet.", "kicsi"))

# --- végigpontozott helyzet ---
s = D["politikai"]["szituaciok"][0]
INDOK = {
    "A": "Nyilvános és a falvak oldalán áll (átl., bev.), a nevével vállalja (fel.). De számok nélkül ígér (dönt. −2), "
         "és az ígéret valószínűleg nem tartható (köv. −2).",
    "B": "A párt menetrendjét tartja (köv. +1). A kész megoldást kérdés nélkül átveszi (dönt. −2), a falvak nem szólhatnak bele "
         "(bev. −1), az ok nem hangzik el (átl. −1).",
    "C": "A PrOACT első két lépése: probléma és célok előbb (dönt. +3), mindenki látja, miről szól a vita (átl. +2). "
         "Ára a csúszás a vállalt menetrendhez képest (köv. −1).",
    "D": "Saját szemével gyűjt adatot (dönt. +2), személyesen áll a falvak elé (fel. +2). A bizottság nem tudja, mire vár "
         "(átl. −1); a menetrendet nem ígérte senkinek, ezért a következetesség 0.",
}
sorok = [["Válasz"] + ROVID + ["Indoklás"]]
kiemel = []
for i, o in enumerate(s["opciok"], 1):
    sz = o["opcio_leirasa"]; sz = sz[:110].rsplit(" ", 1)[0] + " …" if len(sz) > 110 else sz
    sorok.append([f"<b>{o['jel']}</b> — {sz}"] + [elojel(o["pontok"][k]) for k in K] + [INDOK[o["jel"]]])
    for j, k in enumerate(K, 1):
        v = o["pontok"][k]
        if v > 0: kiemel.append((i, j, JO))
        elif v < 0: kiemel.append((i, j, ROSSZ))
hatas = " · ".join(f"{o['jel']}: {fmt(3 * ws(o))}" for o in s["opciok"])
legjobb = max(s["opciok"], key=ws)
t += [PageBreak(), P("Egy helyzet végigpontozva", "h1"),
      P(f"<b>Politikai 1. — {s['cim']}.</b> {s['szituacio_leirasa']}"),
      tabla(sorok, [50] + [10.5] * 5 + [71.5], kiemel=kiemel), Spacer(1, 4),
      P(f"Súlyozott hatás a Bizalomindexre (×3): {hatas}. A {legjobb['jel']} a legjobb, de nem ingyen: a "
        "következetességben fizet. A leggyengébbnek is van érve: gyors, és a párt elvárását követi.")]

# --- kalibráció ---
t += [P("Kalibráció és ellenőrzés", "h1"),
      P("A pontozás akkor jó, ha minden dimenzió megnyerhető és elveszíthető, a legjobb út sem viszi 100 közelébe a "
        "Bizalomindexet, és a véletlenszerű játék a skála közepén marad.")]
sorok = [["Pálya", "Mindig a legjobb válasz", "Mindig a legrosszabb", "Véletlen játék: átlag (5–95%)"]]
for p, d in D.items():
    b, bd = szimulal(d, lambda os: max(os, key=ws)); w, wd = szimulal(d, lambda os: min(os, key=ws))
    random.seed(1); r = sorted(szimulal(d, lambda os: random.choice(os))[0] for _ in range(4000))
    sorok.append([f"{PALYA[p]} vezető", f"{b}  (köv. {bd['kovetkezetesseg']})", f"{w}  (köv. {wd['kovetkezetesseg']})",
                  f"{statistics.mean(r):.1f}".replace(".", ",") + f"  ({r[200]}–{r[3800]})"])
t += [tabla(sorok, [38, 42, 42, 48]),
      P("A zárójeles következetesség mutatja, hogy a végleges pontozásban ez a dimenzió már jó irányba mutat: a legjobb úton "
        "magasabb, mint a legrosszabbon. (Egy korábbi változatban fordítva volt: az eltitkoló és kitérő válaszok kaptak érte pluszt.)", "kicsi")]

eloszl = {k: collections.Counter(o["pontok"][k] for _, _, o in OPC) for k in K}
sorok = [["Dimenzió", "−3", "−2", "−1", "0", "+1", "+2", "+3", "pozitív", "negatív"]]
for n, k in zip(NEV, K):
    c = eloszl[k]
    sorok.append([n] + [str(c.get(v, 0)) for v in range(-3, 4)] +
                 [str(sum(c[v] for v in c if v > 0)), str(sum(c[v] for v in c if v < 0))])
t += [P("A pontok eloszlása", "h2"), tabla(sorok, [52] + [11] * 7 + [16, 16])]

egyoldalu = [(p, s, o) for p, s, o in OPC if not any(v < 0 for v in o["pontok"].values()) or not any(v > 0 for v in o["pontok"].values())]
csak_plusz = [hely(p, s, o) for p, s, o in egyoldalu if not any(v < 0 for v in o["pontok"].values())]
csak_minusz = [hely(p, s, o) for p, s, o in egyoldalu if not any(v > 0 for v in o["pontok"].values())]
t += [P("Egyoldalú válaszok", "h2"),
      P(f"A „nincs ingyen jó döntés” elv szerint minden válasznak kellene pozitív és negatív pontot is kapnia. A végleges "
        f"kérdésbankban {len(egyoldalu)} válasznál ez nem teljesül — jellemzően azért, mert a következetesség átpontozásakor "
        "épp az ellentétes előjelű érték lett 0. A kiértékelés szövege ezeknél is megnevezi az árat, csak a pontokban nem jelenik meg. "
        "Ha a szabályt szigorúan akarjuk tartani, ezeknél egy-egy ±1 kell abba a dimenzióba, ahol a szöveg az árat megnevezi."),
      P(f"<b>Csak pozitív ({len(csak_plusz)}):</b> {', '.join(csak_plusz)}.", "kicsi"),
      P(f"<b>Csak negatív ({len(csak_minusz)}):</b> {', '.join(csak_minusz)}.", "kicsi")]

t += [P("Automatikus ellenőrzés", "h2"),
      P("Az <font name='Arial-Bold'>eszkozok/ellenorzes.py</font> minden módosítás után megnézi: tíz helyzet és A–D válasz "
        "pályánként; a pontok egészek −3 és +3 között; minden válasznak van pozitív és negatív pontja; a helyzetekben és "
        "válaszokban nincs szakszó; egy helyzeten belül a válaszok súlyozott hatása legalább 0,8-del szór; a legjobb válasz "
        "betűjele egy pályán legfeljebb négyszer ugyanaz. A szerkeszthető Excelben (szerkesztes/kerdesek.xlsx) az "
        "„Ellenőrzés” oszlop ugyanezt mutatja soronként.")]

def lap(c, doc):
    c.saveState(); c.setFont("Arial", 7.5); c.setFillColor(SZURKE)
    c.drawString(18 * mm, 10 * mm, "Vezetői Bizalom · Pontozási szempontok")
    c.drawRightString(A4[0] - 18 * mm, 10 * mm, str(doc.page))
    c.setStrokeColor(ARANY); c.setLineWidth(0.6); c.line(18 * mm, A4[1] - 12 * mm, A4[0] - 18 * mm, A4[1] - 12 * mm)
    c.restoreState()

KIMENET.parent.mkdir(exist_ok=True)
SimpleDocTemplate(str(KIMENET), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=18 * mm, bottomMargin=16 * mm,
                  title="Pontozási szempontok — Vezetői Bizalom", author="Vezetői Bizalom").build(t, onFirstPage=lap, onLaterPages=lap)
print("Kész:", KIMENET.relative_to(GYOKER))
