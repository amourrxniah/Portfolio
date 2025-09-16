document.addEventListener("DOMContentLoaded", function() {
    //flashcard functionality
    const flashcardList = document.getElementById("flashcard-list");
    const createFlashcardButton = document.getElementById("create-flashcard");
    const createFlashcardBtn = document.getElementById("create-flashcard-btn");
    const flashcardCreator = document.getElementById("flashcard-creator");
    const closeModalBtns = document.querySelectorAll('.close-modal');

    //load flashcards from localStorage
    loadFlashcards();

    if (createFlashcardBtn) {
        createFlashcardBtn.addEventListener('click', function() {
            flashcardCreator.classList.add('active');
        });
    }
    
    if (closeModalBtns) {
        closeModalBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                flashcardCreator.classList.remove('active');
                document.getElementById('flashcard-viewer').classList.remove('active');
            });
        });
    }

    if (createFlashcardButton) {
        createFlashcardButton.addEventListener('click', function() {
            const title = document.getElementById("flashcard-title").value;
            const content = document.getElementById("flashcard-content").value;
            const category = document.getElementById("flashcard-category").value;

            if (title && content) {
                createFlashcard(title, content, category);
                //add to recent activity
                addRecentActivity(`Created flashcard in <strong>${category}</strong>`, 'create');
                //clear input fields
                document.getElementById('flashcard-title').value = '';
                document.getElementById('flashcard-content').value = '';
                flashcardCreator.classList.remove('active');
            } else {
                alert("Please enter both title and content for the flashcard.");
            }
        });
    }

    function createFlashcard(title, content, category) {
        const flashcard = document.createElement('div');
        flashcard.className = 'flashcard';
        flashcard.innerHTML = `
            <button class="delete-btn"><i class="fas fa-times"></i></button>
            <h3>${title}</h3>
            <p>${content}</p>
            <span class="category">Category: ${category}</span>
        `;

        //delete functionality
        const deleteBtn = flashcard.querySelector('.delete-btn');
        deleteBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            flashcard.remove();
            saveFlashcards();
            updateFlashcardCount();
        });

        //view flashcard on click
        flashcard.addEventListener('click', function() {
            viewFlashcard(title, content, category);
        });

        flashcardList.appendChild(flashcard);
        saveFlashcards();
        updateFlashcardCount();
    }

    function saveFlashcards() {
        const flashcards = [];
        document.querySelectorAll('.flashcard').forEach(card => {
            flashcards.push({
                title: card.querySelector('h3').textContent,
                content: card.querySelector('p').textContent,
                category: card.querySelector('.category').textContent.replace('Category: ', '')
            });
        });
        localStorage.setItem('flashcards', JSON.stringify(flashcards));
    }

    function loadFlashcards() {
        const savedFlashcards = JSON.parse(localStorage.getItem('flashcards')) || [];
        if (savedFlashcards.length > 0) {
            savedFlashcards.forEach(card => {
                createFlashcard(card.title, card.content, card.category);
            });
        } else {
            flashcardList.innerHTML = '<p>No flashcards yet. Create your first one!</p>';
        }
        updateFlashcardCount();
    }

    function updateFlashcardCount() {
        const totalCards = document.querySelectorAll('.flashcard').length;
        const totalCardsElement = document.getElementById('totalCards');
        if (totalCardsElement) {
            totalCardsElement.textContent = totalCards;
        }
    }

    //view single flashcard
    function viewFlashcard(title, content, category) {
        const flashcardViewer = document.getElementById('flashcard-viewer');
        document.getElementById('viewer-title').textContent = title;
        document.getElementById('viewer-content').textContent = content;
        document.getElementById('viewer-category').textContent = category;
        
        flashcardViewer.classList.add('active');
        
        //flip card functionality
        const flipCardBtn = document.getElementById('flip-card');
        const viewerCard = document.querySelector('.viewer-card');
        let isFlipped = false;
        
        if (flipCardBtn) {
            flipCardBtn.addEventListener('click', function() {
                isFlipped = !isFlipped;
                viewerCard.style.transform = isFlipped ? 'rotateY(180deg)' : 'rotateY(0)';
            });
        }
    }
});