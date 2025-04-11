package com.project.repository;

import com.project.repository.entity.Motherboard;

import io.quarkus.mongodb.panache.PanacheMongoRepository;
import jakarta.enterprise.context.ApplicationScoped;


@ApplicationScoped
public class MotherboardsRepository implements PanacheMongoRepository<Motherboard> {
    
}
