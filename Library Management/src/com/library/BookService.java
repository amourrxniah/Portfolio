package com.library;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;

public class BookService {

    private Connection connection;

    public BookService() throws SQLException {
        this.connection = DriverManager.getConnection("jdbc:mysql://localhost:3306/libraryManagement?useSSL=false&serverTimezone=UTC", "root", "password");
    }

    public List<Book> getAllBooks() throws SQLException {
        List<Book> books = new ArrayList<>();
        Statement statement = connection.createStatement();
        ResultSet resultSet = statement.executeQuery("SELECT * FROM books");

        while (resultSet.next()) {
            Book book = new Book(
                    resultSet.getInt("id"),
                    resultSet.getString("title"),
                    resultSet.getString("author"),
                    resultSet.getInt("quantity")
            );
            books.add(book);
        }
        return books;
    }

    public void addBook(Book book) throws SQLException {
        String query = "INSERT INTO books (title, author, quantity) VALUES (?, ?, ?)";
        PreparedStatement preparedStatement = connection.prepareStatement(query);
        preparedStatement.setString(1, book.getTitle());
        preparedStatement.setString(2, book.getAuthor());
        preparedStatement.setInt(3, book.getQuantity());
        preparedStatement.executeUpdate();
    }

    public void deleteBook(int id) throws SQLException {
        String query = "DELETE FROM books WHERE id = ?";
        PreparedStatement preparedStatement = connection.prepareStatement(query);
        preparedStatement.setInt(1, id);
        preparedStatement.executeUpdate();
    }
}