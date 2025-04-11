package com.project.repository;

import com.project.repository.entity.CpuCooler;

import io.quarkus.mongodb.panache.PanacheMongoRepository;
import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class CpuCoolerRepository implements PanacheMongoRepository<CpuCooler> {
	
}
