"""Adapt released metadata to the research scripts without changing labels."""
import argparse
import csv
import json
from pathlib import Path

CULTURES = {'en': 'english', 'zh': 'chinese', 'ar': 'arabic'}


def prepare(root, split, mode, image_root):
    rows = list(csv.DictReader((root / 'data/splits' / (split + '.csv')).open(encoding='utf-8', newline='')))
    annotations = {}
    if mode == 'sft':
        for code in CULTURES:
            with (root / 'data/explanations' / (code + '.jsonl')).open(encoding='utf-8') as stream:
                annotations[code] = {r['image_id']: r['explanations'] for r in map(json.loads, stream)}
    for row in rows:
        path = str(image_root / Path(row['image_path']).name) if image_root else row['image_path']
        common = {'image_id': row['image_id'], 'image_path': path, 'region': row['region_group'], 'split': split}
        if mode == 'concepts':
            yield {**common, 'culture_emotions': {culture: row[culture + '_emotion'] for culture in CULTURES.values()}}
        else:
            for code, culture in CULTURES.items():
                record = {**common, 'culture': culture, 'emotion': row[culture + '_emotion']}
                if mode == 'sft':
                    record['explanations'] = [a['text'] for a in annotations[code][row['image_id']]]
                yield record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--split', choices=['train', 'val', 'test'], required=True)
    parser.add_argument('--mode', choices=['evaluation', 'concepts', 'sft'], default='evaluation')
    parser.add_argument('--image-root', type=Path, help='Extracted Image directory; defaults to paths relative to repository root.')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.mode == 'sft' and args.split == 'test':
        parser.error('Use evaluation mode for test records; reference explanations are not model inputs.')
    records = list(prepare(args.root, args.split, args.mode, args.image_root))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8', newline='\n') as stream:
        for record in records:
            stream.write(json.dumps(record, ensure_ascii=False) + '\n')
    print(f'Wrote {len(records)} {args.mode} records to {args.output}')


if __name__ == '__main__':
    main()
