# BioFM Landscape — Classification & Survey

Snapshot date: 2026-04-17. Sources: cloned survey repos under `research/` and recent (2025–2026) literature surveyed via web. Where a model has an HF hub or GitHub link, it is preferred for hands-on use in the two downstream projects.

## 1. Classification axes

Every biological foundation model (BioFM) can be placed along several orthogonal axes. We use these to group the landscape instead of forcing one taxonomy.

| Axis | Typical values |
|---|---|
| **Modality** | DNA, RNA, protein sequence, protein structure, single-cell transcriptomics, spatial transcriptomics, pathology image, mass spec, literature/text, multimodal |
| **Architecture** | encoder-only Transformer (BERT-style), decoder-only Transformer (GPT/Mistral/LLaMA), enc-dec (T5), state-space / long-convolution (Hyena, Mamba, StripedHyena), graph NN, diffusion, flow matching |
| **Tokenization** | character / 1-mer, k-mer (e.g. 6-mer), byte-pair, species-aware BPE, BioToken (annotation-aware), rank-value gene tokens, structure tokens (3Di, SaProt), cell-as-sentence |
| **Pretraining objective** | masked LM, causal LM, denoising reconstruction, contrastive (cell ↔ cell, seq ↔ structure), supervised multi-task |
| **Pipeline role** | representation / embedding, zero-shot variant effect scoring, generative design, classifier backbone, retrieval, annotation |
| **License** | permissive (Apache-2, MIT), research-only (CC-BY-NC), closed |

## 2. Groupings by domain and pipeline fit

### 2.1 DNA & genome — "read the book of life"

| Model | Arch | Tokens | Objective | Best pipeline slot | Strengths |
|---|---|---|---|---|---|
| [Enformer](https://github.com/lucidrains/enformer-pytorch) | Conv + Transformer | 1-mer | supervised (expression tracks) | gene expression & regulatory prediction from ~200 kb context | long-range interactions, battle-tested baseline |
| [DNABERT / DNABERT-2 / DNABERT-S](https://github.com/MAGICS-LAB/DNABERT_2) | Encoder-only | 6-mer / BPE | MLM | promoter/TF binding classifier backbone | mature, many downstream heads |
| [Nucleotide Transformer](https://github.com/instadeepai/nucleotide-transformer) | Encoder-only | 6-mer | MLM | variant-effect prediction across species | 2.5B params, multi-species corpus |
| [HyenaDNA](https://github.com/HazyResearch/hyena-dna) | Hyena (long-conv) | 1-nt | CLM | single-nucleotide resolution over ~1 M bp | sub-quadratic long context |
| [GENA-LM](https://github.com/AIRI-Institute/GENA_LM) | Encoder-only | BPE | MLM | long-range regulatory tasks | 36 kb context |
| [GPN / GPN-MSA](https://github.com/songlab-cal/gpn) | Encoder-only | 1-nt (MSA-aware) | MLM | genome-wide variant effect (conservation-aware) | zero-shot deleteriousness scoring |
| [Evo](https://github.com/evo-design/evo) | StripedHyena | 1-nt | CLM | prokaryotic genome design (e.g. CRISPR-Cas) | 131 kb context, generative |
| [Evo 2](https://arcinstitute.org/tools/evo) | StripedHyena-2 | 1-nt | CLM | cross-domain (bacteria→eukaryotes), variant impact zero-shot | 7B & 40B, 1 M context, 9.3 T bp |
| **[BioFM-265M](https://huggingface.co/m42-health/BioFM-265M)** | **Mistral decoder** | **BioToken (annotation-aware)** | **CLM** | **variant effect, sQTL, coding/noncoding pathogenicity; small enough for CPU eval** | **biologically-informed tokens beat Enformer/SpliceTransformer at <1% params** |
| [Caduceus](https://github.com/kuleshov-group/caduceus) | Mamba (RC-equivariant) | 1-nt | MLM | reverse-complement-aware DNA | bi-directional state-space |

### 2.2 RNA — structure & regulation

| Model | Arch | Key feature | Pipeline slot |
|---|---|---|---|
| [RNA-FM](https://github.com/ml4bio/RNA-FM) | Encoder-only | 23M ncRNA | secondary structure, function |
| [RNABERT](https://github.com/mana438/RNABERT) | Encoder-only | alignment & clustering | motif discovery |
| [SpliceBERT](https://github.com/biomed-AI/SpliceBERT) | Encoder-only | pre-mRNA | splice site prediction |
| [RiNALMo](https://github.com/lbcb-sci/RiNALMo) | Encoder-only | 650M | general-purpose RNA probe |
| ERNIE-RNA | Encoder-only | structure-enhanced | RNA LM with pairing prior |
| [GenerRNA](https://github.com/pfnet-research/GenerRNA) | Decoder-only | generative | de novo RNA design |
| ATOM-1 | Decoder-only | chemical mapping data | structure/function from reactivity |
| Orthrus | dual-tower | evolutionary + functional | contrastive RNA FM |

### 2.3 Protein — sequence, structure, design

| Model | Arch | Key feature | Pipeline slot |
|---|---|---|---|
| [ESM-2 / ESM-3](https://github.com/evolutionaryscale/esm) | Encoder-only / multimodal | up to 98B (ESM-3); sequence+structure+function | embeddings, zero-shot variant fitness, structure |
| [ProtTrans / ProtBERT](https://github.com/agemagician/ProtTrans) | Encoder / enc-dec | broad suite | general-purpose embeddings |
| [ProtGPT2](https://huggingface.co/nferruz/ProtGPT2) | Decoder-only | 738M | de novo protein design |
| [ProGen2 / ProGen3](https://github.com/salesforce/progen) | Decoder-only | up to 46B | conditional family generation |
| [SaProt](https://github.com/westlake-repl/SaProt) | Encoder + 3Di vocab | structure-aware tokens | fitness, function |
| [Ankh](https://github.com/agemagician/Ankh) | Enc-dec (T5) | efficiency-optimized | general-purpose |
| [ProLLaMA](https://github.com/Lyu6PosHao/ProLLaMA) | Decoder-only | instruction-tuned | multi-task protein LM |
| [ESMFold / OpenFold](https://github.com/aqlaboratory/openfold) | End-to-end folder | MSA-free / MSA | structure prediction |
| AlphaFold2/3 (reference) | Evoformer + diffusion | MSA + templates | structure & complex prediction |
| RoseTTAFold / RF2 / RF-AA | 3-track / all-atom | multi-chain, ligands | interaction prediction |

### 2.4 Single-cell — "cells as sentences"

| Model | Arch | Cells pretrained | Objective | Pipeline slot |
|---|---|---|---|---|
| [scBERT](https://github.com/TencentAILabHealthcare/scBERT) | Encoder-only (Performer) | ~1M | MLM on binned expression | cell-type annotation |
| [Geneformer](https://huggingface.co/ctheodoris/Geneformer) | Encoder-only | 30M → 95M | rank-value MLM | network biology, in-silico perturbation |
| [scGPT](https://github.com/bowang-lab/scGPT) | Decoder-only | 33M | generative, multi-omics heads | batch integration, perturbation, GRN |
| [scFoundation](https://github.com/biomap-research/scFoundation) | Enc-dec | 50M | denoising reconstruction | expression imputation, downstream tuning |
| [scPRINT / scPRINT-2](https://github.com/cantinilab/scPRINT) | Encoder-only | 50M → 350M (16 species) | multi-task | denoising, cell typing, GRN |
| [UCE](https://github.com/snap-stanford/UCE) | Encoder-only | 36M | contrastive, species-agnostic | zero-shot cell embedding across species |
| [Nicheformer](https://github.com/theislab/nicheformer) | Encoder-only | 110M (dissociated + spatial) | MLM | spatial niche prediction |
| CellPLM | Encoder-only | pre-training beyond single cells | MLM | integrates spatial context |
| SCimilarity | Encoder-only | ~28M | contrastive | large-scale cell search |
| [CellFM](https://github.com/biomed-AI/CellFM) | Encoder-only | 100M | MLM | general-purpose scRNA backbone |
| scMulan | Decoder-only | generative multitask | cell generation & annotation |

### 2.5 Multimodal / science LLMs

| Model | Modalities | Pipeline slot |
|---|---|---|
| [Galactica](https://github.com/paperswithcode/galai) | text + SMILES + DNA/protein tokens | scientific text / citation completion |
| [BioT5 / BioT5+](https://github.com/QizhiPei/BioT5) | text + IUPAC + SMILES + protein | cross-modal retrieval & QA |
| [ChatCell](https://github.com/zjunlp/ChatCell) | natural language ↔ cell states | cell analysis conversational UI |
| NatureLM | text + sequences | scientific reasoning over life-science entities |
| Evo / Evo 2 | DNA-centric but generalizes | genome-scale generative design |
| [Med42 / Med-PaLM](https://huggingface.co/m42-health/med42-70b) | biomedical text | clinical QA (same vendor as BioFM-265M) |

### 2.6 Pathology / imaging FMs

| Model | Backbone | Notes |
|---|---|---|
| [UNI](https://github.com/mahmoodlab/UNI) | ViT-H/14 (DINOv2) | 100K WSI |
| [Virchow](https://huggingface.co/paige-ai/Virchow) | ViT-H | 1.5M WSI |
| [CONCH](https://github.com/mahmoodlab/CONCH) | ViT + text | vision-language pathology |
| [PLIP](https://github.com/PathologyFoundation/plip) | CLIP-style | captioned pathology images |

## 3. Pipeline fit cheat-sheet

```
raw reads / VCF   ─► DNA FM (Evo2, BioFM-265M, NT, HyenaDNA)   ─► variant effect, QTL, expression
                                                                ▼
scRNA counts      ─► scFM (Geneformer, scGPT, scPRINT-2)        ─► cell typing, GRN, perturbation
                                                                ▼
protein seq       ─► ESM-2/3, SaProt, ProGen3                   ─► fitness, function, design
                                                                ▼
protein structure ─► AlphaFold3 / RF-AA / ESMFold               ─► complex & interaction
                                                                ▼
image (WSI)       ─► UNI / Virchow / CONCH                      ─► morphology, biomarker
                                                                ▼
any of the above ──► Multimodal LLM (Evo2, BioT5+, Galactica) ──► reasoning, design loop
```

## 4. Why BioFM-265M is the focus for the test-time-compute project

1. **Open weights, CC-BY-NC**, runs on CPU (M2 Pro, 16 GB) — exactly the setting where test-time compute scaling (extra samples, verifiers, search) pays off vs. just training a bigger model.
2. **Causal Mistral decoder** → `model.generate()` supports `temperature`, `top_k/top_p`, `num_return_sequences`, `do_sample` out of the box — standard TTC levers.
3. **Annotation-aware tokenizer** means there is a built-in, biology-aligned verifier signal (variant annotation matches → preserved under generation) that can be used as a TTC scoring function instead of a black-box reward model.
4. **Variant Benchmark dataset already shipped** (`m42-health/variant-benchmark`) → we can measure TTC gains quantitatively with linear-probe AUC.

## 5. Sources

- Survey repos (cloned): `research/Awesome-Bio-Foundation-Models/`, `research/awesome-foundation-model-single-cell-papers/`
- BioFM-265M source: `research/biofm-eval/` and [HF card](https://huggingface.co/m42-health/BioFM-265M)
- Recent reviews: Nature Experimental & Molecular Medicine 2025, Genome Biology 2025, National Science Review 2025
- Model cards & papers linked inline above.
