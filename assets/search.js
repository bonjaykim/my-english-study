const search = document.querySelector('#search');
const date = document.querySelector('#date');
const month = document.querySelector('#month');
const sort = document.querySelector('#sort');
const cards = [...document.querySelectorAll('.card[data-search]')];
const topics = [...document.querySelectorAll('[data-filter-topic]')];
const initialTopic = new URLSearchParams(location.search).get('topic');
let topic = topics.some(button => button.dataset.filterTopic === initialTopic) ? initialTopic : '';
function renderCalendar() {
  const calendar = document.querySelector('#calendar');
  calendar.replaceChildren();
  if (!month.value) return;
  const [year, number] = month.value.split('-').map(Number);
  const offset = (new Date(year, number - 1, 1).getDay() + 6) % 7;
  for (let i = 0; i < offset; i++) calendar.append(document.createElement('span'));
  const days = new Date(year, number, 0).getDate();
  for (let day = 1; day <= days; day++) {
    const value = `${month.value}-${String(day).padStart(2, '0')}`;
    const available = cards.filter(card => card.dataset.date === value && (!topic || card.dataset.topic === topic));
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = day;
    button.disabled = !available.length;
    button.className = available.length ? 'calendar-day available' : 'calendar-day';
    button.setAttribute('aria-label', `${year}년 ${number}월 ${day}일, 학습 자료 ${available.length}개`);
    button.setAttribute('aria-pressed', String(date.value === value));
    button.addEventListener('click', () => { date.value = date.value === value ? '' : value; filterLessons(); });
    calendar.append(button);
  }
}
function filterLessons() {
  const query = search.value.trim().toLocaleLowerCase();
  let count = 0;
  for (const card of cards) {
    const show = card.dataset.search.includes(query) && (!date.value || card.dataset.date === date.value) && (!topic || card.dataset.topic === topic);
    card.hidden = !show;
    count += Number(show);
  }
  topics.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.filterTopic === topic)));
  document.querySelector('#all-topics').setAttribute('aria-pressed', String(!topic));
  const label = topics.find(button => button.dataset.filterTopic === topic)?.querySelector('span').textContent || '모든 주제';
  document.querySelector('#selection').textContent = `${label} · ${date.value || '모든 날짜'}${query ? ` · “${search.value.trim()}”` : ''}`;
  document.querySelector('#count').textContent = `${count}개의 학습 자료`;
  document.querySelector('#empty').hidden = count > 0;
  renderCalendar();
}
topics.forEach(button => button.addEventListener('click', () => { topic = button.dataset.filterTopic; filterLessons(); }));
document.querySelector('#all-topics').addEventListener('click', () => { topic = ''; filterLessons(); });
document.querySelector('#all-dates').addEventListener('click', () => { date.value = ''; filterLessons(); });
document.querySelector('#clear-filters').addEventListener('click', () => { topic = ''; date.value = ''; search.value = ''; filterLessons(); });
search.addEventListener('input', filterLessons);
date.addEventListener('input', () => {
  const selectedMonth = date.value.slice(0, 7);
  if ([...month.options].some(option => option.value === selectedMonth)) month.value = selectedMonth;
  filterLessons();
});
month.addEventListener('change', () => { date.value = ''; filterLessons(); });
sort.addEventListener('change', () => {
  const ordered = [...cards].sort((a, b) => sort.value === 'oldest' ? a.dataset.date.localeCompare(b.dataset.date) : b.dataset.date.localeCompare(a.dataset.date));
  document.querySelector('.cards').append(...ordered);
});
filterLessons();
