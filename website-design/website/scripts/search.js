const searchForm = document.querySelector('form[role="search"]');
const searchInput = searchForm.elements.q;
const results = document.querySelector('#search-results');
const message = document.querySelector('#search-message');
const cards = [...document.querySelectorAll('.artist, .music-sample')];
const chips = [...document.querySelectorAll('[data-genre]')];

function normalise(text) {
    return text.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').trim();
}

function showResults() {
    const params = new URLSearchParams(window.location.search);
    const query = params.get('q');
    const genre = chips.some((chip) => chip.dataset.genre === params.get('genre'))
        ? params.get('genre') : 'all';
    searchInput.value = query || '';
    results.hidden = query === null && genre === 'all';
    const words = normalise(query || '').split(/\s+/).filter(Boolean);
    let count = 0;

    for (const chip of chips) {
        const selected = chip.dataset.genre === genre;
        chip.classList.toggle('selected', selected);
        chip.setAttribute('aria-pressed', String(selected));
    }

    for (const card of cards) {
        const text = normalise(card.textContent);
        const matchesGenre = genre === 'all' || card.dataset.genres.split(' ').includes(genre);
        const matches = matchesGenre && words.every((word) => text.includes(word));
        card.hidden = !matches;
        if (matches) count += 1;
        if (!matches) {
            card.querySelectorAll('audio').forEach((audio) => audio.pause());
            for (const player of card.querySelectorAll('.youtube-player')) {
                if (!player.querySelector('iframe')) continue;
                const button = document.createElement('button');
                button.type = 'button';
                button.className = 'secondary load-video';
                button.textContent = 'Play ' + player.dataset.title;
                player.replaceChildren(button);
            }
        }
    }

    for (const section of document.querySelectorAll('[data-track-section], #listening')) {
        section.hidden = ![...section.querySelectorAll('.music-sample')].some((card) => !card.hidden);
    }

    if (results.hidden) return;
    const genreName = chips.find((chip) => chip.dataset.genre === genre).textContent.trim();
    if (query !== null && !words.length) {
        message.textContent = 'Enter an artist or song name, or browse below.';
    } else if (count === 0) {
        message.textContent = 'No matches. Try another name or choose All music.';
    } else {
        const detail = words.length ? ` for "${query}"` : '';
        const category = genre === 'all' ? '' : ` in ${genreName}`;
        message.textContent = `${count} ${count === 1 ? 'result' : 'results'}${detail}${category}.`;
    }
}

function updateUrl(params) {
    const url = new URL(window.location.href);
    url.search = params.toString();
    url.hash = '';
    window.history.pushState(null, '', url);
    showResults();
}

searchForm.addEventListener('submit', (event) => {
    event.preventDefault();
    const params = new URLSearchParams(window.location.search);
    params.set('q', searchInput.value.trim());
    updateUrl(params);
    document.querySelector('#search-heading').focus();
});

for (const chip of chips) {
    chip.addEventListener('click', () => {
        const params = new URLSearchParams(window.location.search);
        if (chip.dataset.genre === 'all') params.delete('genre');
        else params.set('genre', chip.dataset.genre);
        updateUrl(params);
    });
}

window.addEventListener('popstate', showResults);
showResults();
