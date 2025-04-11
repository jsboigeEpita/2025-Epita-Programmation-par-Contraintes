package com.project.repository.entity;

import org.bson.types.ObjectId;

import com.project.controller.contracts.CPUContract;
import com.project.controller.contracts.CPUCoolerContract;
import com.project.controller.contracts.CaseContract;
import com.project.controller.contracts.MemoryContract;
import com.project.controller.contracts.MotherboardContract;
import com.project.controller.contracts.PowerSupplyContract;
import com.project.controller.contracts.StorageDeviceContract;
import com.project.controller.contracts.VideoCardContract;

import io.quarkus.mongodb.panache.PanacheMongoEntity;
import io.quarkus.mongodb.panache.common.MongoEntity;

@MongoEntity(collection = "product_config")
public class ProductConfig extends PanacheMongoEntity {

    public ObjectId id;
    public String sessionId;

    public CaseContract pcCase;
    
    public CPUContract cpu;

    public CPUCoolerContract cpuCooler;

    public MemoryContract memory;
    
    public MotherboardContract motherboard;
    
    public PowerSupplyContract powerSupply;
    
    public VideoCardContract videoCard;

    public StorageDeviceContract storageDevice;

    public int PowerConsumption;
    public float price;


    public ProductConfig() {}


    public ProductConfig(String sessionId, CaseContract pcCase, CPUContract cpu, CPUCoolerContract cpuCooler,
            MemoryContract memory, MotherboardContract motherboard, PowerSupplyContract powerSupply,
            VideoCardContract videoCard, StorageDeviceContract storageDevice) {
        this.sessionId = sessionId;
        this.pcCase = pcCase;
        this.cpu = cpu;
        this.cpuCooler = cpuCooler;
        this.memory = memory;
        this.motherboard = motherboard;
        this.powerSupply = powerSupply;
        this.videoCard = videoCard;
        this.storageDevice = storageDevice;
    }
}
