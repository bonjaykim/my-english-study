"""Release a prepared lesson on its Seoul calendar date, idempotently."""
from datetime import datetime, date, timezone, timedelta
from pathlib import Path
import argparse
import json
from build import ROOT, validate, build

def publish(day):
    date.fromisoformat(day)
    destination = ROOT / 'data/business' / f'{day}.json'
    if destination.exists():
        validate(json.loads(destination.read_text(encoding='utf-8')))
        build()
        print(f'{day} is already published; skipped duplicate release')
        return
    source = ROOT / 'queue/business' / f'{day}.json'
    if not source.exists():
        raise SystemExit(f'No prepared lesson for {day}. Refill queue/business through ChatGPT. Existing lessons are preserved.')
    lesson = json.loads(source.read_text(encoding='utf-8'))
    if lesson['date'] != day:
        raise SystemExit('Queue date mismatch')
    validate(lesson)
    # All existing data must be valid before moving the queued lesson.
    for path in (ROOT / 'data/business').glob('*.json'):
        validate(json.loads(path.read_text(encoding='utf-8')))
    destination.parent.mkdir(parents=True, exist_ok=True)
    source.replace(destination)
    build()
    print(f'Published {day}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--date')
    # Contemporary Korea is UTC+09:00 year-round; no external tzdata needed.
    requested = parser.parse_args().date
    publish(requested or datetime.now(timezone(timedelta(hours=9))).date().isoformat())
