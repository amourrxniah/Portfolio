export async function mergeSort(array, container, speed, signal, left = 0, right = array.length - 1) {
    if (signal?.aborted) throw new DOMException('Aborted', 'AbortError');
    
    if (left < right) {
        const mid = Math.floor((left + right) / 2);
        await mergeSort(array, container, speed, signal, left, mid);
        await mergeSort(array, container, speed, signal, mid + 1, right);
        await merge(array, container, left, mid, right, speed, signal);
    }

    //highlight sorted after entire recursion
    if (left === 0 && right === array.length - 1) {
        const bars = container.children;
        for (let i = 0; i < bars.length; i++) {
            bars[i].style.background = 'var(--sorted)';
        }
    }
}

async function merge(array, container, left, mid, right, speed, signal) {
    const bars = container.children;
    const n1 = mid - left + 1;
    const n2 = right - mid;

    const L = array.slice(left, mid + 1);
    const R = array.slice(mid + 1, right + 1);

    let i = 0, j = 0, k = left;

    while (i < n1 && j < n2) {
        if (signal?.aborted) throw new DOMException('Aborted', 'AbortError');
        
        await new Promise(res => setTimeout(res, speed));
        bars[k].style.background = 'var(--active)';

        if (L[i] <= R[j]) {
            array[k] = L[i];
            bars[k].style.height = `${L[i]}px`;
            i++;
        } else {
            array[k] = R[j];
            bars[k].style.height = `${L[j]}px`;
            j++;
        }
        bars[k].style.background = 'var(--bar)';
        k++;
    }

    while (i < n1) {
        if (signal?.aborted) throw new DOMException('Aborted', 'AbortError');
        array[k] = L[i];
        bars[k].style.height = `${L[i]}px`;
        bars[k].style.background = 'var(--bar)';
        await new Promise(res => setTimeout(res, speed));
        i++, k++;
    }

    while (j < n2) {
        if (signal?.aborted) throw new DOMException('Aborted', 'AbortError');
        array[k] = R[j];
        bars[k].style.height = `${R[j]}px`;
        await new Promise(res => setTimeout(res, speed));
        bars[k].style.background = 'var(--bar)';
        j++, k++;
    }
}