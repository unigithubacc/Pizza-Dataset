package com.pizza.springbootproject.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.pizza.springbootproject.dao.ManagerDao;

@Service
public class ManagerService {

    @Autowired
    private ManagerDao managerDao;

    public void fetchManager() {
        managerDao.displayStoreIDsFromDB();
        managerDao.displayTopSellingProducts();
    }
}
