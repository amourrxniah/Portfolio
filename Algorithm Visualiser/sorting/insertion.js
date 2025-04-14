export async function insertionSort(array, container, speed, signal) {
    const bars = container.children;
    for (let i = 1; i < array.length; i++) {
        if (signal?.aborted) throw new DOMException('Aborted', 'AbortError');
        let key = array[i];
        let j = i - 1;

        bars[i].style.background = 'var(--active)';
        while (j >= 0 && array[j] > key) {
            if (signal?.aborted) throw new DOMException('Aborted', 'AbortError');
            array[j + 1] = array[j];
            bars[j + 1].style.height = `${array[j]}px`;
            j--;
            await new Promise(res => setTimeout(res, speed));
        }
        array[j + 1] = key;
        bars[j + 1].style.height = `${key}px`;
        bars[i].style.background = 'var(--bar)';
    }

    for (let i = 0; i < array.length; i++) {
        bars[i].style.background = 'var(--sorted)';
    }
}