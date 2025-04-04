package com.project.controller.contracts;

import com.fasterxml.jackson.annotation.JsonProperty;

public class MotherboardContract {
    private String name;
    private String price;

    @JsonProperty("Socket / CPU")
    private String socketCpu;

    @JsonProperty("Form Factor")
    private String formFactor;

    @JsonProperty("Memory Max")
    private String memoryMax;

    @JsonProperty("Memory Slots")
    private String memorySlots;
    private String color;
    
    @JsonProperty("Power Consumption")
    private int powerConsumption;

    public MotherboardContract() {
    }

    public MotherboardContract(String name, String price, String socketCpu, String formFactor, String memoryMax, String memorySlots, String color, int powerConsumption) {
        this.name = name;
        this.price = price;
        this.socketCpu = socketCpu;
        this.formFactor = formFactor;
        this.memoryMax = memoryMax;
        this.memorySlots = memorySlots;
        this.color = color;
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

    public String getSocketCpu() {
        return socketCpu;
    }

    public void setSocketCpu(String socketCpu) {
        this.socketCpu = socketCpu;
    }

    public String getFormFactor() {
        return formFactor;
    }

    public void setFormFactor(String formFactor) {
        this.formFactor = formFactor;
    }

    public String getMemoryMax() {
        return memoryMax;
    }

    public void setMemoryMax(String memoryMax) {
        this.memoryMax = memoryMax;
    }

    public String getMemorySlots() {
        return memorySlots;
    }

    public void setMemorySlots(String memorySlots) {
        this.memorySlots = memorySlots;
    }

    public String getColor() {
        return color;
    }

    public void setColor(String color) {
        this.color = color;
    }

    public int getPowerConsumption() {
        return powerConsumption;
    }

    public void setPowerConsumption(int powerConsumption) {
        this.powerConsumption = powerConsumption;
    }
}
