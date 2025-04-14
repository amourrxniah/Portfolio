export async function quickSort(array, container, speed, signal, low = 0, high = array.length - 1) {
    if (signal?.aborted) throw new DOMException('Aborted', 'AbortError');
    const bars = container.children;

    if (low < high) {
        const pi = await partition(array, container, low, high, speed, signal);
        await quickSort(array, container, speed, signal, low, pi - 1);
        await quickSort(array, container, speed, signal, pi + 1, high);
    }

    //apply sorted colour at the end of full sort
    if (low === 0 && high === array.length - 1) {
        for (let i = 0; i < bars.length; i++) {
            bars[i].style.background = 'var(--sorted)';
        }
    }
}  
async function partition(array, container, low, high, speed, signal) {
    const bars = container.children;
    let pivot = array[high];
    let i = low - 1;

    bars[high].style.background = 'var(--active)';

    for (let j = low; j < high; j++) {
        if (signal?.aborted) throw new DOMException('Aborted', 'AbortError');
        
        bars[j].style.background = 'var(--active)';
        await new Promise(res => setTimeout(res, speed));

        if (array[j] < pivot) {
            i++;
            [array[i], array[j]] = [array[j], array[i]];
            bars[i].style.height = `${array[i]}px`;
            bars[j].style.height = `${array[j]}px`;
        }
        bars[j].style.background = 'var(--bar)';
    }

    [array[i + 1], array[high]] = [array[high], array[i + 1]];
    bars[i + 1].style.height = `${array[i + 1]}px`;
    bars[high].style.height = `${array[high]}px`;
    return i + 1;
}

