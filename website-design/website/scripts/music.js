// Some parts of this code may be from Stack Overflow

// This worked on localhost for me, but not on 127.0.0.1
if (window.location.hostname === '127.0.0.1') {
    const previewUrl = new URL(window.location.href);
    previewUrl.hostname = 'localhost';
    window.location.replace(previewUrl);
}

for (const player of document.querySelectorAll('.youtube-player')) {
    player.addEventListener('click', (event) => {
        if (!event.target.classList.contains('load-video')) return;

        // YouTube does not work when the page is opened as a file
        if (window.location.protocol === 'file:') {
            let notice = player.querySelector('.player-notice');
            if (!notice) {
                notice = document.createElement('p');
                notice.className = 'player-notice';
                notice.textContent = 'Open the local website preview to play this video here.';
                const link = document.createElement('a');
                link.href = 'http://localhost:5500/website-design/website/explore.html';
                link.textContent = 'Open website preview';
                notice.append(' ', link);
                player.append(notice);
            }
            return;
        }

        const frame = document.createElement('iframe');
        // Load the video only when the visitor clicks Play
        const params = new URLSearchParams({
            origin: window.location.origin,
            playsinline: '1',
            rel: '0',
            autoplay: '1',
        });
        frame.src = `https://www.youtube.com/embed/${player.dataset.video}?${params}`;
        frame.title = player.dataset.title;
        frame.allow = 'autoplay; encrypted-media; fullscreen; picture-in-picture';
        frame.allowFullscreen = true;
        frame.referrerPolicy = 'strict-origin-when-cross-origin';
        player.replaceChildren(frame);
        frame.focus();
    });
}
