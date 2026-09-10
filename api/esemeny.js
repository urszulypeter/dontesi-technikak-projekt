/* A ToC output-indikátoraihoz gyűjtött események: a játék indítása, a
   végigjátszás és a kiküldött értékelés. Ebből jön ki a részvételi és
   befejezési arány, amit a résztvevők számából egymagában nem lehet kiszámolni.

   A befejezéshez a végpontszám és az öt bizalmi dimenzió is elmentődik — ez
   adja az outcome-oldal egyetlen belülről mérhető indikátorát, az átláthatóság
   és a bevonás megítélését.

   Névtelen: sem név, sem e-mail, sem IP nem kerül ide. */

import { adatbazis, tablat } from "./_kozos.js";

const TIPUSOK = ["inditas", "befejezes", "ertekeles_kuldve"];
const PALYAK  = ["vallalati", "katonai", "politikai"];
const DIMENZIOK = ["kovetkezetesseg", "atlathatosag", "minoseg", "felelosseg", "bevonas"];

/* 0 és 100 közötti egész, vagy semmi. A „vagy semmi" nem hiba: indításnál és
   értékelésküldésnél nincs még pontszám. */
function pontszam(ertek){
  if(ertek === undefined || ertek === null) return null;
  const sz = Number(ertek);
  if(!Number.isInteger(sz) || sz < 0 || sz > 100) return undefined;   /* hibás */
  return sz;
}

export default async function handler(req, res){
  if(req.method !== "POST") return res.status(405).json({ hiba:"Csak POST kérés." });

  const b = req.body || {};
  if(!TIPUSOK.includes(b.tipus)) return res.status(400).json({ hiba:"Ismeretlen eseménytípus." });
  if(!PALYAK.includes(b.palya))  return res.status(400).json({ hiba:"Ismeretlen pálya." });

  const pont = pontszam(b.pont);
  if(pont === undefined) return res.status(400).json({ hiba:"A pontszám 0 és 100 közötti egész szám." });

  const d = b.dimenziok || {};
  const ertekek = {};
  for(const nev of DIMENZIOK){
    const v = pontszam(d[nev]);
    if(v === undefined) return res.status(400).json({ hiba:"A(z) " + nev + " értéke 0 és 100 közötti egész szám." });
    ertekek[nev] = v;
  }

  try{
    const db = adatbazis();
    await tablat(db);
    await db`
      INSERT INTO esemeny (tipus, palya, pont, kovetkezetesseg, atlathatosag, minoseg, felelosseg, bevonas)
      VALUES (${b.tipus}, ${b.palya}, ${pont},
              ${ertekek.kovetkezetesseg}, ${ertekek.atlathatosag}, ${ertekek.minoseg},
              ${ertekek.felelosseg}, ${ertekek.bevonas})`;
    res.status(204).end();
  }catch(h){
    console.error("Az esemény mentése nem sikerült:", h);
    res.status(500).json({ hiba:"Az esemény mentése nem sikerült." });
  }
}
