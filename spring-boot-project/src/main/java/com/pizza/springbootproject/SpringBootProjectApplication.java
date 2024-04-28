package com.pizza.springbootproject;

import org.springframework.boot.CommandLineRunner;
import org.springframework.context.ApplicationContext;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

import com.pizza.springbootproject.service.ManagerService;

@SpringBootApplication
public class SpringBootProjectApplication {

	public static void main(String[] args) {
		SpringApplication.run(SpringBootProjectApplication.class, args);
	}

	@Bean
	public CommandLineRunner CommandLineRunner(ApplicationContext ctx){
		return args -> {
			ManagerService service = ctx.getBean(ManagerService.class);
			service.fetchManager();
		};
	}

}
