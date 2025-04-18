document.addEventListener("DOMContentLoaded", function() {
    const bookTableBody = document.querySelector("#bookTable tbody");
    const addBookForm = document.getElementById('addBookForm');
    const addBookModal = document.getElementById('addBookModal');
    const themeToggleBtn = document.getElementById('themeToggleBtn');

    function fetchBooks() {
        fetch('/api/books')
            .then(response => response.json())
            .then(data => {
                bookTableBody.innerHTML = '';
                data.forEach(book => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${book.id}</td>
                        <td>${book.title}</td>
                        <td>${book.author}</td>
                        <td>${book.quantity}</td>
                        <td>
                            <button class="edit" onclick="editBook(${book.id})">✏️</button>
                            <button class="delete" onclick="deleteBook(${book.id})">🗑️</button>
                        </td>
                    `;
                    bookTableBody.appendChild(row);
                });
        });
    }

    function addBook(event) {
        event.preventDefault();

        const title = document.getElementById('title').value;
        const author = document.getElementById('author').value;
        const quantity = document.getElementById('quantity').value;

        fetch('/api/books', {
            method: 'POST',
            body: JSON.stringify({
                title: title,
                author: author,
                quantity: quantity
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(() => fetchBooks());
    }

    function deleteBook(id) {
        fetch(`/api/books?id=${id}`, {
            method: 'DELETE'
        }).then(() => fetchBooks());
    }

    addBookForm.addEventListener('submit', addBook);

    document.getElementById('addBookBtn').addEventListener('click', () => {
        addBookModal.style.display = "block";
    });

    document.getElementById('themeToggleBtn').addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
    });
    fetchBooks();
});

function closeAddBookModal() {
    document.getElementById('addBookModal').style.display = "none";
}