/* A résztvevő nevének rögzítése. A tíz döntés végén hívódik, függetlenül attól,
   hogy a kérdőívet kitölti-e valaki — így a listán mindenki szerepel, aki
   végigjátszotta.

   A név KÜLÖN táblába megy, a kérdőív válaszaitól elválasztva, és csak dátumot
   kap, nem időbélyeget: két, azonos pillanatban beszúrt sort az időbélyegük
   összekötne. A kérdőív azt ígéri, hogy a válasz névtelen — ezt az
   adatszerkezetnek kell tartania, nem a jó szándéknak. */

import { adatbazis, tablat } from "./_kozos.js";

/* A vezérlőkaraktereket szóközre cseréljük, hogy a lista kiírható maradjon, és
   ne lehessen vele elrontani a megjelenítést. Kódpont szerint vizsgáljuk, mert
   így a forrásban sem kell vezérlőkaraktert leírni. */
function tisztitottNev(nyers){
  let ki = "";
  for(const jel of String(nyers || "")){
    const kod = jel.codePointAt(0);
    ki += (kod < 32 || kod === 127) ? " " : jel;
  }
  return ki.replace(/\s+/g, " ").trim().slice(0, 40);
}

export default async function handler(req, res){
  if(req.method !== "POST") return res.status(405).json({ hiba: "Csak POST kérés." });

  const nev = tisztitottNev(req.body && req.body.nev);
  if(!nev) return res.status(400).json({ hiba: "Üres név." });

  try{
    const db = adatbazis();
    await tablat(db);
    await db`INSERT INTO resztvevo (nev) VALUES (${nev})`;
    res.status(204).end();
  }catch(h){
    console.error("A résztvevő mentése nem sikerült:", h);
    res.status(500).json({ hiba: "A résztvevő mentése nem sikerült." });
  }
}
