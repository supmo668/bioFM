# Stereo guard {t,m,s} — measured effect on the snapshot

- snapshot: `data/raw/drugbank`
- journal run: `/Users/mo/github/personal/bioFM/worktrees/lung-on-chipsim/projects/lung-on-chipsim/journal/20260915T094806Z-2fe6fafa`
- compounds canonicalized: **6802**
- guard fired on: **1599** (23.5%)
- merge groups: **191 → 156**
- groups split by the guard: **41**
- groups newly merged by the guard: **0**

## Stage breakdown

| stage | without guard | with guard |
|---|---:|---:|
| upstream-duplicate | 100 | 101 |
| parse | 2 | 3 |
| salt | 19 | 19 |
| uncharge | 22 | 26 |
| tautomer | 48 | 7 |

Rollup (CTO's categories; `parse` folded into salt_or_uncharge):

| category | without guard | with guard |
|---|---:|---:|
| source_identical | 100 | 101 |
| salt_or_uncharge | 43 | 48 |
| tautomer | 48 | 7 |

Source-identical count, exactly: **100 without the guard, 101 with it** (any difference is reclassification, not a new merge).

## Split groups

Every group that exists without the guard and is split by it — the record of reference.

| # | members (name) | stage before | layers altered | keys after |
|---:|---|---|---|---|
| 1 | R-3-FLUORO-4-[2-HYDROXY-2-(5,5,8,8-TETRAMETHYL-5,6,7,8,-TETRAHYDRO-NAPHTALEN-2-YL)-ACETYLAMINO]-BENZOIC ACID \| 3-FLUORO-4-[2-HYDROXY-2-(5,5,8,8-TETRAMETHYL-5,6,7,8,-TETRAHYDRO-NAPHTALEN-2-YL)-ACETYLAMINO]-BENZOIC ACID | tautomer | m,s,t | AANFHDFOMFRLLR / AANFHDFOMFRLLR |
| 2 | Donepezil \| 1-BENZYL-4-[(5,6-DIMETHOXY-1-INDANON-2-YL)METHYL]PIPERIDINE | tautomer | m,s,t | ADEBPBSSDYVVLD / ADEBPBSSDYVVLD |
| 3 | L-Isoleucine \| Allo-Isoleucine | tautomer | m,s,t | AGPKZVBTJJNPAG / AGPKZVBTJJNPAG |
| 4 | L-Threonine \| D-Threonine | tautomer | m,s,t | AYFVYJQAPQTCCC / AYFVYJQAPQTCCC |
| 5 | L-Guluronic Acid 6-Phosphate \| 6-Phosphogluconic Acid | tautomer | m,s,t | BIRSGZKFKXLSJQ / BIRSGZKFKXLSJQ |
| 6 | Malate Like Intermediate \| Malate Ion | tautomer | m,s,t | BJEPYKJPYRNKOW / QFBHYOKSQPPXHZ |
| 7 | L-Aspartic Acid \| D-Aspartic Acid \| L-Iso-Aspartate | tautomer | m,s,t | CKLJMWTZIZZHCS / CKLJMWTZIZZHCS |
| 8 | L-Phenylalanine \| D-Phenylalanine | tautomer | m,s,t | COLNVLDHVKWLRT / COLNVLDHVKWLRT |
| 9 | (10S)-10-Formyl-5,8,10-Trideazafolic Acid \| (10R)-10-Formyl-5,8,10-Trideazafolic Acid | tautomer | m,s,t | DAOQLLQRJAXMGY / DAOQLLQRJAXMGY |
| 10 | L-Asparagine \| D-Asparagine | tautomer | m,s,t | DCXYFEDJOCDNAF / DCXYFEDJOCDNAF |
| 11 | D-Glucose in Linear Form \| Tagatose | tautomer | m,s,t | BJHIKXHVCXFQLS / GZCGUPFRVQAUEE |
| 12 | Captopril \| 1-(3-Mercapto-2-Methyl-Propionyl)-Pyrrolidine-2-Carboxylic Acid | tautomer | m,s,t | FAKRSMQSSFJEIM / FAKRSMQSSFJEIM |
| 13 | L-Methionine \| D-Methionine | tautomer | m,s,t | FFEARJCKVFRZRR / FFEARJCKVFRZRR |
| 14 | Glyceraldehyde-3-Phosphate \| 1,3-Dihydroxyacetonephosphate | tautomer | m,s,t | GNGACRATGGDKBX / LXJXRIRHZLFYRP |
| 15 | L-[(N-Hydroxyamino)Carbonyl]Phenylalanine \| D-[(N-Hydroxyamino)Carbonyl]Phenylalanine | tautomer | m,s,t | IOFPEOPOAMOMBE / IOFPEOPOAMOMBE |
| 16 | Loracarbef \| 7-(2-Amino-2-Phenyl-Acetylamino)-3-Chloro-8-Oxo-1-Aza-Bicyclo[4.2.0]Oct-2-Ene-2-Carboxylic Acid | tautomer | t | JAPHQRWPEGVNBT / JAPHQRWPEGVNBT |
| 17 | D-Lactic Acid \| Lactic Acid \| Ammonium lactate | tautomer | m,s,t | JVTAAEKCZFNVCJ / JVTAAEKCZFNVCJ |
| 18 | 7-((Carboxy(4-Hydroxyphenyl)Acetyl)Amino)-7-Methoxy-(3-((1-Methyl-1h-Tetrazol-5-Yl)Thio)Methyl)-8-Oxo-5-Oxa-1-Azabicyclo[4.2.0]Oct-2-Ene-2-Carboxylic Acid \| Latamoxef | tautomer | t | JWCSIUVGFCSJCK / JWCSIUVGFCSJCK |
| 19 | Gallichrome \| Ferricrocin-Iron | tautomer | m,s,t | JXJRJDNSPWNZOK / JXJRJDNSPWNZOK |
| 20 | Dicoumarol \| Bishydroxy[2h-1-Benzopyran-2-One,1,2-Benzopyrone] | tautomer | t | HIZKPJUTKKJDGA / KSKRYQVHJQRUNC |
| 21 | WRR-99 \| WRR-112 | tautomer | m,s,t | KVZMXOVSHIMGNA / KVZMXOVSHIMGNA |
| 22 | Bupivacaine \| Levobupivacaine | tautomer | m,s,t | LEBVLXFERQHONN / LEBVLXFERQHONN |
| 23 | L-Serine \| D-Serine \| Serine Vanadate | tautomer | m,s,t | MTCFGRXMJLQNBG / MTCFGRXMJLQNBG |
| 24 | Isocitric Acid \| Isocitrate Calcium Complex | tautomer | m,s,t | ODBLHEXUDAPZAU / ODBLHEXUDAPZAU |
| 25 | D-Galctopyranosyl-1-On \| Gluconolactone | tautomer | m,s,t | PHOQVHQSTUBQQK / PHOQVHQSTUBQQK |
| 26 | S-Hydroxymethyl Glutathione \| LJP 1082 | tautomer | m,s,t | PIUSLWSYOYFRFR / PIUSLWSYOYFRFR |
| 27 | 3(S)-METHYLCARBAMOYL-7-SULFOAMINO-3,4-DIHYDRO-1H-ISOQUINOLINE-2-CARBOXYLIC ACID TERT-BUTYL ESTER \| 3(R)-METHYLCARBAMOYL-7-SULFOAMINO-3,4-DIHYDRO-1H-ISOQUINOLINE-2-CARBOXYLIC ACID TERT-BUTYL ESTER | tautomer | m,s,t | PPSSYXOFPICMQD / PPSSYXOFPICMQD |
| 28 | Iodo-Phenylalanine \| 4-IODOPHENYLALANINE | tautomer | m,s,t | PZNQZSRPDOEBMS / PZNQZSRPDOEBMS |
| 29 | Gluconic Acid \| Sodium stibogluconate | tautomer | m,s,t | RGHNJXZEOKUKBD / RGHNJXZEOKUKBD |
| 30 | Hyoscyamine \| Atropine | tautomer | m,s,t | RKUNBYITZUJHSG / RKUNBYITZUJHSG |
| 31 | 2-Ammoniobut-3-Enoate, 2-Amino-3-Butenoate \| Vinylglycine | tautomer | m,s,t | RQVLGLPAZTUBKX / RQVLGLPAZTUBKX |
| 32 | Dihydroxyacetone \| (2r)-2,3-Dihydroxypropanal | tautomer | m,s,t | MNQZXJOMYWMBOU / RXKJFZQQPQGTFL |
| 33 | Flurbiprofen \| MPC-7869 | tautomer | m,s,t | SYTBZMRGLBWNTM / SYTBZMRGLBWNTM |
| 34 | N-[(6-BUTOXYNAPHTHALEN-2-YL)SULFONYL]-L-GLUTAMIC ACID \| N-[(6-BUTOXYNAPHTHALEN-2-YL)SULFONYL]-D-GLUTAMIC ACID | tautomer | m,s,t | UAGYXJBYAFGRFR / UAGYXJBYAFGRFR |
| 35 | 2-Oxalosuccinic Acid \| 4-Hydroxy-Aconitate Ion | tautomer | m,s,t | UFSCUAXLTRFIDC / WUUVSJBKHXDKBS |
| 36 | bis(molybdopterin)tungsten cofactor \| Molybdenum Cofactor \| (Molybdopterin-S,S)-Dioxo-Thio-Molybdenum(V) \| Tungstopterin Cofactor | tautomer | m,s,t | HPEUEJRPDGMIMY / HPEUEJRPDGMIMY / UURFNJWEJXZQIN |
| 37 | Glucose-6-Phosphate \| Fructose -6-Phosphate | tautomer | m,s,t | GSXOAOHZAIYLCY / VFRROHXSMXFLSN |
| 38 | Leucovorin \| 5-Formyl-5,6,7,8-Tetrahydrofolate | tautomer | t | VVIAGPKUTFNRDU / VVIAGPKUTFNRDU |
| 39 | Levothyroxine \| Dextrothyroxine \| Liotrix | tautomer | m,s,t | XUIIKFGFIJCVMT / XUIIKFGFIJCVMT |
| 40 | L-Cysteine \| S-(Methylmercury)-L-Cysteine \| D-Cysteine | tautomer | m,s,t | XUJNEKJLAYXESH / XUJNEKJLAYXESH |
| 41 | Dexbrompheniramine \| Brompheniramine | tautomer | m,s,t | ZDIGNSYAACHWNL / ZDIGNSYAACHWNL |

## New merges

None.

## Reclassified groups (same members, different stage)

None.
