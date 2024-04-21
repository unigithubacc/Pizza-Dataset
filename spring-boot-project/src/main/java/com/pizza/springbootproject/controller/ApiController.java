package com.pizza.springbootproject.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class ApiController {
    
    @GetMapping
    public String getApiData() {
        return "Hallo von der API!";
    }

}
