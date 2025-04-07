package com.project.repository.entity;

import org.bson.codecs.pojo.annotations.BsonProperty;
import org.bson.types.ObjectId;

import com.fasterxml.jackson.annotation.JsonProperty;

import io.quarkus.mongodb.panache.PanacheMongoEntity;
import io.quarkus.mongodb.panache.common.MongoEntity;

@MongoEntity(collection = "cpu_coolers")
public class CpuCooler extends PanacheMongoEntity {
    
	private ObjectId id;
	private String name;
    private String price;
	@BsonProperty("Fan RPM")
    private String fanRPM;
	@BsonProperty("Noise Level")
    private String noiseLevel;
	@BsonProperty("Color")
    private String color;
	@BsonProperty("Radiator Size")
    private String radiatorSize;
	@BsonProperty("Power Consumption")
    private int powerConsumption;

    public CpuCooler() {}

    public CpuCooler(ObjectId id, String name, String price, String fanRPM, String noiseLevel, String color, String radiatorSize, int powerConsumption) {
        this.id = id;
		this.name = name;
        this.price = price;
        this.fanRPM = fanRPM;
        this.noiseLevel = noiseLevel;
        this.color = color;
        this.radiatorSize = radiatorSize;
        this.powerConsumption = powerConsumption;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getPrice() {
        return price;
    }

    public void setPrice(String price) {
        this.price = price;
    }

    public String getFanRPM() {
        return fanRPM;
    }

    public void setFanRPM(String fanRPM) {
        this.fanRPM = fanRPM;
    }

    public String getNoiseLevel() {
        return noiseLevel;
    }

    public void setNoiseLevel(String noiseLevel) {
        this.noiseLevel = noiseLevel;
    }

    public String getColor() {
        return color;
    }

    public void setColor(String color) {
        this.color = color;
    }

    public String getRadiatorSize() {
        return radiatorSize;
    }

    public void setRadiatorSize(String radiatorSize) {
        this.radiatorSize = radiatorSize;
    }

    public int getPowerConsumption() {
        return powerConsumption;
    }

    public void setPowerConsumption(int powerConsumption) {
        this.powerConsumption = powerConsumption;
    }
}
