package com.pizza.springbootproject.security;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.web.SecurityFilterChain;

import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
@EnableWebSecurity
public class securityConfig implements WebMvcConfigurer{
    
    @Bean
    protected SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        // Die Cross-Site-Request-Forgery-Schutz wird deaktiviert
        http.csrf(csrf -> csrf.disable());
        return http.build();
    }

}