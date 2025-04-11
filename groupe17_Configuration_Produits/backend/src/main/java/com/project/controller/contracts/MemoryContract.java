package com.project.controller.contracts;

import com.fasterxml.jackson.annotation.JsonProperty;

public class MemoryContract {
    private String name;
    private String price;
    private String speed;
    private String modules;

    @JsonProperty("Price / GB")
    private String pricePerGB;
    private String color;

    @JsonProperty("First Word Latency")
    private String firstWordLatency;

    @JsonProperty("CAS Latency")
    private String casLatency;

    @JsonProperty("Power Consumption")
    private int powerConsumption;

    public MemoryContract() {
    }

    public MemoryContract(String name, String price, String speed, String modules, String pricePerGB, String color, String firstWordLatency, String casLatency, int powerConsumption) {
        this.name = name;
        this.price = price;
        this.speed = speed;
        this.modules = modules;
        this.pricePerGB = pricePerGB;
        this.color = color;
        this.firstWordLatency = firstWordLatency;
        this.casLatency = casLatency;
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

    public String getSpeed() {
        return speed;
    }

    public void setSpeed(String speed) {
        this.speed = speed;
    }

    public String getModules() {
        return modules;
    }

    public void setModules(String modules) {
        this.modules = modules;
    }

    public String getPricePerGB() {
        return pricePerGB;
    }

    public void setPricePerGB(String pricePerGB) {
        this.pricePerGB = pricePerGB;
    }

    public String getColor() {
        return color;
    }

    public void setColor(String color) {
        this.color = color;
    }

    public String getFirstWordLatency() {
        return firstWordLatency;
    }

    public void setFirstWordLatency(String firstWordLatency) {
        this.firstWordLatency = firstWordLatency;
    }

    public String getCasLatency() {
        return casLatency;
    }

    public void setCasLatency(String casLatency) {
        this.casLatency = casLatency;
    }

    public int getPowerConsumption() {
        return powerConsumption;
    }

    public void setPowerConsumption(int powerConsumption) {
        this.powerConsumption = powerConsumption;
    }
}
