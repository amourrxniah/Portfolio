export async function bubbleSort(array, container, speed, signal) {
    const bars = container.children;
    for (let i = 0; i < array.length - 1; i++) {
        for (let j = 0; j < array.length - i - 1; j++) {
            if (signal?.aborted) throw new DOMException('Aborted', 'AbortError');

            bars[j].style.background = 'var(--active)';
            bars[j + 1].style.background = 'var(--active)';
            await new Promise(res => setTimeout(res, speed));

            if (array[j] > array[j + 1]) {
                [array[j], array[j + 1]] = [array[j + 1], array[j]];
                bars[j].style.height = `${array[j]}px`;
                bars[j + 1].style.height = `${array[j + 1]}px`;
            }

            bars[j].style.background = 'var(--bar)';
            bars[j + 1].style.background = 'var(--bar)';
        }
        bars[array.length - i - 1].style.background = 'var(--sorted)';
    }
    bars[0].style.background = 'var(--sorted)'; //last sorted
}