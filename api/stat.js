/* A kimutatás adatai. Csak belépve érhető el, és csak összesítést ad vissza:
   egyedi kitöltés soha nem hagyja el a kiszolgálót. */

import { adatbazis, tablat, belepett } from "./_kozos.js";

export default async function handler(req, res){
  if(req.method !== "GET") return res.status(405).json({ hiba:"Csak GET kérés." });
  if(!belepett(req)) return res.status(401).json({ hiba:"Nincs belépve." });

  try{
    const db = adatbazis();
    await tablat(db);

    const [ossz, ertekelesek, k1, k2, palyak, napok] = await Promise.all([
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
           FROM visszajelzes GROUP BY nap ORDER BY nap`
    ]);

    res.setHeader("Cache-Control", "no-store");
    res.status(200).json({
      osszes:    ossz[0].db,
      atlag:     ossz[0].atlag,
      atlagPont: ossz[0].atlag_pont,
      ertekelesek, k1, k2, palyak, napok
    });
  }catch(h){
    console.error("A kimutatás lekérése nem sikerült:", h);
    res.status(500).json({ hiba:"A kimutatás lekérése nem sikerült." });
  }
}
