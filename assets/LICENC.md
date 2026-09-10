# Az eszközök forrása és licence

A nyitókép (`heroInit()` az `index.html`-ben) valódi, szabadon felhasználható
3D-eszközökből épül. Ez a fájl sorolja fel mindet, forrással és licenccel együtt.
A CC-BY licencű elemeknél a névattribúció kötelező — az alábbi lista teljesíti ezt.

## Környezetfény (HDRI)

| Fájl | Eredeti | Szerző | Forrás | Licenc |
|---|---|---|---|---|
| `hdri/dresden_square_768.hdr` | Dresden Square | Greg Zaal | [Poly Haven](https://polyhaven.com/a/dresden_square) | CC0 |

Ez adja a tér irányfüggő megvilágítását és az ablakon kilátszó valódi városképet is.

## Felületek (PBR anyagok)

| Fájl | Eredeti | Szerző | Forrás | Licenc |
|---|---|---|---|---|
| `felulet/padlo_diff.webp` | Granite Tile 03 | Charlotte Baglioni | [Poly Haven](https://polyhaven.com/a/granite_tile_03) | CC0 |
| `felulet/fal_*.webp` | Plastered Wall 05 | Charlotte Baglioni | [Poly Haven](https://polyhaven.com/a/plastered_wall_05) | CC0 |

## Modellek

| Fájl | Eredeti | Szerző | Forrás | Licenc |
|---|---|---|---|---|
| `modell/modern_arm_chair_01.glb` | Modern Arm Chair 01 | Vibrant Nordic | [Poly Haven](https://polyhaven.com/a/modern_arm_chair_01) | CC0 |
| `modell/sofa_02.glb` | Sofa 02 | Kirill Sannikov | [Poly Haven](https://polyhaven.com/a/sofa_02) | CC0 |
| `modell/modern_coffee_table_01.glb` | Modern Coffee Table 01 | Amin | [Poly Haven](https://polyhaven.com/a/modern_coffee_table_01) | CC0 |
| `modell/potted_plant_01.glb` | Potted Plant 01 | Rico Cilliers | [Poly Haven](https://polyhaven.com/a/potted_plant_01) | CC0 |
| `modell/potted_plant_02.glb` | Potted Plant 02 | Rico Cilliers | [Poly Haven](https://polyhaven.com/a/potted_plant_02) | CC0 |
| `modell/modern_ceiling_lamp_01.glb` | Modern Ceiling Lamp 01 | James Ray Cock | [Poly Haven](https://polyhaven.com/a/modern_ceiling_lamp_01) | CC0 |
| `modell/chess_set.glb` | Chess Set | Riley Queen | [Poly Haven](https://polyhaven.com/a/chess_set) | CC0 |
| `modell/ceramic_vase_01.glb` | Ceramic Vase 01 | James Ray Cock | [Poly Haven](https://polyhaven.com/a/ceramic_vase_01) | CC0 |
| `modell/wall_clock.glb` | Wall Clock | PierreB3D | [Poly Haven](https://polyhaven.com/a/wall_clock) | CC0 |
| `modell/marble_bust_01.glb` | Marble Bust 01 | Rico Cilliers | [Poly Haven](https://polyhaven.com/a/marble_bust_01) | CC0 |
| `modell/ClassicConsole_01.glb` | Classic Console 01 | Kirill Sannikov | [Poly Haven](https://polyhaven.com/a/ClassicConsole_01) | CC0 |

## Alakok

| Fájl | Eredeti | Szerző | Forrás | Licenc |
|---|---|---|---|---|
| `modell/emberek.glb` | „Fitg013" — két fotogrammetriával szkennelt alak | **LGA-NA** | [Sketchfab](https://sketchfab.com/3d-models/59d4622960164eed88fe31ea284cc1ab) · [Objaverse](https://huggingface.co/datasets/allenai/objaverse) | **CC BY 4.0** |
| `modell/vendeg.glb` | „MM" — fotogrammetriával szkennelt alak | **LGA-NA** | [Sketchfab](https://sketchfab.com/3d-models/ce39df9e32084c348e741605d4d28cb0) · [Objaverse](https://huggingface.co/datasets/allenai/objaverse) | **CC BY 4.0** |

> **Kötelező attribúció:** „Fitg013" és „MM" by **LGA-NA**,
> [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), forrás: Sketchfab.
> A modellek módosítva lettek: a „Fitg013" két alakja külön objektumra bontva és
> 1 499 992 → 2 × 32 000 háromszögre egyszerűsítve, az „MM" 916 867 → 53 916
> háromszögre; a textúrák WebP-be átkódolva.
>
> Ez a hivatkozás jelenik meg a nyitóoldal láblécében is, hogy a licenc a
> futó alkalmazásban is teljesüljön.

## Amit nem használunk és miért

- **Renderpeople / Human Alloy ingyenes minták** — a licencük tiltja, hogy a
  modellfájlok külön letölthetők legyenek, márpedig egy WebGL-oldalon azok.
- **Mixamo-karakterek** — az Adobe feltételei a különálló eszközként való
  továbbterjesztést nem engedik; egy publikus repóban a `.glb` pontosan ez.
- **Objaverse-ben talált, valódi közszereplőket ábrázoló szkennek** — a
  személyiségi jog és a témával való nem kívánt asszociáció miatt.

## Feldolgozás

Minden eszköz az eredetiből készült, `@gltf-transform` és `sharp` segítségével:
textúrák WebP-be, geometria `EXT_meshopt_compression`-nel tömörítve, a
poligonszám a webes megjelenítéshez szükséges szintre csökkentve.
