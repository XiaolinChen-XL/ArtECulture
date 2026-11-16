"""Create one unlabeled SWIFT inference prompt per image and culture."""
import argparse
import json
from pathlib import Path
from common import iter_jsonl
from prompts import SFT_INSTRUCTIONS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8', newline='\n') as stream:
        for record in iter_jsonl(args.input):
            out = {'messages': [{'role': 'user', 'content': [
                {'type': 'image', 'image': record['image_path']},
                {'type': 'text', 'text': SFT_INSTRUCTIONS[record['culture']]},
            ]}]}
            stream.write(json.dumps(out, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    main()
