package com.project.repository;

import com.project.repository.entity.PowerSupply;

import io.quarkus.mongodb.panache.PanacheMongoRepository;
import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class PowerSupplyRepository implements PanacheMongoRepository<PowerSupply> {
	
}