package com.project.repository;

import com.project.repository.entity.VideoCard;

import io.quarkus.mongodb.panache.PanacheMongoRepository;
import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class VideoCardRepository implements PanacheMongoRepository<VideoCard> {
	
}