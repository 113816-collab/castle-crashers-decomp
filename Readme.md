# castle-crashers-decomp

Edits from og game:
- replaced .fnt with .json
- replaced .dds with .png
- decompiled the pak files (not bsps idk how to do that one)
- replaced .xma with .mp3
- replaced binary .xpu and .xvu with readable .psa and .vsa

all i know about bsps .pak files:
- its a zip file with a called BSP%s.PDAG.NREC
- bsps files load from f_BSPLoadLevel that is defined in the [castle.exe](https://gofile.io/d/SObWSm) file

all files were just decompiled, no code from game/ and levels/ folder were messed with, so the renamed files won't work probably

> honestly idrk what i was doing