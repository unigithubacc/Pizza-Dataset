import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

public class DisplayStoreIDs {
    static final String DB_URL = "jdbc:mysql://localhost:3306/";
    static final String USER = "root";
    static final String PASS = "ProLab895+";

    public static void main(String[] args) {
        try (Connection conn = DriverManager.getConnection(DB_URL, USER, PASS);
                Statement stmt = conn.createStatement();) {
            String sql = "SELECT storeID FROM pizza.stores"; // SQL-Abfrage, um alle storeIDs abzurufen
            ResultSet rs = stmt.executeQuery(sql);
            System.out.println("alle storeIDs");

            while (rs.next()) {
                try {
                    int storeID = rs.getInt("storeID");
                    System.out.println("StoreID: " + storeID);
                } catch (SQLException ex) {
                    // Handle non-integer values gracefully
                    String storeID = rs.getString("storeID");
                    System.out.println("Non-integer value encountered storeID: " + storeID);
                }
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
