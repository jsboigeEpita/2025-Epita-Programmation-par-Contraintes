package com.project.converter;

import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import jakarta.enterprise.context.ApplicationScoped;


@ApplicationScoped
public class SocketMbToCpu {

    public Map<String, List<String>> socketArchitectureMap;

    public SocketMbToCpu()
    {
        initializeSocketArchitectureMap();
    }

    private void initializeSocketArchitectureMap() {
        socketArchitectureMap = new HashMap<>();
        
        // Intel LGA Sockets
        socketArchitectureMap.put("LGA775", Arrays.asList("Core", "Wolfdale", "Yorkfield"));
        socketArchitectureMap.put("LGA1150", Arrays.asList("Haswell", "Haswell Refresh"));
        socketArchitectureMap.put("LGA1151", Arrays.asList("Skylake", "Kaby Lake", "Coffee Lake", "Coffee Lake Refresh"));
        socketArchitectureMap.put("LGA1155", Arrays.asList("Sandy Bridge", "Ivy Bridge"));
        socketArchitectureMap.put("LGA1156", Arrays.asList("Nehalem"));
        socketArchitectureMap.put("LGA1200", Arrays.asList("Comet Lake", "Rocket Lake"));
        socketArchitectureMap.put("LGA1366", Arrays.asList("Nehalem", "Westmere"));
        socketArchitectureMap.put("LGA1700", Arrays.asList("Alder Lake", "Raptor Lake", "Raptor Lake Refresh"));
        socketArchitectureMap.put("LGA1851", Arrays.asList("Arrow Lake"));
        socketArchitectureMap.put("LGA2011", Arrays.asList("Sandy Bridge-E"));
        socketArchitectureMap.put("LGA2011-3", Arrays.asList("Haswell-E", "Broadwell-E"));
        socketArchitectureMap.put("LGA2011-3 Narrow", Arrays.asList("Haswell-EP", "Broadwell-EP"));
        socketArchitectureMap.put("LGA2066", Arrays.asList("Skylake-X", "Cascade Lake-X"));
        socketArchitectureMap.put("2 x LGA1366", Arrays.asList("Nehalem", "Westmere"));
        socketArchitectureMap.put("2 x LGA2011", Arrays.asList("Sandy Bridge-E"));
        socketArchitectureMap.put("2 x LGA2011-3", Arrays.asList("Haswell-E", "Broadwell-E"));
        socketArchitectureMap.put("2 x LGA2011-3 Narrow", Arrays.asList("Haswell-EP", "Broadwell-EP"));
        
        // AMD Sockets
        socketArchitectureMap.put("AM1", Arrays.asList("Jaguar"));
        socketArchitectureMap.put("AM2", Arrays.asList("K10"));
        socketArchitectureMap.put("AM2+", Arrays.asList("K10"));
        socketArchitectureMap.put("AM2+/AM2", Arrays.asList("K10"));
        socketArchitectureMap.put("AM3", Arrays.asList("K10"));
        socketArchitectureMap.put("AM3+", Arrays.asList("Bulldozer", "Piledriver"));
        socketArchitectureMap.put("AM3+/AM3", Arrays.asList("Bulldozer", "Piledriver", "K10"));
        socketArchitectureMap.put("AM3/AM2+/AM2", Arrays.asList("K10"));
        socketArchitectureMap.put("AM3/AM2+", Arrays.asList("K10"));
        socketArchitectureMap.put("AM4", Arrays.asList("Zen", "Zen+", "Zen 2", "Zen 3"));
        socketArchitectureMap.put("AM5", Arrays.asList("Zen 4", "Zen 5"));
        socketArchitectureMap.put("FM1", Arrays.asList("Lynx"));
        socketArchitectureMap.put("FM2", Arrays.asList("Piledriver"));
        socketArchitectureMap.put("FM2+", Arrays.asList("Steamroller", "Excavator"));
        socketArchitectureMap.put("sTR4", Arrays.asList("Zen", "Zen+", "Zen 2"));
        socketArchitectureMap.put("sTRX4", Arrays.asList("Zen 2", "Zen 3"));
        socketArchitectureMap.put("2 x G34", Arrays.asList("Bulldozer", "Piledriver"));
        
        // Integrated CPUs
        socketArchitectureMap.put("Integrated Atom 230", Arrays.asList("Atom"));
        socketArchitectureMap.put("Integrated Atom 330", Arrays.asList("Atom"));
        socketArchitectureMap.put("Integrated Atom C2358", Arrays.asList("Atom"));
        socketArchitectureMap.put("Integrated Atom C2550", Arrays.asList("Atom"));
        socketArchitectureMap.put("Integrated Atom C2750", Arrays.asList("Atom"));
        socketArchitectureMap.put("Integrated Atom D410", Arrays.asList("Atom"));
        socketArchitectureMap.put("Integrated Atom D425", Arrays.asList("Atom"));
        socketArchitectureMap.put("Integrated Atom D510", Arrays.asList("Atom"));
        socketArchitectureMap.put("Integrated Atom D525", Arrays.asList("Atom"));
        socketArchitectureMap.put("Integrated Atom D2500", Arrays.asList("Atom"));
        socketArchitectureMap.put("Integrated Atom D2550", Arrays.asList("Atom"));
        socketArchitectureMap.put("Integrated Atom D2700", Arrays.asList("Atom"));
        socketArchitectureMap.put("Integrated Atom N550", Arrays.asList("Atom"));
        socketArchitectureMap.put("Integrated Celeron 847", Arrays.asList("Sandy Bridge"));
        socketArchitectureMap.put("Integrated Celeron 1037U", Arrays.asList("Ivy Bridge"));
        socketArchitectureMap.put("Integrated Celeron J1900", Arrays.asList("Bay Trail"));
        socketArchitectureMap.put("Integrated Celeron N3050", Arrays.asList("Braswell"));
        socketArchitectureMap.put("Integrated Celeron N3150", Arrays.asList("Braswell"));
        socketArchitectureMap.put("Integrated Pentium J3710", Arrays.asList("Braswell"));
        socketArchitectureMap.put("Integrated Pentium N3700", Arrays.asList("Braswell"));
        socketArchitectureMap.put("Integrated Xeon D-1520", Arrays.asList("Broadwell"));
        socketArchitectureMap.put("Integrated Xeon D-1521", Arrays.asList("Broadwell"));
        socketArchitectureMap.put("Integrated Xeon D-1537", Arrays.asList("Broadwell"));
        socketArchitectureMap.put("Integrated Xeon D-1541", Arrays.asList("Broadwell"));
        socketArchitectureMap.put("Integrated E-Series E-350", Arrays.asList("Bobcat"));
        socketArchitectureMap.put("Integrated E-Series E-450", Arrays.asList("Bobcat"));
        socketArchitectureMap.put("Integrated C-Series C-70", Arrays.asList("Bobcat"));
        socketArchitectureMap.put("Integrated A4-5000", Arrays.asList("Jaguar"));
        socketArchitectureMap.put("Integrated Athlon II X2 215", Arrays.asList("K10"));
    }
}