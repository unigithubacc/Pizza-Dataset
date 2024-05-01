package com.pizza.springbootproject.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
@RequestMapping("/web/")

public class WebController {
    
    private static final Logger log = LoggerFactory.getLogger(WebController.class);

    @Autowired
    private ApiController apiController;

    @GetMapping("home")
    public String home() {
        log.info("GET localhost:8080/web/home -> home() is called");

        return "index";
    }
}
