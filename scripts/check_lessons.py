"""Validate specific lesson files and report word counts (helper for authoring)."""
import json
import sys
from pathlib import Path
from build import validate

failed = False
for name in sys.argv[1:]:
    path = Path(name)
    try:
        lesson = json.loads(path.read_text(encoding='utf-8'))
        assert path.stem == lesson['date'], 'Filename/date mismatch'
        words = validate(lesson)
        print(f'OK   {lesson["date"]} {words:>5} words  {len(lesson["expressions"])} expr  {lesson["topic"]:<11} {lesson["subject"]}')
    except Exception as error:  # report every file, then fail
        failed = True
        print(f'FAIL {path.name}: {type(error).__name__}: {error}')
sys.exit(1 if failed else 0)
