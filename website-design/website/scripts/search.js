// Some parts of this code may be from Stack Overflow

const searchForm = document.querySelector('form[role="search"]');
const searchInput = searchForm.elements.q;
const results = document.querySelector('#search-results');
const message = document.querySelector('#search-message');
const cards = document.querySelectorAll('.artist, .music-sample');
const chips = document.querySelectorAll('[data-genre]');

function normalise(text) {
    return text.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').trim();
}

function showResults() {
    // Keep the search and genre in the URL after a refresh
    const params = new URLSearchParams(window.location.search);
    const query = params.get('q');
    const selectedGenre = params.get('genre');
    let genre = 'all';
    for (const chip of chips) {
        if (chip.dataset.genre === selectedGenre) {
            genre = selectedGenre;
            break;
        }
    }
    searchInput.value = query || '';
    results.hidden = query === null && genre === 'all';
    let words = [];
    if (query) words = normalise(query).split(/\s+/).filter(Boolean);
    let count = 0;

    for (const chip of chips) {
        // Show which genre is selected
        const selected = chip.dataset.genre === genre;
        chip.classList.toggle('selected', selected);
        chip.setAttribute('aria-pressed', String(selected));
    }

    for (const card of cards) {
        const text = normalise(card.textContent);
        const matchesGenre = genre === 'all' || card.dataset.genres.split(' ').includes(genre);
        let matchesSearch = true;
        for (const word of words) {
            if (!text.includes(word)) matchesSearch = false;
        }
        const matches = matchesGenre && matchesSearch;
        card.hidden = !matches;
        if (matches) count += 1;
        if (!matches) {
            // Stop videos and audio when a card is hidden
            for (const audio of card.querySelectorAll('audio')) audio.pause();
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
        let hasVisibleCard = false;
        const sectionCards = section.querySelectorAll('.music-sample');
        for (const card of sectionCards) {
            if (!card.hidden) {
                hasVisibleCard = true;
                break;
            }
        }
        section.hidden = !hasVisibleCard;
    }

    if (results.hidden) return;
    let genreName = '';
    for (const chip of chips) {
        if (chip.dataset.genre === genre) {
            genreName = chip.textContent.trim();
            break;
        }
    }
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
    // Change the URL without reloading the page
    const url = new URL(window.location.href);
    url.search = params.toString();
    url.hash = '';
    window.history.pushState(null, '', url);
    showResults();
}

searchForm.addEventListener('submit', (event) => {
    event.preventDefault();
    // Save the search in the URL so it can be shared
    const params = new URLSearchParams(window.location.search);
    params.set('q', searchInput.value.trim());
    updateUrl(params);
    document.querySelector('#search-heading').focus();
});

for (const chip of chips) {
    chip.addEventListener('click', () => {
        // Clear the search when a genre is clicked
        const params = new URLSearchParams(window.location.search);
        params.delete('q');
        if (chip.dataset.genre === 'all') params.delete('genre');
        else params.set('genre', chip.dataset.genre);
        updateUrl(params);
    });
}

window.addEventListener('popstate', showResults);
showResults();
