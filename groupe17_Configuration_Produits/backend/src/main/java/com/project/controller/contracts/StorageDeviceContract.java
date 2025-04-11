package com.project.controller.contracts;


public class StorageDeviceContract {
    private String manufacturer;
    private String name;
    private String interfaceType;
    private String formFactor;
    private String storageType;
    private String capacity;
    private String readSpeed;
    private String writeSpeed;
    private String price;

    public StorageDeviceContract() {
    }

    public StorageDeviceContract(String manufacturer, String name, String interfaceType, String formFactor,
            String storageType, String capacity, String readSpeed, String writeSpeed, String price) {
        this.manufacturer = manufacturer;
        this.name = name;
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

    public String getName() {
        return name;
    }

    public void setName(String modelName) {
        this.name = modelName;
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
