import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.sql.*;

public class LibraryGUI {
    private JFrame frame;
    private JTextField txtTitle, txtAuthor, txtQuantity;
    private JButton btnAddBook;
    private JTable table;

    public LibraryGUI() {
        frame = new JFrame("Library Management System");
        frame.setSize(600, 400);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setLayout(new BorderLayout());

        JPanel panel = new JPanel();
        panel.setLayout(new GridLayout(4, 2));

        panel.add(new JLabel("Title:"));
        txtTitle = new JTextField();
        panel.add(txtTitle);

        panel.add(new JLabel("Author:"));
        txtAuthor = new JTextField();
        panel.add(txtAuthor);

        panel.add(new JLabel("Quantity:"));
        txtQuantity = new JTextField();
        panel.add(txtQuantity);

        btnAddBook = new JButton("Add Book");
        btnAddBook.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                try {
                    String title = txtTitle.getText();
                    String author = txtAuthor.getText();
                    int quantity = Integer.parseInt(txtQuantity.getText());
                    Book book = new Book();
                    book.setTitle(title);
                    book.setAuthor(author);
                    book.setQuantity(quantity);
                    BookDAO dao = new BookDAO();
                    dao.addBook(book);
                    JOptionPane.showMessageDialog(frame, "Book added successfully!");
                    refreshBookTable();
                } catch (Exception ex) {
                    JOptionPane.showMessageDialog(frame, "Error: " + ex.getMessage());
                }
            }
        });
        panel.add(btnAddBook);

        frame.add(panel, BorderLayout.NORTH);

        table = new JTable();  // Use a proper table model
        frame.add(new JScrollPane(table), BorderLayout.CENTER);
    }

    private void refreshBookTable() {
        try {
            BookDAO dao = new BookDAO();
            java.util.List<Book> books = dao.getAllBooks();

            //define column names
            String[] columnNames = {"ID", "Title", "Author", "Quantity"};

            //fill data into 2d array
            Object[][] data = new Object[books.size()][4];
            for (int i = 0; i < books.size(); i++) {
                Book book = books.get(i);
                data[i][0] = book.getBookId();
                data[i][1] = book.getTitle();
                data[i][2] = book.getAuthor();
                data[i][3] = book.getQuantity();
            }

            //set model to the table
            table.setModel(new javax.swing.table.DefaultTableModel(data, columnNames));

        } catch (SQLException e) {
            e.printStackTrace();
            JOptionPane.showMessageDialog(frame, "Error loading books: " + e.getMessage());
        }
    }

    public void show() {
        frame.setVisible(true);
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(new Runnable() {
            @Override
            public void run() {
                new LibraryGUI().show();
            }
        });
    }
}
