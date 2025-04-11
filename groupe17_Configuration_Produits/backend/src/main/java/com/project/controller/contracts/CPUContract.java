package com.project.controller.contracts;

import com.fasterxml.jackson.annotation.JsonProperty;

public class CPUContract {
    private String name;
    private String price;

    @JsonProperty("Core Count") 
    private String coreCount;

    @JsonProperty("Performance Core Clock") 
    private String performanceCoreClock;

    @JsonProperty("Performance Core Boost Clock") 
    private String performanceCoreBoostClock;

    private String microarchitecture;
    private String tdp;

    @JsonProperty("Integrated Graphics") 
    private String integratedGraphics;

    @JsonProperty("Power Consumption") 
    private int powerConsumption;

    public CPUContract() {
    }

    public CPUContract(String name, String price, String coreCount, String performanceCoreClock, String performanceCoreBoostClock, String microarchitecture, String tdp, String integratedGraphics, int powerConsumption) {
        this.name = name;
        this.price = price;
        this.coreCount = coreCount;
        this.performanceCoreClock = performanceCoreClock;
        this.performanceCoreBoostClock = performanceCoreBoostClock;
        this.microarchitecture = microarchitecture;
        this.tdp = tdp;
        this.integratedGraphics = integratedGraphics;
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

    public String getCoreCount() {
        return coreCount;
    }

    public void setCoreCount(String coreCount) {
        this.coreCount = coreCount;
    }

    public String getPerformanceCoreClock() {
        return performanceCoreClock;
    }

    public void setPerformanceCoreClock(String performanceCoreClock) {
        this.performanceCoreClock = performanceCoreClock;
    }

    public String getPerformanceCoreBoostClock() {
        return performanceCoreBoostClock;
    }

    public void setPerformanceCoreBoostClock(String performanceCoreBoostClock) {
        this.performanceCoreBoostClock = performanceCoreBoostClock;
    }

    public String getMicroarchitecture() {
        return microarchitecture;
    }

    public void setMicroarchitecture(String microarchitecture) {
        this.microarchitecture = microarchitecture;
    }

    public String getTdp() {
        return tdp;
    }

    public void setTdp(String tdp) {
        this.tdp = tdp;
    }

    public String getIntegratedGraphics() {
        return integratedGraphics;
    }

    public void setIntegratedGraphics(String integratedGraphics) {
        this.integratedGraphics = integratedGraphics;
    }

    public int getPowerConsumption() {
        return powerConsumption;
    }

    public void setPowerConsumption(int powerConsumption) {
        this.powerConsumption = powerConsumption;
    }
}
