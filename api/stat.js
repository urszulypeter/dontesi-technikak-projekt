/* A kimutatás adatai. Csak belépve érhető el, és csak összesítést ad vissza:
   egyedi kitöltés soha nem hagyja el a kiszolgálót. */

import { adatbazis, tablat, belepett } from "./_kozos.js";

export default async function handler(req, res){
  if(req.method !== "GET") return res.status(405).json({ hiba:"Csak GET kérés." });
  if(!belepett(req)) return res.status(401).json({ hiba:"Nincs belépve." });

  try{
    const db = adatbazis();
    await tablat(db);

    const [ossz, ertekelesek, k1, k2, palyak, napok, resztvevok, esemenyek, dimenziok] = await Promise.all([
      /* A Postgres az idézőjel nélküli aliast kisbetűsíti, ezért itt minden
         név kisbetűs és aláhúzásos — így a JS-oldal is azt látja, ami van. */
      db`SELECT count(*)::int                     AS db,
                coalesce(avg(ertekeles), 0)::float AS atlag,
                coalesce(avg(pont), 0)::float      AS atlag_pont
           FROM visszajelzes`,

      db`SELECT ertekeles AS fok, count(*)::int AS db
           FROM visszajelzes GROUP BY fok ORDER BY fok`,

      db`SELECT k1 AS valasz, count(*)::int AS db
           FROM visszajelzes GROUP BY valasz ORDER BY valasz`,

      db`SELECT k2 AS valasz, count(*)::int AS db
           FROM visszajelzes GROUP BY valasz ORDER BY valasz`,

      db`SELECT palya, count(*)::int AS db,
                avg(ertekeles)::float AS atlag,
                avg(pont)::float      AS atlag_pont
           FROM visszajelzes GROUP BY palya ORDER BY db DESC`,

      /* A napi bontás budapesti idő szerint készül, különben a késő esti
         kitöltések a következő napra csúsznának át. */
      db`SELECT to_char(date_trunc('day', letrehozva AT TIME ZONE 'Europe/Budapest'), 'YYYY-MM-DD') AS nap,
                count(*)::int AS db
           FROM visszajelzes GROUP BY nap ORDER BY nap`,

      /* A résztvevők névsora. Azonos néven többször is végig lehet játszani,
         ezért névre csoportosítunk: a listán egyszer szerepel, a `db` mondja
         meg, hányszor játszott. A rendezés kisbetűsítve történik, különben az
         ékezetes nevek a lista végére csúsznának. */
      db`SELECT nev, count(*)::int AS db, min(nap)::text AS elso
           FROM resztvevo
          GROUP BY nev
          ORDER BY lower(nev)
          LIMIT 1000`,

      /* ToC output-indikátorok: ebből jön a részvételi és befejezési arány */
      db`SELECT tipus, count(*)::int AS db FROM esemeny GROUP BY tipus`,

      /* Az öt bizalmi dimenzió átlaga a végigjátszók körében. Ez a ToC
         outcome-oldalának egyetlen belülről mérhető indikátora: az
         átláthatóság és a bevonás megítélése. */
      db`SELECT coalesce(avg(kovetkezetesseg),0)::float AS kovetkezetesseg,
                coalesce(avg(atlathatosag),0)::float    AS atlathatosag,
                coalesce(avg(minoseg),0)::float         AS minoseg,
                coalesce(avg(felelosseg),0)::float      AS felelosseg,
                coalesce(avg(bevonas),0)::float         AS bevonas,
                count(*)::int                           AS db
           FROM esemeny WHERE tipus = 'befejezes'`
    ]);

    const esemenySzam = t => (esemenyek.find(e => e.tipus === t) || { db:0 }).db;
    const inditasok   = esemenySzam("inditas");
    const befejezesek = esemenySzam("befejezes");

    res.setHeader("Cache-Control", "no-store");
    res.status(200).json({
      osszes:    ossz[0].db,
      atlag:     ossz[0].atlag,
      atlagPont: ossz[0].atlag_pont,
      /* hányan játszottak végig — ez független a kérdőív kitöltésétől */
      jatszottak: resztvevok.reduce((s, r) => s + r.db, 0),
      /* ToC output-indikátorok. A befejezési arány csak akkor értelmes, ha
         volt indítás — nulla osztóval null megy vissza, és a felület kiírja,
         hogy még nincs mit mutatni. */
      toc: {
        inditasok,
        befejezesek,
        kikuldottErtekelesek: esemenySzam("ertekeles_kuldve"),
        befejezesiArany: inditasok ? befejezesek / inditasok : null,
        dimenziok: dimenziok[0]
      },
      ertekelesek, k1, k2, palyak, napok, resztvevok
    });
  }catch(h){
    console.error("A kimutatás lekérése nem sikerült:", h);
    res.status(500).json({ hiba:"A kimutatás lekérése nem sikerült." });
  }
}
