"""Expand one visual-concept record into three culture-conditioned records."""
import argparse
import json
from pathlib import Path
from common import iter_jsonl


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8', newline='\n') as stream:
        for record in iter_jsonl(args.input):
            for culture, emotion in record['culture_emotions'].items():
                expanded = {k: v for k, v in record.items() if k != 'culture_emotions'}
                expanded.update(culture=culture, emotion=emotion)
                stream.write(json.dumps(expanded, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    main()
