import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

public class DisplayBestSellingProducts {
    static final String DB_URL = "jdbc:mysql://localhost:3306/pizza";
    static final String USER = "root";
    static final String PASS = "ProLab895+";

    public static void main(String[] args) {
        try (Connection conn = DriverManager.getConnection(DB_URL, USER, PASS);
             Statement stmt = conn.createStatement();) {
            String sql = "SELECT products.SKU, products.Name, SUM(orders.nItems) AS TotalSold "+
                         "FROM pizza.products "+
                         "INNER JOIN pizza.order_items ON products.SKU = order_items.SKU "+
                         "INNER JOIN pizza.orders ON order_items.orderID = orders.orderID "+
                         "GROUP BY products.SKU, products.Name "+
                         "ORDER BY TotalSold DESC "+
                         "LIMIT 5 "; 
            
        
            ResultSet rs = stmt.executeQuery(sql);
            System.out.println("Die meistverkauften Produkte:");

            while (rs.next()) {
                String SKU = rs.getString("SKU");
                String name = rs.getString("Name");
                int totalSold = rs.getInt("TotalSold");
            
                System.out.println("SKU: " + SKU + ", Name: " + name +
                                   ", Gesamtmenge verkauft: " + totalSold);
            }
            
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
