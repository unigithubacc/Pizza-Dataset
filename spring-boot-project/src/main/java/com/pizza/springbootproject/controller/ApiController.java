package com.pizza.springbootproject.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;

import com.pizza.springbootproject.dao.ManagerDao;

@RestController
@RequestMapping("/api")
public class ApiController {

    @GetMapping
    public String getApiData() {
        return "Hallo von der API!";
    }
    
    private static final Logger log = LoggerFactory.getLogger(ApiController.class);

    @Autowired
    private ManagerDao managerDao;

    @GetMapping(value = "/store-ids", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<?> getStoreIDs() {
        log.info("GET localhost:8080/store-ids -> getStoreIDs() is called");

        // Aufruf der Methode, um die Store-IDs abzurufen
        return ResponseEntity.ok(managerDao.getStoreIDsFromDB());
    }

}
