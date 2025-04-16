// LibraryGUI.java
import javax.swing.*;
import javax.swing.border.EmptyBorder;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.awt.event.*;
import java.sql.*;
import java.util.List;

public class LibraryGUI {
    private JFrame frame;
    private JTable table;
    private boolean isDarkMode = false;
    private DefaultTableModel tableModel;

    public LibraryGUI() {
        frame = new JFrame("📚 Library Management System");
        frame.setSize(800, 550);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setLayout(new BorderLayout(10, 10));

        JPanel topPanel = new JPanel(new BorderLayout());
        JButton btnToggleTheme = new JButton("🌙 Dark Mode");
        btnToggleTheme.addActionListener(e -> toggleDarkMode());

        topPanel.add(btnToggleTheme, BorderLayout.EAST);
        frame.add(topPanel, BorderLayout.NORTH);

        // Table Model
        tableModel = new DefaultTableModel(new String[]{"ID", "Title", "Author", "Quantity", "Edit", "Delete"}, 0);
        table = new JTable(tableModel) {
            public boolean isCellEditable(int row, int column) {
                return column == 4 || column == 5;
            }
        };

        table.getColumn("Edit").setCellRenderer(new ButtonRenderer("✏️"));
        table.getColumn("Delete").setCellRenderer(new ButtonRenderer("🗑️"));
        table.getColumn("Edit").setCellEditor(new ButtonEditor(new JCheckBox(), "edit"));
        table.getColumn("Delete").setCellEditor(new ButtonEditor(new JCheckBox(), "delete"));

        table.setRowHeight(35);
        JScrollPane scrollPane = new JScrollPane(table);
        frame.add(scrollPane, BorderLayout.CENTER);

        JButton btnAdd = new JButton("➕ Add Book");
        btnAdd.addActionListener(e -> showAddPopup());
        JPanel bottomPanel = new JPanel();
        bottomPanel.add(btnAdd);
        frame.add(bottomPanel, BorderLayout.SOUTH);

        refreshTable();
    }

    private void toggleDarkMode() {
        isDarkMode = !isDarkMode;
        UIManager.put("control", isDarkMode ? new Color(40, 40, 40) : UIManager.getColor("control"));
        UIManager.put("info", isDarkMode ? Color.DARK_GRAY : UIManager.getColor("info"));
        UIManager.put("nimbusBase", isDarkMode ? Color.DARK_GRAY : UIManager.getColor("nimbusBase"));
        UIManager.put("nimbusBlueGrey", isDarkMode ? new Color(50, 50, 50) : UIManager.getColor("nimbusBlueGrey"));
        UIManager.put("nimbusLightBackground", isDarkMode ? new Color(60, 60, 60) : Color.WHITE);
        SwingUtilities.updateComponentTreeUI(frame);
    }

    private void showAddPopup() {
        JTextField txtTitle = new JTextField();
        JTextField txtAuthor = new JTextField();
        JTextField txtQuantity = new JTextField();
        Object[] fields = {
                "Title:", txtTitle,
                "Author:", txtAuthor,
                "Quantity:", txtQuantity
        };

        int result = JOptionPane.showConfirmDialog(frame, fields, "Add New Book", JOptionPane.OK_CANCEL_OPTION);
        if (result == JOptionPane.OK_OPTION) {
            try {
                Book book = new Book();
                book.setTitle(txtTitle.getText().trim());
                book.setAuthor(txtAuthor.getText().trim());
                book.setQuantity(Integer.parseInt(txtQuantity.getText().trim()));
                new BookDAO().addBook(book);
                refreshTable();
                JOptionPane.showMessageDialog(frame, "✅ Book added!");
            } catch (Exception ex) {
                JOptionPane.showMessageDialog(frame, "Error: " + ex.getMessage());
            }
        }
    }

    private void refreshTable() {
        try {
            tableModel.setRowCount(0);
            List<Book> books = new BookDAO().getAllBooks();
            for (Book book : books) {
                tableModel.addRow(new Object[]{
                        book.getBookId(), book.getTitle(), book.getAuthor(), book.getQuantity(), "Edit", "Delete"
                });
            }
        } catch (Exception ex) {
            JOptionPane.showMessageDialog(frame, "Error loading books: " + ex.getMessage());
        }
    }

    private void showEditPopup(int row) {
        int bookId = (int) tableModel.getValueAt(row, 0);
        String currentTitle = (String) tableModel.getValueAt(row, 1);
        String currentAuthor = (String) tableModel.getValueAt(row, 2);
        int currentQuantity = (int) tableModel.getValueAt(row, 3);

        JTextField txtTitle = new JTextField(currentTitle);
        JTextField txtAuthor = new JTextField(currentAuthor);
        JTextField txtQuantity = new JTextField(String.valueOf(currentQuantity));

        Object[] fields = {
                "Title:", txtTitle,
                "Author:", txtAuthor,
                "Quantity:", txtQuantity
        };

        int result = JOptionPane.showConfirmDialog(frame, fields, "Edit Book", JOptionPane.OK_CANCEL_OPTION);
        if (result == JOptionPane.OK_OPTION) {
            try {
                Book book = new Book();
                book.setBookId(bookId);
                book.setTitle(txtTitle.getText().trim());
                book.setAuthor(txtAuthor.getText().trim());
                book.setQuantity(Integer.parseInt(txtQuantity.getText().trim()));
                new BookDAO().updateBook(book);
                refreshTable();
                JOptionPane.showMessageDialog(frame, "✅ Book updated!");
            } catch (Exception e) {
                JOptionPane.showMessageDialog(frame, "Update failed: " + e.getMessage());
            }
        }
    }

    private void confirmDelete(int row) {
        int bookId = (int) tableModel.getValueAt(row, 0);
        int confirm = JOptionPane.showConfirmDialog(frame, "Are you sure you want to delete this book?",
                "Delete Book", JOptionPane.YES_NO_OPTION);
        if (confirm == JOptionPane.YES_OPTION) {
            try {
                new BookDAO().deleteBook(bookId);
                refreshTable();
                JOptionPane.showMessageDialog(frame, "🗑️ Book deleted.");
            } catch (Exception e) {
                JOptionPane.showMessageDialog(frame, "Delete failed: " + e.getMessage());
            }
        }
    }

    public void show() {
        frame.setLocationRelativeTo(null);
        frame.setVisible(true);
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new LibraryGUI().show());
    }

    // Inner Renderer & Editor classes
    class ButtonRenderer extends JButton implements javax.swing.table.TableCellRenderer {
        public ButtonRenderer(String text) {
            setText(text);
            setOpaque(true);
        }

        public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected,
                                                       boolean hasFocus, int row, int column) {
            return this;
        }
    }

    class ButtonEditor extends DefaultCellEditor {
        private String action;
        private JButton button;
        private int row;

        public ButtonEditor(JCheckBox checkBox, String action) {
            super(checkBox);
            this.action = action;
            button = new JButton();
            button.setOpaque(true);
            button.addActionListener(e -> {
                if ("edit".equals(action)) {
                    showEditPopup(row);
                } else {
                    confirmDelete(row);
                }
            });
        }

        public Component getTableCellEditorComponent(JTable table, Object value, boolean isSelected, int row, int column) {
            this.row = row;
            button.setText("edit".equals(action) ? "✏️" : "🗑️");
            return button;
        }

        public Object getCellEditorValue() {
            return "";
        }
    }
}