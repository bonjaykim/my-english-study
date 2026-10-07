Create exactly one original business English lesson as JSON, without markdown fences.
Use the requested date in Asia/Seoul. Read recent lesson subjects to avoid repetition.
Audience: Korean learner; mix B2 and C1 English, natural spoken meeting language.
The dialogue alone MUST have 2200-2800 English words (target 2400, roughly 20 minutes at 120 wpm).
Use 3-4 teams and 4-8 named participants. Every participant must speak.
Include five or more stages: attendance and introductions, agenda/background,
substantive discussion with clarification and disagreement, decisions/actions with owners
and deadlines, and closing with a concrete next meeting date/time/timezone.
Keep figures, decisions, deadlines and Korean translations internally consistent.
Vary sector, teams, stakes, negotiation style and meeting type daily.
Do not reuse earlier dialogue or pad the length with repetitive statements.
Give a full faithful Korean translation of EACH turn, not a summary.
Give 12-20 expressions occurring verbatim in the English dialogue, with Korean meaning,
usage explanation, a verbatim example, and a different practice sentence.
Schema:
{"date":"YYYY-MM-DD","category":"business","subject":"Safe English Title",
"title_ko":"한국어 제목","summary_ko":"회의 배경 한두 문장",
"participants":[{"name":"Name","team":"Team"}],
"sections":[{"title_en":"Attendance","title_ko":"참석자 확인",
"turns":[{"speaker":"Name","en":"Full spoken English turn","ko":"전체 한국어 번역"}]}],
"expressions":[{"phrase":"align on","meaning_ko":"합의하다","usage_ko":"쓰는 상황",
"example":"Exact dialogue sentence with align on.","practice":"New example."}]}
Subject must match [A-Za-z0-9][A-Za-z0-9 ,()&-]{0,100}.
