package com.pizza.springbootproject.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import com.pizza.springbootproject.dao.ManagerDao;

@Service
public class ManagerService {

    // Read the URL of the external API from properties file.
    @Value("${ManagerService.url}")
    String apiUrl;

    @Autowired
    private ManagerDao managerDao;

    public void fetchManager() {
        managerDao.displayBestSellingProductsFromDB();
    }
}
