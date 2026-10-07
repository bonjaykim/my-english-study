"""Create one assigned GitHub issue per published lesson, after Pages deployment."""
import argparse
from datetime import datetime, timezone, timedelta
import json
import os
from urllib.parse import quote
from urllib.request import Request, urlopen
from build import ROOT, filename, validate

def notification(day, site_url):
    lesson = json.loads((ROOT / 'data/business' / f'{day}.json').read_text(encoding='utf-8'))
    words = validate(lesson)
    link = site_url.rstrip('/') + '/business/' + quote(filename(lesson), safe='')
    marker = f'<!-- english-study:{day} -->'
    return {
        'title': f'{day} 영어 학습 · {lesson["title_ko"]}',
        'body': f'{marker}\n\n오늘의 Business English 학습 자료가 게시됐습니다.\n\n'
                f'**{lesson["subject"]}**\n\n{lesson["summary_ko"]}\n\n'
                f'[오늘의 대본 바로 열기]({link})\n\n'
                f'영문 {words:,}단어 · 약 {round(words / 120)}분 · 한국어 전체 번역 · 핵심 표현 {len(lesson["expressions"])}개',
    }, marker

def api(path, token, payload=None):
    request = Request('https://api.github.com' + path,
                      data=json.dumps(payload).encode() if payload is not None else None,
                      headers={'Authorization': f'Bearer {token}',
                               'Accept': 'application/vnd.github+json',
                               'X-GitHub-Api-Version': '2022-11-28',
                               'User-Agent': 'my-english-study',
                               'Content-Type': 'application/json'})
    with urlopen(request, timeout=30) as response:
        return json.load(response)

def send(day, site_url, repository, token, test_id=None):
    payload, marker = notification(day, site_url)
    if test_id:
        test_marker = f'<!-- english-study-test:{test_id} -->'
        payload['body'] = payload['body'].replace(marker, test_marker)
        payload['title'] = '[테스트 알림] ' + payload['title']
        marker = test_marker
    # Match the marker, including closed issues, so reruns never notify twice.
    page = 1
    while True:
        issues = api(f'/repos/{repository}/issues?state=all&per_page=100&page={page}', token)
        if any(marker in (issue.get('body') or '') for issue in issues):
            print(f'{day}: notification already exists; skipped')
            return
        if len(issues) < 100:
            break
        page += 1
    payload['assignees'] = [repository.split('/')[0]]
    result = api(f'/repos/{repository}/issues', token, payload)
    print(f'Created notification: {result["html_url"]}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', default=datetime.now(timezone(timedelta(hours=9))).date().isoformat())
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--test-id')
    args = parser.parse_args()
    site_url = os.environ.get('SITE_URL', 'https://bonjaykim.github.io/my-english-study/')
    if args.dry_run:
        print(json.dumps(notification(args.date, site_url)[0], ensure_ascii=False, indent=2))
    else:
        send(args.date, site_url, os.environ['GITHUB_REPOSITORY'], os.environ['GITHUB_TOKEN'], args.test_id)
