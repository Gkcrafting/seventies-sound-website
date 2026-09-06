const menuButton = document.querySelector('.mobile-menu');
const siteNav = document.querySelector('#site-nav');
const exploreToggle = document.querySelector('.explore-toggle');
const exploreMenu = document.querySelector('#explore-menu');

function closeMenu() {
    siteNav.classList.remove('open');
    menuButton.setAttribute('aria-expanded', 'false');
}

function closeExploreMenu(returnFocus = false) {
    exploreMenu.hidden = true;
    exploreToggle.setAttribute('aria-expanded', 'false');
    if (returnFocus) exploreToggle.focus();
}

menuButton.addEventListener('click', () => {
    const isOpen = siteNav.classList.toggle('open');
    menuButton.setAttribute('aria-expanded', String(isOpen));
});

exploreToggle.addEventListener('click', () => {
    const opening = exploreMenu.hidden;
    exploreMenu.hidden = !opening;
    exploreToggle.setAttribute('aria-expanded', String(opening));
});

siteNav.addEventListener('click', (event) => {
    if (event.target.closest('a')) closeMenu();
});

document.addEventListener('click', (event) => {
    if (!event.target.closest('.nav-dropdown')) closeExploreMenu();
});

document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape') return;
    closeMenu();
    if (!exploreMenu.hidden) closeExploreMenu(true);
});
