# Vezetői Bizalom — döntési szimuláció

Interaktív, egyfájlos webalkalmazás a Budapesti Corvinus Egyetem **Döntési technikák**
kurzusához. A játékos vezetőként tíz hétköznapi helyzetben dönt, a válaszai pedig egy
öt dimenzióból álló **Bizalomindexet** mozgatnak. A végén személyre szabott
kiértékelést kap, amit e-mailben is elküldhet.

**Élő verzió:** https://vezetoi-bizalom.vercel.app

---

## Mit tud

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

    index.html    a teljes alkalmazás: HTML, CSS, JS, 3D jelenetek, kérdésadatok
    README.md     ez a leírás

Egyetlen fájl, nincs build lépés. Külső függőség: Three.js (3D), Google Fonts
(tipográfia), EmailJS (eredményküldés) — mind CDN-ről.

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
