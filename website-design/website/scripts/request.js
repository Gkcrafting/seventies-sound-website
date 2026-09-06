// Some parts of this code may be from Stack Overflow

const form = document.querySelector('#request-form');
const emailLink = document.querySelector('#email-request');
const recipient = 'kilekwg25@foxford.coventry.sch.uk';
const cc = 'Kemi.Adeeko@castlephoenixtrust.org.uk';
const topic = document.querySelector('#topic');
const kind = document.querySelector('#kind');
const reason = document.querySelector('#reason');

function updateEmail() {
    // Make the email link from the form answers
    const subject = `Seventies Sound request: ${topic.value.trim()}`;
    const body = [
        `Artist, song or topic: ${topic.value.trim()}`,
        `Content type: ${kind.value}`,
        '',
        reason.value.trim(),
    ].join('\r\n');

    emailLink.href = `mailto:${recipient}?cc=${encodeURIComponent(cc)}&subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
}

form.addEventListener('input', () => {
    // Keep the email link up to date while typing
    topic.setCustomValidity('');
    updateEmail();
});

emailLink.addEventListener('click', (event) => {
    // Check the topic before opening the email app
    topic.setCustomValidity(topic.value.trim() ? '' : 'Enter an artist, song or topic.');
    if (!form.reportValidity()) {
        event.preventDefault();
        return;
    }
    updateEmail();
});

form.addEventListener('submit', (event) => {
    event.preventDefault();
    emailLink.click();
});

updateEmail();
