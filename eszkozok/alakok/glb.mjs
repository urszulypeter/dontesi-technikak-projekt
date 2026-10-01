// Rocketbox FBX → webes GLB: textúrák rákötése, tömörítés (meshopt + WebP).
// Munkakönyvtárból: npm i fbx2gltf @gltf-transform/core @gltf-transform/extensions @gltf-transform/functions meshoptimizer
//                   node glb.mjs <repo>/assets/alak [alaknév …]
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS, EXTMeshoptCompression, EXTTextureWebP } from '@gltf-transform/extensions';
import { dedup, prune, reorder, quantize } from '@gltf-transform/functions';
import { MeshoptEncoder, MeshoptDecoder } from 'meshoptimizer';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const S = process.cwd();
const FBX2GLTF = path.join(S, 'node_modules/fbx2gltf/bin/Darwin/FBX2glTF');
const CEL = process.argv[2];
const csak = process.argv.slice(3);

await MeshoptEncoder.ready; await MeshoptDecoder.ready;
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS)
  .registerDependencies({ 'meshopt.encoder': MeshoptEncoder, 'meshopt.decoder': MeshoptDecoder });

const DURVA = { body: 0.82, head: 0.62, opacity: 0.7, helmet: 0.55, equipment: 0.75 };

for (const nev of fs.readdirSync(path.join(S, 'rbsrc')).sort()) {
  if (csak.length && !csak.includes(nev)) continue;
  const src = path.join(S, 'rbsrc', nev, nev + '.fbx');
  const tmp = path.join(S, 'tmp', nev);
  fs.mkdirSync(path.dirname(tmp), { recursive: true });
  execFileSync(FBX2GLTF, ['--binary', '--input', src, '--output', tmp], { stdio: 'ignore' });
  const doc = await io.read(tmp + '.glb');
  const root = doc.getRoot();
  root.listTextures().forEach(t => t.dispose());
  for (const m of root.listMaterials()) {
    const resz = m.getName().replace(/^[a-z]+\d+_/, '');
    const szin = path.join(S, 'tex', nev, resz + '_c.webp');
    const norm = path.join(S, 'tex', nev, resz + '_n.webp');
    if (!fs.existsSync(szin)) { console.warn(nev, 'hiányzó textúra', resz); continue; }
    m.setBaseColorTexture(doc.createTexture(resz + '_c').setMimeType('image/webp').setImage(fs.readFileSync(szin)).setURI(resz + '_c.webp'));
    if (fs.existsSync(norm))
      m.setNormalTexture(doc.createTexture(resz + '_n').setMimeType('image/webp').setImage(fs.readFileSync(norm)).setURI(resz + '_n.webp'));
    m.setMetallicFactor(0).setRoughnessFactor(DURVA[resz] ?? 0.75).setBaseColorFactor([1, 1, 1, 1]);
    m.setEmissiveFactor([0, 0, 0]);
    if (resz === 'opacity') m.setAlphaMode('MASK').setAlphaCutoff(0.42).setDoubleSided(true);
  }
  // a csúcsszín mindenhol fehér: csak helyet foglalna
  root.listMeshes().forEach(me => me.listPrimitives().forEach(p => { const c = p.getAttribute('COLOR_0'); if (c) { p.setAttribute('COLOR_0', null); } }));
  // az üres animáció kidobása
  root.listAnimations().forEach(a => a.dispose());
  doc.createExtension(EXTTextureWebP).setRequired(true);
  doc.createExtension(EXTMeshoptCompression).setRequired(true).setEncoderOptions({ method: EXTMeshoptCompression.EncoderMethod.QUANTIZE });
  await doc.transform(dedup(), prune(), reorder({ encoder: MeshoptEncoder }), quantize());
  const ki = path.join(CEL, nev.toLowerCase() + '.glb');
  await io.write(ki, doc);
  console.log(nev, Math.round(fs.statSync(ki).size / 1024), 'KB');
}
