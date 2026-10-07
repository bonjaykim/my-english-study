"""Validate prepared content and report remaining dates."""
import json
from build import ROOT, validate

paths = sorted((ROOT / 'queue/business').glob('*.json'))
for path in paths:
    lesson = json.loads(path.read_text(encoding='utf-8'))
    assert path.stem == lesson['date'], 'Queue filename/date mismatch'
    words = validate(lesson)
    print(f'{lesson["date"]} | {words} words | {lesson["subject"]}')
print(f'{len(paths)} prepared lesson(s) remaining')
