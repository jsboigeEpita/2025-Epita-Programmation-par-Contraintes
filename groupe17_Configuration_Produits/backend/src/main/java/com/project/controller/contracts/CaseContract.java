package com.project.controller.contracts;

import com.fasterxml.jackson.annotation.JsonProperty;

public class CaseContract {
    private String name;
    private String price;
    private String type;
    private String color;

    @JsonProperty("Power Supply") 
    private String powerSupply;

    @JsonProperty("Side Panel")
    private String sidePanel;

    @JsonProperty("External Volume")
    private String externalVolume;

    @JsonProperty("Internal 3.5\" Bays") 
    private String internalBays;
    private String dimensions;

    public CaseContract() {
    }

    public CaseContract(String name, String price, String type, String color, String powerSupply, String sidePanel, String externalVolume, String internalBays, String dimensions) {
        this.name = name;
        this.price = price;
        this.type = type;
        this.color = color;
        this.powerSupply = powerSupply;
        this.sidePanel = sidePanel;
        this.externalVolume = externalVolume;
        this.internalBays = internalBays;
        this.dimensions = dimensions;
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

    public String getColor() {
        return color;
    }

    public void setColor(String color) {
        this.color = color;
    }

    public String getPowerSupply() {
        return powerSupply;
    }

    public void setPowerSupply(String powerSupply) {
        this.powerSupply = powerSupply;
    }

    public String getSidePanel() {
        return sidePanel;
    }

    public void setSidePanel(String sidePanel) {
        this.sidePanel = sidePanel;
    }

    public String getExternalVolume() {
        return externalVolume;
    }

    public void setExternalVolume(String externalVolume) {
        this.externalVolume = externalVolume;
    }

    public String getInternalBays() {
        return internalBays;
    }

    public void setInternalBays(String internalBays) {
        this.internalBays = internalBays;
    }

    public String getDimensions() {
        return dimensions;
    }

    public void setDimensions(String dimensions) {
        this.dimensions = dimensions;
    }
}
