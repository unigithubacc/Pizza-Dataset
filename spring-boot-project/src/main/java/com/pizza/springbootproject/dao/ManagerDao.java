package com.pizza.springbootproject.dao;

import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

@Repository
public class ManagerDao {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    public void displayBestSellingProductsFromDB() {
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

}
