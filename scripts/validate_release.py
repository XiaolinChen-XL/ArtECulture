"""Offline structural validation; optionally verify the image archive and checksums."""
import argparse
import collections
import csv
import hashlib
import json
import tarfile
from pathlib import Path


def digest(stream):
    h = hashlib.sha256()
    while block := stream.read(4 * 1024 * 1024):
        h.update(block)
    return h.hexdigest()


def validate(root, archive=False, checksums=False):
    errors = []
    def check(condition, message):
        if not condition:
            errors.append(message)
    def csvrows(path):
        with (root / path).open(encoding='utf-8', newline='') as stream:
            return list(csv.DictReader(stream))
    rows = csvrows('data/metadata.csv')
    index = {r['image_id']: r for r in rows}
    check(len(rows) == len(index) == 6792, 'Metadata count or duplicate IDs')
    union = set()
    for split, count in [('train', 5434), ('val', 679), ('test', 679)]:
        subset = csvrows('data/splits/' + split + '.csv')
        ids = {r['image_id'] for r in subset}
        check(len(subset) == len(ids) == count, 'Invalid split count: ' + split)
        check(not union & ids, 'Image ID overlap: ' + split)
        check(all(r == index.get(r['image_id']) and r['split'] == split for r in subset), 'Split content mismatch: ' + split)
        union |= ids
    check(union == set(index), 'Split coverage mismatch')
    annotation_counts = {}
    for code, expected in [('en', 30932), ('zh', 31559), ('ar', 29571)]:
        with (root / 'data/explanations' / (code + '.jsonl')).open(encoding='utf-8') as stream:
            records = [json.loads(line) for line in stream]
        check(len(records) == len({r['image_id'] for r in records}) == 6792, 'Explanation count: ' + code)
        check({r['image_id'] for r in records} == set(index), 'Explanation coverage: ' + code)
        count = 0
        for record in records:
            row = index[record['image_id']]
            check(record['image_path'] == row['image_path'] and record['split'] == row['split'] and record['language'] == code, 'Explanation metadata mismatch')
            for annotation in record['explanations']:
                count += 1
                check(bool(annotation['text'].strip()), 'Empty explanation')
                check(not any(k.startswith('annotator_') or k == 'culture_from_filename' for k in annotation), 'Personal metadata retained')
        check(count == expected, 'Annotation count: ' + code)
        annotation_counts[code] = count
    all_kb = []
    for code, culture, expected in [('en', 'english', 2784), ('zh', 'chinese', 2902), ('ar', 'arabic', 2753)]:
        with (root / 'knowledge_base' / (code + '.jsonl')).open(encoding='utf-8') as stream:
            entries = [json.loads(line) for line in stream]
        check(len(entries) == expected, 'KB count: ' + code)
        for entry in entries:
            check(entry['culture'] == culture and bool(entry['rationales']), 'Invalid KB entry')
            dist = entry['emotion_distribution']
            check(abs(sum(dist.values()) - 1) < 1e-6 and all(0 <= v <= 1 for v in dist.values()), 'Invalid distribution')
            check(dist[entry['dominant_emotion']] == max(dist.values()), 'Invalid dominant emotion')
        all_kb.extend(entries)
    with (root / 'knowledge_base/all.jsonl').open(encoding='utf-8') as stream:
        check([json.loads(line) for line in stream] == all_kb, 'Combined KB mismatch')
    manifest = csvrows('data/image_manifest.csv')
    expected_files = {r['image_path']: r for r in manifest}
    check(len(manifest) == len(expected_files) == len(index), 'Image manifest count')
    check(set(expected_files) == {r['image_path'] for r in rows}, 'Image path coverage')
    if archive:
        seen = set()
        with tarfile.open(root / 'assets/ArtECulture_Image.tar.gz', 'r|gz') as tar:
            for member in tar:
                if member.isdir():
                    continue
                check(member.isfile(), 'Unexpected non-regular archive member: ' + member.name)
                if not member.isfile():
                    continue
                check(member.name not in seen and member.name in expected_files, 'Unexpected/duplicate image: ' + member.name)
                seen.add(member.name)
                entry = expected_files.get(member.name)
                if entry:
                    check(member.size == int(entry['size_bytes']) and digest(tar.extractfile(member)) == entry['sha256'], 'Image hash mismatch: ' + member.name)
        check(seen == set(expected_files), 'Archive coverage')
    if checksums:
        for line in (root / 'CHECKSUMS.sha256').read_text(encoding='utf-8').splitlines():
            expected, name = line.split('  ', 1)
            with (root / name).open('rb') as stream:
                check(digest(stream) == expected, 'Checksum mismatch: ' + name)
    return {'errors': errors, 'images': len(rows), 'annotations': annotation_counts}



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--archive', action='store_true')
    parser.add_argument('--checksums', action='store_true')
    args = parser.parse_args()
    result = validate(args.root, args.archive, args.checksums)
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(result['errors']))
