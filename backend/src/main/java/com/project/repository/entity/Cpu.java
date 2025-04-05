package com.project.repository.entity;

import org.bson.codecs.pojo.annotations.BsonProperty;
import org.bson.types.ObjectId;

import io.quarkus.mongodb.panache.PanacheMongoEntity;
import io.quarkus.mongodb.panache.common.MongoEntity;

@MongoEntity(collection = "cpus")
public class Cpu extends PanacheMongoEntity {
    
    public ObjectId id;
    public String name;
    public String price;

    @BsonProperty("Core Count")
    public String coreCount;

    @BsonProperty("Performance Core Clock")
    public String performanceCoreClock;

    @BsonProperty("Performance Core Boost Clock")
    public String performanceCoreBoostClock;

    @BsonProperty("Microarchitecture")
    public String microarchitecture;

    @BsonProperty("TDP")
    public String tdp;

    @BsonProperty("Integrated Graphics")
    public String integratedGraphics;
    @BsonProperty("Power Consumption")
    public int powerConsumption;
}
