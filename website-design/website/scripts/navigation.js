// Some parts of this code may be from Stack Overflow

const menuButton = document.querySelector('.mobile-menu');
const siteNav = document.querySelector('#site-nav');
const exploreToggle = document.querySelector('.explore-toggle');
const exploreMenu = document.querySelector('#explore-menu');

function closeMenu() {
    // Close the mobile menu after a link is clicked
    siteNav.classList.remove('open');
    menuButton.setAttribute('aria-expanded', 'false');
}

function closeExploreMenu(returnFocus = false) {
    // Hide the genre list and return to Explore if needed
    exploreMenu.hidden = true;
    exploreToggle.setAttribute('aria-expanded', 'false');
    if (returnFocus) exploreToggle.focus();
}

menuButton.addEventListener('click', () => {
    // Open and close the mobile menu
    const isOpen = siteNav.classList.toggle('open');
    menuButton.setAttribute('aria-expanded', String(isOpen));
});

exploreToggle.addEventListener('click', () => {
    // Show the genre links when Explore is clicked
    const opening = exploreMenu.hidden;
    exploreMenu.hidden = !opening;
    exploreToggle.setAttribute('aria-expanded', String(opening));
});

siteNav.addEventListener('click', (event) => {
    if (event.target.tagName === 'A') closeMenu();
});

document.addEventListener('click', (event) => {
    if (!event.target.closest('.nav-dropdown')) closeExploreMenu();
});

document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape') return;
    // Escape closes an open menu
    closeMenu();
    if (!exploreMenu.hidden) closeExploreMenu(true);
});
