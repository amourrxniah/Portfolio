import { generateArray, renderBars } from './utils/helpers.js';
import { bubbleSort } from './sorting/bubble.js';
import { quickSort } from './sorting/quick.js';
import { mergeSort } from './sorting/merge.js';
import { insertionSort } from './sorting/insertion.js';

const modeSelect = document.getElementById('mode');
const algoSelect = document.getElementById('algorithm');
const startBtn = document.getElementById('startBtn');
const resetBtn = document.getElementById('resetBtn');
const speedSlider = document.getElementById('speedSlider');
const speedValue = document.getElementById('speedValue');
const visualiser = document.getElementById('visualiser');
const themeToggle = document.getElementById('themeToggle');
const currentAlgo = document.getElementById('currentAlgo');

let array = [];
let isSorting = false;
let controller = null;
let currentSignal = null;

//populate sorting or pathfinding options
function populateAlgorithms() {
    algoSelect.innerHTML = '';
    const options = modeSelect.value === 'sorting'
        ? ['Bubble Sort', 'Quick Sort', 'Merge Sort', 'Insertion Sort']
        : ['BFS', 'DFS', 'Dijkstra', 'A* Search'];

    options.forEach(name => {
        const opt = document.createElement('option');
        opt.value = name.toLowerCase().replace(/ /g, '');
        opt.textContent = name;
        algoSelect.appendChild(opt);
    });
}

//reset and optionally restart sorting
function resetVisualiser(shouldRestart = false) {
    if (controller) controller.abort(); //stop previous sort if running
    controller = new AbortController();
    currentSignal = controller.signal;
    isSorting = false;
    resetBtn.disabled = false;
    startBtn.disabled = false;

    if (modeSelect.value === 'sorting') {
        array = generateArray(50);
        renderBars(array, visualiser);
        currentAlgo.textContent = '';
        if (shouldRestart) {
            runSelectedSort(currentSignal); //restart sort
        }
    } else {
        visualiser.innerHTML = 'Pathfinding grid coming soon...';
    }
}

//update speed % display
speedSlider.addEventListener('input', () => {
    speedValue.textContent = `${speedSlider.value}%`;
});

//colour bars based on algorithm
function applySortColor() {
    const bars = visualiser.children;
    const algo = algoSelect.value;
    const colorMap = {
        bubblesort: 'var(--bar-bubble)',
        quicksort: 'var(--bar-quick)',
        mergesort: 'var(--bar-merge)',
        insertionsort: 'var(--bar-insertion)'
    };
    for (let bar of bars) {
        bar.style.background = colorMap[algo] || 'var(--bar)';
    }
}

//run chosen sort algorithm
async function runSelectedSort(signal) {
    const algo = algoSelect.value;
    const speed = Math.floor(300 - (speedSlider.value * 2.5)); //invert slider: 100 = fast, 1 = slow
    isSorting = true;
    resetBtn.disabled = true;
    startBtn.disabled = true;

    currentAlgo.textContent = `Running: ${algoSelect.options[algoSelect.selectedIndex].text}`;
    applySortColor(); //colour only during run

    try {
        const sortMap = {
            bubblesort: bubbleSort,
            quicksort: quickSort,
            mergesort: mergeSort,
            insertionsort: insertionSort,
        };

        const sortFunction = sortMap[algo];
        if (sortFunction) {
            await sortFunction(array, visualiser, speed, signal);
        } else {
            currentAlgo.textContent = 'Unknown algorithm';
        }
    } catch (e) {
        if (e.name === 'AbortError') {
            console.log('Sort cancelled.');
            return;
        }
        console.error('Sort failed:', e);
    }

    currentAlgo.textContent = `Finished: ${algoSelect.options[algoSelect.selectedIndex].text}`;
    isSorting = false;
    resetBtn.disabled = false;
    startBtn.disabled = false;
}

//event listeners
startBtn.addEventListener('click', async () => {
    if (isSorting || modeSelect.value !== 'sorting') {
        if (controller) controller.abort(); //cancel current
    }

    controller = new AbortController();
    currentSignal = controller.signal;
    renderBars(array, visualiser);
    applySortColor();
    await runSelectedSort(currentSignal);
});

resetBtn.addEventListener('click', () => {
    resetVisualiser(true); //restart current sort
});

modeSelect.addEventListener('change', () => {
    populateAlgorithms();
    resetVisualiser();
});

algoSelect.addEventListener('change', () => {
    resetVisualiser(); //reset and rerender with new colour
});

themeToggle.addEventListener('click', () => {
    document.body.classList.toggle('dark');
});

window.onload = () => {
    populateAlgorithms();
    resetVisualiser();
    speedValue.textContent = `${speedSlider.value}%`;
};