package com.project.repository;

import com.project.repository.entity.StorageDevice;

import io.quarkus.mongodb.panache.PanacheMongoRepository;
import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class StorageDeviceRepository implements PanacheMongoRepository<StorageDevice> {
	
}