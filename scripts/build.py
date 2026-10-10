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
TOPICS = {
    'strategy': ('전략·사업기획', 'Strategy', '새로운 시장과 사업의 방향을 정하는 회의'),
    'sales': ('영업·고객', 'Sales & customers', '고객 요구를 듣고 제안과 계약 범위를 조율'),
    'finance': ('재무·예산', 'Finance', '예산과 투자, 성과를 근거로 판단하는 회의'),
    'people': ('인사·조직', 'People & culture', '근무 방식과 팀 운영에 관한 의견 조율'),
    'operations': ('운영·공급망', 'Operations', '공급, 물류, 서비스 운영 문제의 해결'),
    'marketing': ('마케팅·브랜드', 'Marketing', '캠페인과 메시지, 성과를 검토하는 회의'),
    'projects': ('프로젝트·제품', 'Projects & product', '일정, 제품 범위와 위험을 함께 점검'),
    'partnerships': ('파트너십·협의', 'Partnerships', '여러 이해관계자의 관점과 공동 목표를 조율'),
}

def topic_key(lesson):
    return lesson.get('topic', 'projects')

def validate(lesson):
    date.fromisoformat(lesson['date'])
    assert lesson['category'] == 'business', 'Unsupported category'
    assert topic_key(lesson) in TOPICS, 'Unknown business topic'
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
    turns = [t['en'] for s in lesson['sections'] for t in s['turns']]
    dialogue = ' '.join(turns).lower()
    for expression in lesson['expressions']:
        assert all(isinstance(expression[k], str) and expression[k].strip() for k in ('phrase', 'meaning_ko', 'usage_ko', 'example', 'practice'))
        assert expression['phrase'].lower() in dialogue, 'Expression absent from script'
        assert expression['phrase'].lower() in expression['example'].lower(), 'Example missing expression'
        assert any(expression['example'] in turn for turn in turns), 'Example must quote the dialogue'
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
    topic = topic_key(lesson)
    body = f'''<main class="lesson"><a class="back-link" href="../index.html?topic={topic}">← {e(TOPICS[topic][0])} 학습 목록</a><p class="eyebrow">BUSINESS / {e(lesson['date'])} / {e(TOPICS[topic][1])}</p><h1 lang="en">{e(lesson['subject'])}</h1><p>{e(lesson['title_ko'])}</p><div class="intro"><p>{e(lesson['summary_ko'])}</p><p class="muted">가상의 비즈니스 회의 · 중급~고급 · {words:,}단어 · 약 {round(words/120)}분</p><div class="tags">{tags}</div></div><nav aria-label="학습 구간"><a href="#english">영문 대본</a><a href="#korean">한국어 번역</a><a href="#expressions">핵심 표현</a></nav><section id="english"><h2>01 / English script</h2>{content[0]}</section><section id="korean"><details open><summary>02 / 한국어 번역</summary>{content[1]}</details></section><section id="expressions"><h2>03 / Business expressions</h2>{expressions}</section></main>'''
    return document(lesson['subject'], body, '../')

def index_page(lessons, prefix=''):
    cards = []
    counts = {key: sum(topic_key(lesson) == key for lesson, _ in lessons) for key in TOPICS}
    for lesson, words in lessons:
        topic = topic_key(lesson)
        haystack = ' '.join([*TOPICS[topic][:2], lesson['subject'], lesson['title_ko'], lesson['summary_ko'], *[p['team'] for p in lesson['participants']], *[x['phrase'] for x in lesson['expressions']]]).lower()
        link = ('' if prefix else 'business/') + quote(filename(lesson))
        cards.append(f'''<article class="card" data-date="{lesson['date']}" data-topic="{topic}" data-search="{escape(haystack, quote=True)}"><div class="card-meta"><span class="topic-badge">{escape(TOPICS[topic][0])}</span><time datetime="{lesson['date']}">{lesson['date']}</time></div><h3><a href="{link}">{escape(lesson['title_ko'])}</a></h3><p class="english-title" lang="en">{escape(lesson['subject'])}</p><p class="muted">{escape(lesson['summary_ko'])}</p><div class="card-bottom"><span>약 {round(words/120)}분 · 표현 {len(lesson['expressions'])}개</span><a href="{link}" aria-label="{escape(lesson['title_ko'], quote=True)} 학습 시작">학습하기 ↗</a></div></article>''')
    latest = lessons[0][0]['date'] if lessons else '게시 대기'
    hero_lesson = ''
    if lessons:
        item, words = lessons[0]
        link = ('' if prefix else 'business/') + quote(filename(item))
        hero_lesson = f'''<aside class="featured"><div class="featured-top"><span class="live-dot"></span>최근 학습 <time>{latest}</time></div><small>{escape(TOPICS[topic_key(item)][0])}</small><h2>{escape(item['title_ko'])}</h2><p lang="en">{escape(item['subject'])}</p><div class="featured-footer"><span>{words:,}단어 · 약 {round(words/120)}분</span><a class="primary-button" href="{link}">학습 시작 ↗</a></div></aside>'''
    topic_buttons = ''.join(f'''<button type="button" class="topic-choice" data-filter-topic="{key}" aria-pressed="false"><span>{escape(label)}</span><small>{counts[key]:02d}</small><em lang="en">{escape(english)}</em></button>''' for key, (label, english, _) in TOPICS.items())
    months = sorted({lesson['date'][:7] for lesson, _ in lessons}, reverse=True)
    month_options = ''.join(f'<option value="{month}">{month[:4]}년 {int(month[5:])}월</option>' for month in months)
    body = f'''<main class="library"><section class="library-hero"><div><p class="eyebrow">YOUR DAILY MEETING ROOM</p><h1>매일 다른 회의,<br>더 자연스러운 영어.</h1><p class="muted">실무 주제를 골라 가상의 회의에 참여하세요.<br>영문 대본부터 한국어 번역, 핵심 표현까지 한 번에.</p><div class="library-shortcuts"><a href="#topic-heading">주제로 찾기 ↓</a><a href="#browse-heading">날짜로 찾기 ↓</a></div><div class="hero-stats"><span><strong>{len(lessons):02d}</strong> 학습 자료</span><span><strong>{sum(n > 0 for n in counts.values()):02d}</strong> 주제</span><span><strong>B2–C1</strong> 중급·고급</span></div></div>{hero_lesson}</section><section class="topic-section" aria-labelledby="topic-heading"><div class="section-head"><div><p class="eyebrow">01 / PICK A TOPIC</p><h2 id="topic-heading">어떤 회의를 연습할까요?</h2></div><button type="button" class="text-button" id="all-topics" aria-pressed="true">모든 주제 보기</button></div><div class="topic-grid">{topic_buttons}</div></section><section class="browse-section" aria-labelledby="browse-heading"><div class="section-head"><div><p class="eyebrow">02 / YOUR STUDY ARCHIVE</p><h2 id="browse-heading">날짜별 학습 보관함</h2></div><p class="muted" id="count" role="status" aria-live="polite">{len(lessons)}개의 학습 자료</p></div><div class="archive-layout"><aside class="date-panel"><div class="calendar-heading"><h3>학습 날짜</h3><label class="sr-only" for="month">학습 월</label><select id="month">{month_options}</select></div><div class="calendar-week" aria-hidden="true"><span>월</span><span>화</span><span>수</span><span>목</span><span>금</span><span>토</span><span>일</span></div><div id="calendar" class="calendar-grid" aria-label="게시된 학습 날짜"></div><p class="calendar-hint"><span class="live-dot"></span>점이 있는 날짜에 학습 자료가 있습니다.</p><label for="date">날짜 직접 선택<input id="date" type="date"></label><button type="button" id="all-dates" class="date-reset">모든 날짜 보기</button><div class="study-flow"><small>20분 학습 루틴</small><p><span>01</span> English script</p><p><span>02</span> 한국어 번역</p><p><span>03</span> Business expressions</p></div></aside><div class="archive-results"><div class="filter-bar"><label class="sr-only" for="search">제목·팀·표현 검색</label><input id="search" type="search" placeholder="제목, 팀, 영어 표현 검색" autocomplete="off"><label class="sr-only" for="sort">정렬</label><select id="sort"><option value="newest">최신순</option><option value="oldest">날짜순</option></select></div><div class="filter-summary"><span id="selection">모든 주제 · 모든 날짜</span><button type="button" class="text-button" id="clear-filters">선택 초기화</button></div><div class="cards">{''.join(cards)}</div><p class="empty" id="empty" {'hidden' if lessons else ''}>선택한 조건에 해당하는 자료가 없습니다. 다른 날짜나 주제를 선택해 주세요.</p></div></div></section></main>'''
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
