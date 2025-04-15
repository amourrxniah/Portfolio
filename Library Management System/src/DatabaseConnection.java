import java.sql.Connection;
import java.sql.DriverManager;

public class DatabaseConnection {
    private static final String url = "jdbc:mysql://localhost:3306/library";
    private static final String user = "root";         
    private static final String password = "Bethebest_1";

    public static Connection getConnection() {
        try {
            Class.forName("com.mysql.cj.jdbc.Driver");
            return DriverManager.getConnection(url, user, password);
        } catch (Exception e) {
            System.out.println("Error connecting to the database.");
            e.printStackTrace();
            return null;
        }
    }
}
