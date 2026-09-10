# Vezetői Bizalom — döntési szimuláció

Interaktív, egyfájlos webalkalmazás a Budapesti Corvinus Egyetem **Döntési technikák**
kurzusához. A játékos vezetőként tíz hétköznapi helyzetben dönt, a válaszai pedig egy
öt dimenzióból álló **Bizalomindexet** mozgatnak. A végén személyre szabott
kiértékelést kap, amit e-mailben is elküldhet.

**Élő verzió:** https://vezetoi-bizalom.vercel.app

---

## Mit tud

- **Fotórealisztikus nyitókép.** A kezdőoldal háttere nem stilizált díszlet:
  fotografált HDRI-környezetfény, beszkennelt PBR-anyagok, fotogrammetriás
  bútorok és három 3D-szkennelt alak, valódi napfénnyel, hosszú ablakárnyékokkal
  és filmes utómunkával (AgX színkezelés, ragyogás, vignetta, filmszemcse,
  objektív-színbontás). A források és licencek: `assets/LICENC.md`.
- **Három pálya** ugyanazzal a tíz döntési ívvel, más környezetben:
  vállalati középvezető, katonai ezredes, politikai középvezető.
- **3D jelenetek** Three.js-szel. Pályánként tíz díszlet, közöttük valódi
  kameramozgással; a kamera átér a helyszínre, a kép megáll, és feljön a döntés.
- **Telltale-stílusú döntési réteg**: a jelenetre vetített kérdés és válaszok.
- **Bizalomindex** felül középen. Válasz után megnő, kiírja a változást, majd
  visszahúzódik.
- **Véletlen válaszsorrend** minden jelenetnél, így nem tanulható meg, hogy „az első a jó”.
- **Kiértékelés**: végső pontszám, előnyök és hátrányok, radardiagram, döntési
  mintázat, három konkrét ajánlás, döntési napló.
- **Eredményküldés** EmailJS-szel; tartalék a `mailto:`, a vágólap és a letöltés.

## A bizalom öt dimenziója

| Dimenzió | Súly | Mit mér |
|---|---|---|
| Következetesség | 0,22 | betartja-e, amit ígért; kiszámítható-e |
| Átláthatóság és kommunikáció | 0,22 | megosztja-e a döntés okait, időben tájékoztat-e |
| Döntési minőség | 0,20 | strukturáltan, tények alapján dönt-e |
| Felelősségvállalás | 0,18 | vállalja-e a hibát, tanul-e belőle |
| Érintettek bevonása | 0,18 | bevonja-e azokat, akiket a döntés érint |

Mindegyik 50 pontról indul, 0 és 100 között mozog. A Bizalomindex ezek súlyozott átlaga.

## Pontozási rendszer

Minden válasz 3–5 dimenziót mozdít. Négy sáv, mindhárom pályán azonos nagyságrend:

| Sáv | Összeg |
|---|---|
| mintaértékű döntés | +22 … +30 |
| részben jó döntés | +1 … +14 |
| gyenge döntés | −7 … −16 |
| súlyosan romboló döntés | −18 … −28 |

Ellenőrzött végeredmény: a legjobb úton 90–91 pont, a legrosszabbon 10–15 pont
mindhárom pályán.

## A tíz döntési ív

A helyzetek hétköznapiak, a mögöttük álló döntéstechnikát a válasz utáni
visszajelzés nevezi meg.

1. A feladat értelmezése — CATWOE-lista, Ockham borotvája
2. Kit érint a döntés — érintett-térkép, érintetterőtér
3. A valódi ok megkeresése — halszálka (Ishikawa) diagram, Pareto-elemzés
4. Bevonás vagy tájékoztatás — Arnstein részvételi létra, állampolgári tanács
5. Minek higgyünk — több nézőpont, elérhetőségi torzítás, hárítás, horgonyzás
6. Honnan jönnek a javaslatok — névleges csoport módszer, brainstorming, szinektika
7. Felkészülés a hibára — hibafa, forgatókönyv-elemzés
8. Mi alapján válassz — Even Swap, haszonérték-elemzés
9. Amit senki nem lát — etikai ellenőrző lista, napfény teszt, gátló racionalizálások
10. Visszatekintés — következtetési létra, reflektív gondolkodás, baloldali oszlop

## Fájlszerkezet

    index.html            a teljes alkalmazás: HTML, CSS, JS, 3D jelenetek, kérdésadatok
    assets/hdri/          a nyitókép környezetfénye (.hdr)
    assets/felulet/       padló- és falanyag PBR-térképei (.webp)
    assets/modell/        a nyitókép modelljei (.glb, meshopt-tömörítve)
    assets/LICENC.md      minden eszköz forrása, szerzője és licence
    README.md             ez a leírás

Nincs build lépés. Külső függőség: Three.js `0.180.0` (3D, importmap-en át
CDN-ről), Google Fonts (tipográfia), EmailJS (eredményküldés).

A kód ES-modul (`<script type="module">`), ezért a Three.js kiegészítői
(`GLTFLoader`, `RGBELoader`, utómunka-passzok) importtal érhetők el. Az
importmap az `index.html` tetején van; a verzió egy helyen cserélhető.

## A nyitókép eszközei

A nyitókép minden eleme szabadon felhasználható forrásból származik, és a
repóban optimalizált formában van benne — így nem függ egy külső CDN
elérhetőségétől. Összesen ~4,8 MB, de **nem egyszerre**: két ütemben tölt be
(lásd lentebb), és a szöveg mindvégig olvasható.

| Mi | Honnan | Licenc |
|---|---|---|
| Környezetfény (Dresden Square HDRI, 768×384) | Poly Haven | CC0 |
| Padló- és falanyag | Poly Haven | CC0 |
| Fotelek, kanapé, asztal, növények, lámpa, sakk-készlet, váza, óra, mellszobor, konzol | Poly Haven | CC0 |
| A két alak („Fitg013”, LGA-NA) | Sketchfab / Objaverse | **CC BY 4.0** |

A CC-BY névattribúció a nyitóoldal láblécében és az `assets/LICENC.md`-ben is
szerepel — ez a licenc feltétele, ne töröld.

Az eszközök feldolgozása `@gltf-transform`-mal és `sharp`-pal történt:
textúrák WebP-be, geometria `EXT_meshopt_compression`-nel, a szkennelt alakok
1 499 992 → 2 × 32 000, illetve 916 867 → 53 916 háromszögre egyszerűsítve.

**Amit tudatosan nem használunk:** a Renderpeople és a Mixamo ingyenes
karaktereit. Mindkettő licence tiltja, hogy a modellfájl önálló fájlként
letölthető legyen — egy WebGL-oldalon pontosan az.

## A nyitókép teljesítménye

A nyitókép háttér: nem foghatja el a gépet a szöveg és a görgetés elől. A
végleges költség egy integrált GPU-n **12 ms / képkocka**, 30 kép/mp-re
korlátozva — tehát a GPU nagyjából harmadát használja. Az első működő változat
ugyanezen a gépen 120 ms / képkocka volt (8 kép/mp); ami a különbséget adta,
mérési sorrendben:

| Mit | Miért került sokba | Nyereség |
|---|---|---|
| Egyetlen `transmission`-os anyag (a falióra üvegje) | Ha a jelenetben bárminek van átvilágítása, a three **az egész jelenetet még egyszer** lerajzolja egy külön pufferbe | 480 000 → 240 000 háromszög/kép |
| GTAO (takarási árnyalás) | Saját mélységképéhez szintén újrarajzolja a jelenetet | −56 ms |
| Üveg `MeshPhysicalMaterial`, kétoldalas, átlátszó | A kép felét lefedi, tehát minden mögötte lévő képpontot újra árnyékol — pedig az üvegen csak tükröződés látszik | −31 ms |
| Mélységélesség (bokeh) | Ugyancsak külön mélységrajzolás | −11 ms |
| Többmintás élsimítás (MSAA) | Integrált GPU-n drágább, mint amennyit ér: MSAA nélkül 2,9 Mpixel olcsóbb, mint kétmintásan 1,4 Mpixel | −8 ms |
| Hat pontfény | Minden fény minden képpont árnyékolását drágítja | −13 ms |
| Vak képpontarány (`devicePixelRatio` × 1,9) | Retina-kijelzőn 5,2 millió képpont; helyette képpont**keret** van | ~2× |

Ezenkívül: az árnyéktérkép egyszer rajzolódik meg (a nap és a berendezés áll),
és ha a nyitókép kigörgetett a képernyőről, egyáltalán nem renderelünk.

Ha egy gépen mégis akadna, a `heroMinoseg()` három fokozata (`alap`, `kozep`,
`magas`) egy helyen állítja a képpontkeretet, az árnyéktérképet és a porszemek
számát.

## A nyitókép betöltése

A 3D nem várakoztathatja meg a lapot. Három dolgon múlik, mikor jelenik meg:

**1. Ne kelljen sorban állni.** Az importtérkép, a `modulepreload` és a
`preload` sorok a `<head>`-ben vannak: a böngésző így már a HTML olvasása
közben elkezdi tölteni a Three.js modulokat *és* az első ütem eszközeit.
Enélkül a modul lefutásáig — mérve 1,4 másodpercig — egyetlen eszköz sem
indult el. (Az importtérképnek meg kell előznie a `modulepreload` sorokat,
különben a kiegészítők `three` hivatkozása feloldhatatlan.)

**2. Két ütem.** Az első ütem csak az, ami nélkül nincs mit mutatni: a
környezetfény és a tér felületei — 1,3 MB. Ebből már valódi, helyesen
megvilágított helyiség lesz, és azonnal látszik. A berendezés és az alakok
(3,5 MB) csak ezután indulnak, hogy ne vegyék el a sávszélességet az elsőtől,
és megérkezéskor lágyan beúsznak, nem pattannak be.

**3. Kevesebb bájt.** A HDRI 1024×512-ről 768×384-re ment (1489 → 829 kB): az
ablakon kilátszó városkép ekkora méretben megkülönböztethetetlen, mert a
szórt üvegen át amúgy is lágy. A padló domborzat- és durvaságtérképét pedig
egyszerűen töröltük — az anyaga már nem használta őket, mégis letöltődtek.

**4. Ne akadjon el a lap.** A modellek értelmezése, a shaderfordítás és a
textúrafeltöltés mind főszálas munka. Egyben ez másodperc körüli akadás, amit
a görgetés is megérez; ezért a tizenkét modell egyenként, képkockánként
dolgozódik fel (`heroFelkeszit()` egy képkockányi idő után átengedi a szót).
A leghosszabb akadás így 1101 ms-ról 424 ms-ra csökkent, a nyitókép
megjelenése utáni képkockák pedig egyenletesen 17 ms-osak.

Mért idő az első képig:

| Kapcsolat | Előtte | Utána |
|---|---|---|
| helyi kiszolgáló | 2,3 mp | 1,0 mp |
| 9 Mbit/s | 6,8 mp | 2,4 mp |
| 4 Mbit/s | 14,2 mp | 4,8 mp |

## Helyi futtatás

A CDN-ek miatt érdemes kiszolgálón megnyitni, nem duplakattintással:

```bash
python3 -m http.server 8765
```

Ezután: http://127.0.0.1:8765/index.html

## E-mail beállítása

Az `index.html` tetején négy konstans van. Az elsők hármat az
[EmailJS](https://www.emailjs.com) fiókodból kell kitölteni:

```js
const EMAILJS_PUBLIC_KEY   = "IDE_JON_A_PUBLIC_KEY";
const EMAILJS_SERVICE_ID   = "IDE_JON_A_SERVICE_ID";
const EMAILJS_TEMPLATE_ID  = "IDE_JON_A_TEMPLATE_ID";
const EREDMENY_MASOLAT_CIM = "";   // ide megy másolat minden eredményről
```

A sablonban ezek a változók használhatók: `{{to_email}}`, `{{player_name}}`,
`{{report}}`, `{{score}}`, `{{level}}`, `{{mode}}`. Kitöltetlen kulcsokkal a
küldés gomb nem hibázik, hanem felajánlja a levelezőprogramos tartalékot.

## Kérdések szerkesztése

A kérdések a `STORIK` objektumban vannak, pályánként tíz szituáció, mindegyikben
négy válasszal. Egy válasz mezői:

```js
{ szoveg:"…",              // amit a játékos lát, hétköznapi nyelven
  technika:"…",            // a technika neve; a visszajelzésben és az elemzésben jelenik meg
  stilus:"strukturalt",    // gyors | strukturalt | bevono | ovatos | delegalo
  hatas:{kov:2, atl:5, min:11, fel:0, bev:7},
  vissza:"…",              // következmény a válasz után
  naplo:"…" }              // rövid bejegyzés a döntési naplóba
```

## Közzététel

A Vercelre a projekt gyökeréből:

```bash
vercel deploy --prod --yes
```

## Forrás

A szituációk a kurzus tantárgyi tájékoztatójára és a *Döntési technikák* jegyzet
fejezeteire épülnek. A jegyzet szerzői jogvédelem alatt áll, ezért a forrásanyagok
nincsenek a repóban.

A történetek fiktívek. A kiértékelés fejlesztő célú, nem minősítés.
