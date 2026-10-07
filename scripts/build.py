"""Validate canonical lessons and build a static site without external dependencies."""
from pathlib import Path
from datetime import date
from html import escape
from urllib.parse import quote
import argparse
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]

def validate(lesson):
    date.fromisoformat(lesson['date'])
    assert lesson['category'] == 'business', 'Unsupported category'
    assert re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9 ,()&-]{0,100}', lesson['subject']), 'Unsafe subject filename'
    assert all(isinstance(lesson[k], str) and lesson[k].strip() for k in ('title_ko', 'summary_ko'))
    people = {p['name']: p['team'] for p in lesson['participants']}
    assert len(people) == len(lesson['participants']), 'Duplicate participant'
    assert 3 <= len(set(people.values())) <= 4, 'Expected 3-4 teams'
    assert 4 <= len(people) <= 8, 'Expected 4-8 speakers'
    assert len(lesson['sections']) >= 5, 'Missing meeting stages'
    words = 0
    speakers = set()
    for section in lesson['sections']:
        assert section['title_en'] and section['title_ko'] and section['turns']
        for turn in section['turns']:
            assert turn['speaker'] in people, 'Unknown speaker'
            speakers.add(turn['speaker'])
            assert turn['en'].strip() and re.search(r'[가-힣]', turn['ko']), 'Missing bilingual dialogue'
            words += len(re.findall(r"\b[\w]+(?:['’-][\w]+)*\b", turn['en']))
    assert speakers == set(people), 'Silent participant'
    assert 2200 <= words <= 2800, f'Expected 2200-2800 English words; got {words}'
    assert 12 <= len(lesson['expressions']) <= 20, 'Expected 12-20 expressions'
    dialogue = ' '.join(t['en'] for s in lesson['sections'] for t in s['turns']).lower()
    for expression in lesson['expressions']:
        assert all(isinstance(expression[k], str) and expression[k].strip() for k in ('phrase', 'meaning_ko', 'usage_ko', 'example', 'practice'))
        assert expression['phrase'].lower() in dialogue, 'Expression absent from script'
    return words

def document(title, body, prefix='', search=False):
    home_current = ' aria-current="page"' if search and not prefix else ''
    business_current = ' aria-current="page"' if not home_current else ''
    return f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#07111f"><title>{escape(title)} · My English Study</title><link rel="stylesheet" href="{prefix}assets/style.css">{f'<script defer src="{prefix}assets/search.js"></script>' if search else ''}</head><body><header><a class="brand" href="{prefix}index.html"><span class="mark" aria-hidden="true">En</span><span><strong>My English Study</strong><small>매일 만나는 비즈니스 영어</small></span></a><nav class="primary-nav" aria-label="주요 메뉴"><a href="{prefix}index.html"{home_current}>학습 보관함</a><a href="{prefix}business/index.html"{business_current}>Business English</a></nav></header>{body}<footer>영문 대본 → 한국어 번역 → 핵심 표현 · 읽기 시간은 분당 120단어 기준의 추정치입니다.</footer></body></html>'''

def filename(lesson):
    return f"{lesson['date']} {lesson['subject']}.html"

def lesson_page(lesson, words):
    e = escape
    people = {p['name']: p['team'] for p in lesson['participants']}
    content = []
    for lang in ('en', 'ko'):
        sections = []
        n = 0
        for section in lesson['sections']:
            turns = []
            for turn in section['turns']:
                n += 1
                turns.append(f'<div class="turn" id="{lang}-{n}"><div class="speaker">{n:02d} · {e(turn["speaker"])}<small>{e(people[turn["speaker"]])}</small></div><p lang="{lang}">{e(turn[lang])}</p></div>')
            sections.append(f'<h3>{e(section["title_"+lang])}</h3>' + ''.join(turns))
        content.append(''.join(sections))
    expressions = ''.join(f'<article class="expression"><h3 lang="en">{e(x["phrase"])}</h3><p><strong>{e(x["meaning_ko"])}</strong> · {e(x["usage_ko"])}</p><p class="example" lang="en">{e(x["example"])}</p><p><span class="muted">응용 연습</span><br><span lang="en">{e(x["practice"])}</span></p></article>' for x in lesson['expressions'])
    tags = ''.join(f'<span class="tag">{e(p["name"])} · {e(p["team"])}</span>' for p in lesson['participants'])
    body = f'''<main class="lesson"><p class="eyebrow">BUSINESS / {e(lesson['date'])}</p><h1 lang="en">{e(lesson['subject'])}</h1><p>{e(lesson['title_ko'])}</p><div class="intro"><p>{e(lesson['summary_ko'])}</p><p class="muted">중급~고급 · {words:,}단어 · 약 {round(words/120)}분</p><div class="tags">{tags}</div></div><nav aria-label="학습 구간"><a href="#english">영문 대본</a><a href="#korean">한국어 번역</a><a href="#expressions">핵심 표현</a></nav><section id="english"><h2>01 / English script</h2>{content[0]}</section><section id="korean"><details open><summary>02 / 한국어 번역</summary>{content[1]}</details></section><section id="expressions"><h2>03 / Business expressions</h2>{expressions}</section></main>'''
    return document(lesson['subject'], body, '../')

def index_page(lessons, prefix=''):
    cards = []
    for lesson, words in lessons:
        haystack = ' '.join([lesson['subject'], lesson['title_ko'], lesson['summary_ko'], *[p['team'] for p in lesson['participants']], *[x['phrase'] for x in lesson['expressions']]]).lower()
        link = ('' if prefix else 'business/') + quote(filename(lesson))
        cards.append(f'''<article class="card" data-date="{lesson['date']}" data-search="{escape(haystack, quote=True)}"><div class="card-meta"><span class="badge">BUSINESS</span><small>{lesson['date']}</small></div><h2><a lang="en" href="{link}">{escape(lesson['subject'])}</a></h2><p>{escape(lesson['title_ko'])}</p><p class="muted">{escape(lesson['summary_ko'])}</p><div class="tags"><span class="tag">중급~고급</span><span class="tag">약 {round(words/120)}분</span><span class="tag">{len(lesson['expressions'])}개 표현</span></div></article>''')
    latest = lessons[0][0]['date'] if lessons else '게시 대기'
    expression_count = sum(len(x['expressions']) for x, _ in lessons)
    overview = f'''<section class="overview" aria-label="학습 자료 요약"><article class="metric"><small>누적 학습 자료</small><strong>{len(lessons):02d}</strong><span>다양한 팀의 회의 시나리오</span></article><article class="metric"><small>대본 읽기</small><strong>약 20분</strong><span>중급~고급 회의 영어</span></article><article class="metric"><small>핵심 표현</small><strong>{expression_count:02d}</strong><span>뜻 · 사용 상황 · 응용 예문</span></article></section>'''
    body = f'''<main><div class="page-heading"><div><p class="eyebrow">BUSINESS ENGLISH / DAILY PRACTICE</p><h1>오늘의 회의를 영어로.</h1><p class="muted">영문 대본을 먼저 읽고, 한국어 번역과 핵심 표현으로 복습하세요.</p></div><div class="edition">최근 학습 · {latest}</div></div>{overview}<div class="toolbar"><label for="search">주제·팀·표현 검색<input id="search" type="search" placeholder="예: launch, 고객, Engineering" autocomplete="off"></label><label for="date">학습 날짜<input id="date" type="date"></label></div><div class="section-head"><h2>학습 보관함</h2><p class="muted" id="count" role="status" aria-live="polite">{len(lessons)}개의 학습 자료</p></div><div class="cards">{''.join(cards)}</div><p class="empty" id="empty" {'hidden' if lessons else ''}>해당 조건의 학습 자료가 없습니다. 검색어나 날짜를 지워 주세요.</p></main>'''
    return document('Business English', body, prefix, search=True)

def build(output=None):
    target = Path(output).resolve() if output else ROOT
    lessons = []
    for path in sorted((ROOT / 'data/business').glob('*.json'), reverse=True):
        lesson = json.loads(path.read_text(encoding='utf-8'))
        assert path.stem == lesson['date'], 'Source filename/date mismatch'
        lessons.append((lesson, validate(lesson)))
    # Validate every source before writing any public files.
    (target / 'business').mkdir(parents=True, exist_ok=True)
    if target != ROOT:
        shutil.copytree(ROOT / 'assets', target / 'assets', dirs_exist_ok=True)
    for lesson, words in lessons:
        (target / 'business' / filename(lesson)).write_text(lesson_page(lesson, words), encoding='utf-8')
    (target / 'index.html').write_text(index_page(lessons), encoding='utf-8')
    (target / 'business/index.html').write_text(index_page(lessons, '../'), encoding='utf-8')
    (target / '.nojekyll').touch()
    print(f'Built {len(lessons)} validated lesson(s) in {target}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output')
    build(parser.parse_args().output)
