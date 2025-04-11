package com.project.repository;

import com.project.repository.entity.Cpu;

import io.quarkus.mongodb.panache.PanacheMongoRepository;
import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class CpuRepository implements PanacheMongoRepository<Cpu> {    
}
