const imageDialog = document.createElement('dialog');
imageDialog.className = 'image-dialog';
imageDialog.setAttribute('aria-labelledby', 'image-title');
imageDialog.innerHTML = `
    <div class="dialog-header">
        <h2 id="image-title">Artist photo</h2>
        <button class="secondary close-image" type="button">Close</button>
    </div>
    <figure>
        <img alt="">
        <figcaption></figcaption>
    </figure>
`;
document.body.append(imageDialog);

let imageButton;
let previousOverflow;

function openImage(button) {
    const photo = button.parentElement.querySelector('.photo');
    const original = photo.querySelector('img');
    const enlarged = imageDialog.querySelector('img');
    enlarged.src = original.src;
    enlarged.alt = original.alt;
    imageDialog.querySelector('#image-title').textContent = original.alt;
    imageDialog.querySelector('figcaption').replaceChildren(
        ...[...photo.querySelector('figcaption').childNodes].map((node) => node.cloneNode(true))
    );
    imageButton = button;
    previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    imageDialog.showModal();
    imageDialog.querySelector('.close-image').focus();
}

for (const button of document.querySelectorAll('.enlarge-image')) {
    const original = button.parentElement.querySelector('.photo img');
    original.classList.add('enlarge-trigger');
    original.tabIndex = 0;
    original.setAttribute('role', 'button');
    original.setAttribute('aria-label', `Enlarge ${original.alt}`);
    button.addEventListener('click', () => openImage(button));
    original.addEventListener('click', () => openImage(button));
    original.addEventListener('keydown', (event) => {
        if (event.key !== 'Enter' && event.key !== ' ') return;
        event.preventDefault();
        openImage(button);
    });
}

imageDialog.querySelector('.close-image').addEventListener('click', () => imageDialog.close());
imageDialog.addEventListener('click', (event) => {
    const bounds = imageDialog.getBoundingClientRect();
    if (event.target === imageDialog && (
        event.clientX < bounds.left || event.clientX > bounds.right ||
        event.clientY < bounds.top || event.clientY > bounds.bottom
    )) imageDialog.close();
});
imageDialog.addEventListener('close', () => {
    document.body.style.overflow = previousOverflow;
    imageButton?.focus();
});

imageDialog.addEventListener('keydown', (event) => {
    if (event.key !== 'Tab') return;
    const controls = [...imageDialog.querySelectorAll('button, a[href]')];
    const first = controls[0];
    const last = controls[controls.length - 1];
    if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
    }
});
