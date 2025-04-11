package com.project.repository;

import com.project.repository.entity.Case;

import io.quarkus.mongodb.panache.PanacheMongoRepository;
import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class CaseRepository implements PanacheMongoRepository<Case> {
	
}

