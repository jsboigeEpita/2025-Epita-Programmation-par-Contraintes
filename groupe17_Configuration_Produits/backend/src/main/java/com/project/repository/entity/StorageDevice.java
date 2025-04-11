package com.project.repository.entity;

import org.bson.codecs.pojo.annotations.BsonProperty;
import org.bson.types.ObjectId;

import io.quarkus.mongodb.panache.PanacheMongoEntity;
import io.quarkus.mongodb.panache.common.MongoEntity;

@MongoEntity(collection =  "storage_devices")
public class StorageDevice extends PanacheMongoEntity {
    public ObjectId id;

    @BsonProperty("Manufacturer")
    private String manufacturer;

    @BsonProperty("Model name")
    private String name;

    @BsonProperty("Interface")
    private String interfaceType;

    @BsonProperty("Form factor")
    private String formFactor;

    @BsonProperty("Storage type")
    private String storageType;

    @BsonProperty("Capacity")
    private String capacity;

    @BsonProperty("Read speed (MB/s)")
    private String readSpeed;

    @BsonProperty("Write speed (MB/s)")
    private String writeSpeed;

    @BsonProperty("Price (USD)")
    private String price;

    public StorageDevice() {
    }

    public StorageDevice(String manufacturer, String name, String interfaceType, String formFactor,
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

    public void setName(String name) {
        this.name = name;
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
