/* A kérdőív beküldése. Nyilvános végpont, ezért minden mező ellenőrzött, és
   csak az a hat érték kerül be, amiből a kimutatás készül. Nevet, e-mail-címet
   és IP-t szándékosan nem tárolunk: a visszajelzés névtelen. */

import { adatbazis, tablat } from "./_kozos.js";

const PALYAK   = ["vallalati", "katonai", "politikai"];
const VALASZOK = ["A", "B", "C"];

export default async function handler(req, res){
  if(req.method !== "POST") return res.status(405).json({ hiba:"Csak POST kérés." });

  const b = req.body || {};
  const ertekeles = Number(b.ertekeles), pont = Number(b.pont);

  if(!Number.isInteger(ertekeles) || ertekeles < 1 || ertekeles > 5)
    return res.status(400).json({ hiba:"Az értékelés 1 és 5 közötti egész szám." });
  if(!VALASZOK.includes(b.k1) || !VALASZOK.includes(b.k2))
    return res.status(400).json({ hiba:"A válasz csak A, B vagy C lehet." });
  if(!PALYAK.includes(b.palya))
    return res.status(400).json({ hiba:"Ismeretlen pálya." });
  if(!Number.isInteger(pont) || pont < 0 || pont > 100)
    return res.status(400).json({ hiba:"A pontszám 0 és 100 közötti egész szám." });

  try{
    const db = adatbazis();
    await tablat(db);
    await db`INSERT INTO visszajelzes (ertekeles, k1, k2, palya, pont)
             VALUES (${ertekeles}, ${b.k1}, ${b.k2}, ${b.palya}, ${pont})`;
    res.status(204).end();
  }catch(h){
    console.error("A visszajelzés mentése nem sikerült:", h);
    res.status(500).json({ hiba:"A visszajelzés mentése nem sikerült." });
  }
}
