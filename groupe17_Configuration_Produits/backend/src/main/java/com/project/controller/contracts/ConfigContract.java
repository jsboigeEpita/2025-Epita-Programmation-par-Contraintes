package com.project.controller.contracts;


public class ConfigContract {

    private CaseContract pcCase;
    
    private CPUContract cpu;

    private CPUCoolerContract cpuCooler;

    private MemoryContract memory;
    
    private MotherboardContract motherboard;
    
    private PowerSupplyContract powerSupply;
    
    private VideoCardContract videoCard;

    private StorageDeviceContract storageDevice;

    public ConfigContract() {}

    public ConfigContract(CaseContract pcCase, CPUContract cpu, CPUCoolerContract cpuCooler, MemoryContract memory, MotherboardContract motherboard, PowerSupplyContract powerSupply, VideoCardContract videoCard, StorageDeviceContract storageDevice) {
        this.pcCase = pcCase;
        this.cpu = cpu;
        this.cpuCooler = cpuCooler;
        this.memory = memory;
        this.motherboard = motherboard;
        this.powerSupply = powerSupply;
        this.videoCard = videoCard;
        this.storageDevice = storageDevice;
    }

    public CaseContract getCase() {
        return pcCase;
    }

    public void setCase(CaseContract pcCase) {
        this.pcCase = pcCase;
    }

    public CPUContract getCpu() {
        return cpu;
    }

    public void setCpu(CPUContract cpu) {
        this.cpu = cpu;
    }

    public CPUCoolerContract getCpuCooler() {
        return cpuCooler;
    }

    public void setCpuCooler(CPUCoolerContract cpuCooler) {
        this.cpuCooler = cpuCooler;
    }

    public MemoryContract getMemory() {
        return memory;
    }

    public void setMemory(MemoryContract memory) {
        this.memory = memory;
    }

    public MotherboardContract getMotherboard() {
        return motherboard;
    }

    public void setMotherboard(MotherboardContract motherboard) {
        this.motherboard = motherboard;
    }

    public PowerSupplyContract getPowerSupply() {
        return powerSupply;
    }

    public void setPowerSupply(PowerSupplyContract powerSupply) {
        this.powerSupply = powerSupply;
    }

    public VideoCardContract getVideoCard() {
        return videoCard;
    }

    public void setVideoCard(VideoCardContract videoCard) {
        this.videoCard = videoCard;
    }

    public StorageDeviceContract getStorageDevice() {
        return storageDevice;
    }

    public void setStorageDevice(StorageDeviceContract storageDevice) {
        this.storageDevice = storageDevice;
    }
}
