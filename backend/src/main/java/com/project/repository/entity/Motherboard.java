package com.project.repository.entity;

import org.bson.codecs.pojo.annotations.BsonProperty;
import org.bson.types.ObjectId;

import io.quarkus.mongodb.panache.PanacheMongoEntity;
import io.quarkus.mongodb.panache.common.MongoEntity;

@MongoEntity(collection = "motherboards")
public class Motherboard extends PanacheMongoEntity {

    public ObjectId id;
    public String name;
    public String price;

    @BsonProperty("Socket / CPU")
    public String socketCpu;

    @BsonProperty("Form Factor")
    public String formFactor;
    @BsonProperty("Memory Max")
    public String maxMemory;
    @BsonProperty("Memory Slots")
    public String memorySlots;
    @BsonProperty("Color")
    public String color;
    @BsonProperty("Power Consumption")
    public int powerConsumption;

    // Constructors, getters, and setters can be added here if needed
    

    public Motherboard() {}
}
