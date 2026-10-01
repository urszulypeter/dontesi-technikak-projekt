#!/bin/bash
# A kiválasztott Microsoft Rocketbox alakok (MIT) letöltése ./rbsrc alá: FBX + szín- és normáltérképek.
mkdir -p rbsrc && cd rbsrc
ALAKOK="Professions/Business_Male_01 Professions/Business_Male_02 Professions/Business_Male_03 Professions/Business_Male_06 Professions/Business_Female_01 Professions/Business_Female_03 Professions/Business_Female_04 Adults/Male_Adult_03 Adults/Male_Adult_05 Adults/Male_Adult_08 Adults/Male_Adult_14 Adults/Female_Adult_02 Adults/Female_Adult_09 Adults/Female_Adult_14 Professions/Military_Male_02 Professions/Military_Male_05 Professions/Military_Male_06 Professions/Military_Female_01 Professions/Construction_Male_02"
for p in $ALAKOK; do
  n=$(basename $p); mkdir -p $n
  (
    cd $n; B=https://raw.githubusercontent.com/microsoft/Microsoft-Rocketbox/master/Assets/Avatars/$p
    [ -f $n.fbx ] || curl -sfL -o $n.fbx $B/Export/$n.fbx || echo "HIBA fbx $n"
    for t in $(gh api "repos/microsoft/Microsoft-Rocketbox/contents/Assets/Avatars/$p/Textures" --jq '.[].name' | grep -v -i specular); do
      [ -f $t ] || curl -sfL -o $t "$B/Textures/$t" || echo "HIBA $n/$t"
    done
  ) &
done
wait
