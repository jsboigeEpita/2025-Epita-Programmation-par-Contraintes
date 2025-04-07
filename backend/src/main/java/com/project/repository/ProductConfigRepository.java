package com.project.repository;

import com.project.repository.entity.Motherboard;
import com.project.repository.entity.ProductConfig;

import io.quarkus.mongodb.panache.PanacheMongoRepository;
import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class ProductConfigRepository implements PanacheMongoRepository<ProductConfig> {
}