/* ============================================================================
   KÖZÖS RÉSZEK A KISZOLGÁLÓFÜGGVÉNYEKHEZ
   ----------------------------------------------------------------------------
   Adatbázis, belépőjegy és sütikezelés. Az aláhúzással kezdődő fájlokat a
   Vercel nem teszi ki végpontként, tehát ez csak belülről érhető el.
   ========================================================================== */

import { neon } from "@neondatabase/serverless";
import { createHash, createHmac, timingSafeEqual } from "node:crypto";

/* --- adatbázis ------------------------------------------------------------ */

export function adatbazis(){
  const url = process.env.DATABASE_URL;
  if(!url) throw new Error("Hiányzik a DATABASE_URL környezeti változó.");
  return neon(url);
}

/* A táblát az első kérésnél hozzuk létre, nem külön migrációs lépésben: így a
   telepítés továbbra is egyetlen `vercel deploy`, és egy újonnan bekötött
   adatbázis magától használhatóvá válik. A jelző csak a futó példányra
   vonatkozik — a CREATE ... IF NOT EXISTS ismételve is ártalmatlan. */
let tablaKesz = false;
export async function tablat(db){
  if(tablaKesz) return;
  await db`
    CREATE TABLE IF NOT EXISTS visszajelzes (
      id          bigserial   PRIMARY KEY,
      ertekeles   smallint    NOT NULL CHECK (ertekeles BETWEEN 1 AND 5),
      k1          char(1)     NOT NULL CHECK (k1 IN ('A','B','C')),
      k2          char(1)     NOT NULL CHECK (k2 IN ('A','B','C')),
      palya       text        NOT NULL,
      pont        smallint    NOT NULL CHECK (pont BETWEEN 0 AND 100),
      letrehozva  timestamptz NOT NULL DEFAULT now()
    )`;
  tablaKesz = true;
}

/* --- belépés --------------------------------------------------------------
   Nincs felhasználónév, egyetlen jelszó van, környezeti változóban. A jegy egy
   lejárati időbélyeg és annak HMAC-aláírása: a kiszolgálónak nem kell
   munkamenetet tárolnia, a jegyet viszont nem lehet meghamisítani a jelszó
   ismerete nélkül.
   -------------------------------------------------------------------------- */

export const SUTI_NEV = "vb_admin";
const ERVENYESSEG_MP = 8 * 60 * 60;

function titok(){
  const t = process.env.ADMIN_JELSZO;
  if(!t) throw new Error("Hiányzik az ADMIN_JELSZO környezeti változó.");
  return t;
}

/* Mindkét oldalt előbb elkeverjük, így az összehasonlítandó adat mindig 32
   bájt: a jelszó hossza sem derül ki abból, mennyi ideig tart a válasz. */
export function jelszoEgyezik(megadott){
  const a = createHash("sha256").update(String(megadott ?? "")).digest();
  const b = createHash("sha256").update(titok()).digest();
  return timingSafeEqual(a, b);
}

export function jegyKeszit(){
  const lejar = Date.now() + ERVENYESSEG_MP * 1000;
  return lejar + "." + createHmac("sha256", titok()).update(String(lejar)).digest("hex");
}

export function jegyErvenyes(jegy){
  const [lejar, alairas] = String(jegy || "").split(".");
  if(!/^\d+$/.test(lejar || "") || !alairas) return false;
  if(Number(lejar) < Date.now()) return false;
  const vart = createHmac("sha256", titok()).update(lejar).digest("hex");
  const a = Buffer.from(vart, "hex"), b = Buffer.from(alairas, "hex");
  return a.length === b.length && timingSafeEqual(a, b);
}

export function suti(req, nev){
  for(const resz of String(req.headers.cookie || "").split(";")){
    const [kulcs, ...ertek] = resz.trim().split("=");
    if(kulcs === nev) return decodeURIComponent(ertek.join("="));
  }
  return null;
}

/* A `Secure` jelző https-t követel meg. Helyi kiszolgálón ez azt jelentené,
   hogy a böngésző eldobja a sütit, és a felület kipróbálhatatlan — ezért ott
   elmarad. Éles kiszolgálón mindig ott van. */
export function sutitBeallit(req, res, ertek, mpMulva){
  const helyi = /^(localhost|127\.0\.0\.1)(:|$)/.test(String(req.headers.host || ""));
  res.setHeader("Set-Cookie",
    `${SUTI_NEV}=${ertek}; HttpOnly; SameSite=Strict; Path=/; Max-Age=${mpMulva}` +
    (helyi ? "" : "; Secure"));
}

export function belepett(req){
  return jegyErvenyes(suti(req, SUTI_NEV));
}
