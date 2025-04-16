import java.sql.*;
import java.util.*;

public class BookDAO {
    public void addBook(Book book) throws SQLException {
        String query = "INSERT INTO books (title, author, quantity) VALUES (?, ?, ?)";
        try (Connection connection = DatabaseConnection.getConnection();
             PreparedStatement stmt = connection.prepareStatement(query)) {
            stmt.setString(1, book.getTitle());
            stmt.setString(2, book.getAuthor());
            stmt.setInt(3, book.getQuantity());
            stmt.executeUpdate();
        }
    }

    public List<Book> getAllBooks() throws SQLException {
        List<Book> books = new ArrayList<>();
        String query = "SELECT * FROM books";
        try (Connection connection = DatabaseConnection.getConnection();
             Statement stmt = connection.createStatement();
             ResultSet rs = stmt.executeQuery(query)) {
            while (rs.next()) {
                Book book = new Book();
                book.setBookId(rs.getInt("book_id"));
                book.setTitle(rs.getString("title"));
                book.setAuthor(rs.getString("author"));
                book.setQuantity(rs.getInt("quantity"));
                books.add(book);
            }
        }
        return books;
    }

    //additional methods for update and delete operations
    public void updateBook(Book book) throws SQLException {
        String query = "UPDATE books SET title=?, author=?, quantity=? WHERE book_id=?";
        try (Connection connection = DatabaseConnection.getConnection();
             PreparedStatement stmt = connection.prepareStatement(query)) {
            stmt.setString(1, book.getTitle());
            stmt.setString(2, book.getAuthor());
            stmt.setInt(3, book.getQuantity());
            stmt.setInt(4, book.getBookId());
            stmt.executeUpdate();
        }   
    }

    public void deleteBook(int bookId) throws SQLException {
        String query = "DELETE FROM books WHERE book_id=?";
        try (Connection connection = DatabaseConnection.getConnection();
             PreparedStatement stmt = connection.prepareStatement(query)) {
            stmt.setInt(1, bookId);
            stmt.executeUpdate();
        }
    }
}