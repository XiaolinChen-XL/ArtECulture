# ArtECulture

**Benchmarking Culture-Conditioned Visual Emotion Understanding in Multimodal Large Language Models**

[Paper](https://arxiv.org/abs/2608.03358) | [Download images](https://drive.google.com/file/d/1pqkivBdU-aRoFaQWOC9JQcc-5qyNcLlU/view?usp=sharing)

ArtECulture contains 6,792 artwork records with English-, Chinese-, and Arabic-community emotion labels and 92,062 explanations. The repository provides the benchmark, cultural emotion knowledge base, and implementations of zero-shot prediction, retrieval-augmented inference, and supervised fine-tuning.

| Resource | Train | Validation | Test | Total |
|---|---:|---:|---:|---:|
| Artwork records | 5,434 | 679 | 679 | 6,792 |
| English explanations | 24,835 | 3,037 | 3,060 | 30,932 |
| Chinese explanations | 25,256 | 3,144 | 3,159 | 31,559 |
| Arabic explanations | 23,694 | 2,901 | 2,976 | 29,571 |
| All explanations | 73,785 | 9,082 | 9,195 | 92,062 |

The knowledge base contains 8,439 concept-culture entries and 28,146 associated rationales: English 2,784/9,538; Chinese 2,902/9,626; Arabic 2,753/8,982.

## Layout

```text
data/
  metadata.csv                 # Authoritative labels, region groups, and split assignments
  splits/{train,val,test}.csv   # Exact subsets of metadata.csv
  explanations/{en,zh,ar}.jsonl # Individual annotations, without annotator identifiers
  image_manifest.csv           # Actual archive paths, sizes, and SHA-256 hashes
  labels.json
knowledge_base/
  {en,zh,ar,all}.jsonl          # Compatible with retrieval_augmented_inference.py
scripts/                       # Research scripts, input adapters, and validation
docs/                          # Data schema and research workflow
assets/ArtECulture_Image.tar.gz            # Image archive; distribute separately from Git
```

## Quick start

Use Python 3.10 or later. Data preparation, validation, zero-shot API clients, and evaluation use the Python standard library. Run commands from the repository root.

Download **ArtECulture_Image.tar.gz** from [Google Drive](https://drive.google.com/file/d/1pqkivBdU-aRoFaQWOC9JQcc-5qyNcLlU/view?usp=sharing), create an `assets/` directory, and place the archive there. The archive is hosted separately from the GitHub repository.

```bash
tar -xzf assets/ArtECulture_Image.tar.gz
python scripts/prepare_inputs.py --split test --output runs/test.jsonl
```

The image archive extracts to `Image/`. To use an existing extracted image directory, pass `--image-root /your/path/to/Image` to `prepare_inputs.py`. Use the `image_path` field to locate each image.

Example standard-library loading:

```python
import csv
import json
from pathlib import Path

root = Path('.')
with (root / 'data/splits/test.csv').open(encoding='utf-8', newline='') as f:
    records = list(csv.DictReader(f))
with (root / 'data/explanations/en.jsonl').open(encoding='utf-8') as f:
    explanations = {r['image_id']: r['explanations'] for r in map(json.loads, f)}
image = root / records[0]['image_path']
label = records[0]['english_emotion']
references = explanations[records[0]['image_id']]
```

Retrieval requires pre-extracted visual concepts. Concept extraction code and precomputed concept files are not included in this release.

See [the pipeline guide](docs/PIPELINE.md) for zero-shot inference, retrieval, knowledge construction, SFT, and evaluation. See [the schema](docs/SCHEMA.md) before joining tables.

## Data notes

Nine canonical labels are used: `amusement`, `awe`, `contentment`, `excitement`, `anger`, `disgust`, `fear`, `sadness`, and `something else`.

`country` is an original source-country or artistic-tradition field, not a normalized country code. Values such as `chinese`, `islamic`, `Jewish`, and `Japan` are retained. Language-community labels are not assertions about every individual in that community. There are 3,796 Western and 2,996 non-Western records according to the supplied split metadata.

## Evaluation

Emotion prediction is evaluated by accuracy against the culture-level majority labels, reported for English, Chinese, Arabic, and overall (Table 2). Explanation generation is evaluated by emotion alignment on a five-point scale using Claude Sonnet 5 and GLM-4.5V as separate judges (Table 6). Western/non-Western accuracy is the supplementary regional analysis.

## Citation

If you use the ArtECulture dataset, knowledge base, or code in your research, please cite our paper:

```bibtex
@misc{chen2026arteculture,
  title         = {ArtECulture: Benchmarking Culture-Conditioned Visual Emotion Understanding in Multimodal Large Language Models},
  author        = {Xiaolin Chen and Xuemeng Song and Wenhao Shi and Xianjing Han and Mong-Li Lee and Wynne Hsu},
  year          = {2026},
  eprint        = {2608.03358},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CL},
  url           = {https://arxiv.org/abs/2608.03358}
}
```
