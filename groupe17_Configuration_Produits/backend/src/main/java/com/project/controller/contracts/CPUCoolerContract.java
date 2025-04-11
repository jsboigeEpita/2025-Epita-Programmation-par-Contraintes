package com.project.controller.contracts;

import com.fasterxml.jackson.annotation.JsonProperty;

public class CPUCoolerContract {
    private String name;
    private String price;

    @JsonProperty("Fan RPM")
    private String fanRPM;

    @JsonProperty("Noise Level")
    private String noiseLevel;
    private String color;

    @JsonProperty("Radiator Size")
    private String radiatorSize;

    @JsonProperty("Power Consumption")
    private int powerConsumption;

    public CPUCoolerContract() {
    }

    public CPUCoolerContract(String name, String price, String fanRPM, String noiseLevel, String color, String radiatorSize, int powerConsumption) {
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
