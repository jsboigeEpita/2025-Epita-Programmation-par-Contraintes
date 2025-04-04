package com.project.controller.contracts;

import com.fasterxml.jackson.annotation.JsonProperty;

public class PowerSupplyContract {
    private String name;
    private String price;
    private String type;

    @JsonProperty("Efficiency Rating")
    private String efficiencyRating;
    private String wattage;
    private String modular;
    private String color;

    public PowerSupplyContract() {
    }

    public PowerSupplyContract(String name, String price, String type, String efficiencyRating, String wattage, String modular, String color) {
        this.name = name;
        this.price = price;
        this.type = type;
        this.efficiencyRating = efficiencyRating;
        this.wattage = wattage;
        this.modular = modular;
        this.color = color;
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

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }

    public String getEfficiencyRating() {
        return efficiencyRating;
    }

    public void setEfficiencyRating(String efficiencyRating) {
        this.efficiencyRating = efficiencyRating;
    }

    public String getWattage() {
        return wattage;
    }

    public void setWattage(String wattage) {
        this.wattage = wattage;
    }

    public String getModular() {
        return modular;
    }

    public void setModular(String modular) {
        this.modular = modular;
    }

    public String getColor() {
        return color;
    }

    public void setColor(String color) {
        this.color = color;
    }
}
