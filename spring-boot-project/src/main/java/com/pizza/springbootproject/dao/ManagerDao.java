package com.pizza.springbootproject.dao;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

@Repository
public class ManagerDao {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    public void displayStoreIDsFromDB() {
        List<Map<String, Object>> result = this.jdbcTemplate
                .queryForList("SELECT storeID FROM pizza.stores WHERE state_abbr = 'CA'");
        for (Map<String, Object> row : result) {
            for (Map.Entry<String, Object> entry : row.entrySet()) {
                String columnName = entry.getKey();
                Object value = entry.getValue();
                System.out.println(columnName + ": " + value);
            }
        }
    }

    public List<String> getStoreIDsFromDB() {
        List<String> storeIDs = new ArrayList<>();
        List<Map<String, Object>> result = this.jdbcTemplate
                .queryForList("SELECT storeID FROM pizza.stores WHERE state_abbr = 'CA'");
        for (Map<String, Object> row : result) {
            for (Map.Entry<String, Object> entry : row.entrySet()) {
                Object value = entry.getValue();
                storeIDs.add(value.toString()); // Hinzufügen der Store-ID zur Liste
            }
        }
        return storeIDs;
    }

    public void displayTopSellingProducts() {
        List<Map<String, Object>> result = this.jdbcTemplate
                .queryForList("SELECT products.SKU, products.Name, SUM(orders.nItems) AS TotalSold " +
                        "FROM pizza.products " +
                        "INNER JOIN pizza.order_items ON products.SKU = order_items.SKU " +
                        "INNER JOIN pizza.orders ON order_items.orderID = orders.orderID " +
                        "GROUP BY products.SKU, products.Name " +
                        "ORDER BY TotalSold DESC " +
                        "LIMIT 5");
        System.out.println("\nDie meistverkauften Produkte:");
        for (Map<String, Object> row : result) {
            Object sku = row.get("SKU");
            Object name = row.get("Name");
            Object totalSold = row.get("TotalSold");
            System.out.println("SKU: " + sku + ", Name: " + name + ", TotalSold: " + totalSold);
        }

    }
}
