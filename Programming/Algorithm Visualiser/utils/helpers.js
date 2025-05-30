export function generateArray(size = 50) {
    return Array.from({ length: size }, () => Math.floor(Math.random() * 200) + 10);
}
  
export function renderBars(array, container) {
    container.innerHTML = '';
    array.forEach(value => {
        const bar = document.createElement('div');
        bar.classList.add('bar');
        bar.style.width = `${value}px`;
        bar.style.height = '20px';
        bar.style.background = 'var(--bar)';
        container.appendChild(bar);
    });
}  