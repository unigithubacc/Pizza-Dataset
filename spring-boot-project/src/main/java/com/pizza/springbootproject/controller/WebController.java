package com.pizza.springbootproject.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.ui.Model;

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

    @GetMapping("store-ids")
    public String home(Model model) {
        log.info("GET localhost:8080/web/home -> home() is called");

        // Aufruf der Methode aus dem ApiController, um die Store-IDs abzurufen
        ResponseEntity<?> response = apiController.getStoreIDs();

        // Setze die Daten im Model, damit sie in der View verwendet werden können
        model.addAttribute("storeIDs", response.getBody());

        // Rückgabe des Namens der View, die die Daten anzeigen wird
        return "storelist";
    }    
}
