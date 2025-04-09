package com.project.controller.contracts;

import com.fasterxml.jackson.annotation.JsonProperty;

public class StorageDeviceContract {
    private String manufacturer;
    private String modelName;
    private String interfaceType;
    private String formFactor;
    private String storageType;
    private String capacity;
    private String readSpeed;
    private String writeSpeed;
    private String price;

    public StorageDeviceContract() {
    }

    public StorageDeviceContract(String manufacturer, String modelName, String interfaceType, String formFactor,
            String storageType, String capacity, String readSpeed, String writeSpeed, String price) {
        this.manufacturer = manufacturer;
        this.modelName = modelName;
        this.interfaceType = interfaceType;
        this.formFactor = formFactor;
        this.storageType = storageType;
        this.capacity = capacity;
        this.readSpeed = readSpeed;
        this.writeSpeed = writeSpeed;
        this.price = price;
    }

    public String getManufacturer() {
        return manufacturer;
    }

    public void setManufacturer(String manufacturer) {
        this.manufacturer = manufacturer;
    }

    public String getModelName() {
        return modelName;
    }

    public void setModelName(String modelName) {
        this.modelName = modelName;
    }

    public String getInterfaceType() {
        return interfaceType;
    }

    public void setInterfaceType(String interfaceType) {
        this.interfaceType = interfaceType;
    }

    public String getFormFactor() {
        return formFactor;
    }

    public void setFormFactor(String formFactor) {
        this.formFactor = formFactor;
    }

    public String getStorageType() {
        return storageType;
    }

    public void setStorageType(String storageType) {
        this.storageType = storageType;
    }

    public String getCapacity() {
        return capacity;
    }

    public void setCapacity(String capacity) {
        this.capacity = capacity;
    }

    public String getReadSpeed() {
        return readSpeed;
    }

    public void setReadSpeed(String readSpeed) {
        this.readSpeed = readSpeed;
    }

    public String getWriteSpeed() {
        return writeSpeed;
    }

    public void setWriteSpeed(String writeSpeed) {
        this.writeSpeed = writeSpeed;
    }

    public String getPrice() {
        return price;
    }

    public void setPrice(String price) {
        this.price = price;
    }
}
