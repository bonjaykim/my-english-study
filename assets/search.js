const search = document.querySelector('#search');
const date = document.querySelector('#date');
const cards = [...document.querySelectorAll('[data-search]')];
function filterLessons() {
  const query = search.value.trim().toLocaleLowerCase();
  let count = 0;
  for (const card of cards) {
    const show = card.dataset.search.includes(query) && (!date.value || card.dataset.date === date.value);
    card.hidden = !show;
    count += Number(show);
  }
  document.querySelector('#count').textContent = `${count}개의 학습 자료`;
  document.querySelector('#empty').hidden = count > 0;
}
search.addEventListener('input', filterLessons);
date.addEventListener('input', filterLessons);
filterLessons();
