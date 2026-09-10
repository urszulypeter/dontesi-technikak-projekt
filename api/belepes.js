/* Admin belépés és kilépés. A jegy HttpOnly sütibe kerül: a lap saját
   szkriptje nem fér hozzá, tehát egy esetleges beszúrt szkript sem tudja
   ellopni. */

import { jelszoEgyezik, jegyKeszit, sutitBeallit, belepett } from "./_kozos.js";

export default async function handler(req, res){
  /* a kimutatás ebből tudja meg, kell-e belépteti a látogatót */
  if(req.method === "GET") return res.status(200).json({ belepve: belepett(req) });

  if(req.method === "DELETE"){
    sutitBeallit(req, res, "", 0);
    return res.status(204).end();
  }

  if(req.method !== "POST") return res.status(405).json({ hiba:"Csak POST, GET vagy DELETE." });

  try{
    if(!jelszoEgyezik(req.body && req.body.jelszo)){
      /* A késleltetés a végigpróbálást drágítja: száz jelszó kipróbálása így
         perc nagyságrend, nem másodperc. */
      await new Promise(r => setTimeout(r, 900));
      return res.status(401).json({ hiba:"Hibás jelszó." });
    }
    sutitBeallit(req, res, jegyKeszit(), 8 * 60 * 60);
    res.status(204).end();
  }catch(h){
    console.error("A belépés nem sikerült:", h);
    res.status(500).json({ hiba:"A belépés nincs beállítva a kiszolgálón." });
  }
}
