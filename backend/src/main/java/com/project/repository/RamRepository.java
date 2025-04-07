package com.project.repository;

import com.project.repository.entity.Ram;

import io.quarkus.mongodb.panache.PanacheMongoRepository;
import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class RamRepository implements PanacheMongoRepository<Ram> {
	
}
