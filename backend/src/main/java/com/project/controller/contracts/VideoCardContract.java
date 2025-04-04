package com.project.controller.contracts;

import com.fasterxml.jackson.annotation.JsonProperty;

public class VideoCardContract {
    private String name;
    private String price;
    private String chipset;
    private String memory;

    @JsonProperty("Core Clock")
    private String coreClock;

    @JsonProperty("Boost Clock")
    private String boostClock;
    private String color;
    private String length;

    @JsonProperty("Power Consumption")
    private int powerConsumption;

    public VideoCardContract() {
    }

    public VideoCardContract(String name, String price, String chipset, String memory, String coreClock, String boostClock, String color, String length, int powerConsumption) {
        this.name = name;
        this.price = price;
        this.chipset = chipset;
        this.memory = memory;
        this.coreClock = coreClock;
        this.boostClock = boostClock;
        this.color = color;
        this.length = length;
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

    public String getChipset() {
        return chipset;
    }

    public void setChipset(String chipset) {
        this.chipset = chipset;
    }

    public String getMemory() {
        return memory;
    }

    public void setMemory(String memory) {
        this.memory = memory;
    }

    public String getCoreClock() {
        return coreClock;
    }

    public void setCoreClock(String coreClock) {
        this.coreClock = coreClock;
    }

    public String getBoostClock() {
        return boostClock;
    }

    public void setBoostClock(String boostClock) {
        this.boostClock = boostClock;
    }

    public String getColor() {
        return color;
    }

    public void setColor(String color) {
        this.color = color;
    }

    public String getLength() {
        return length;
    }

    public void setLength(String length) {
        this.length = length;
    }

    public int getPowerConsumption() {
        return powerConsumption;
    }

    public void setPowerConsumption(int powerConsumption) {
        this.powerConsumption = powerConsumption;
    }
}
