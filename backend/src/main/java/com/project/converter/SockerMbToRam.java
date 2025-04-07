package com.project.converter;

import java.util.HashMap;
import java.util.Map;

import jakarta.enterprise.context.ApplicationScoped;


@ApplicationScoped
public class SockerMbToRam {
	public Map<String, String> socketMemoryMap;

	public SockerMbToRam() {
        this.socketMemoryMap = new HashMap<>();
        initializeSocketMemoryMap();
    }

	private void initializeSocketMemoryMap() {
        // Sockets Intel
        socketMemoryMap.put("LGA1851", "DDR5");
        socketMemoryMap.put("LGA1700", "DDR5/DDR4");
        socketMemoryMap.put("LGA1200", "DDR4");
        socketMemoryMap.put("LGA1151", "DDR4");
        socketMemoryMap.put("LGA1150", "DDR4/DDR3");
        socketMemoryMap.put("LGA1156", "DDR3");
        socketMemoryMap.put("LGA1155", "DDR3");
        socketMemoryMap.put("LGA1366", "DDR3");
        socketMemoryMap.put("2 x LGA1366", "DDR3");
        socketMemoryMap.put("LGA2066", "DDR4");
        socketMemoryMap.put("LGA2011-3", "DDR4");
        socketMemoryMap.put("LGA2011-3 Narrow", "DDR4");
        socketMemoryMap.put("2 x LGA2011-3 Narrow", "DDR4");
        socketMemoryMap.put("2 x LGA2011-3", "DDR4");
        socketMemoryMap.put("LGA2011", "DDR3");
        socketMemoryMap.put("2 x LGA2011", "DDR3");
        socketMemoryMap.put("LGA775", "DDR3/DDR2");
        
        // Sockets AMD
        socketMemoryMap.put("AM5", "DDR5");
        socketMemoryMap.put("AM4", "DDR4");
        socketMemoryMap.put("AM3+", "DDR3");
        socketMemoryMap.put("AM3+/AM3", "DDR3");
        socketMemoryMap.put("AM3", "DDR3");
        socketMemoryMap.put("AM3/AM2+", "DDR3/DDR2");
        socketMemoryMap.put("AM3/AM2+/AM2", "DDR3/DDR2");
        socketMemoryMap.put("AM2+/AM2", "DDR2");
        socketMemoryMap.put("AM2", "DDR2");
        socketMemoryMap.put("AM1", "DDR3");
        socketMemoryMap.put("sTRX4", "DDR4");
        socketMemoryMap.put("sTR4", "DDR4");
        socketMemoryMap.put("FM2+", "DDR3");
        socketMemoryMap.put("FM2", "DDR3");
        socketMemoryMap.put("FM1", "DDR3");
        socketMemoryMap.put("2 x G34", "DDR3");
        
        // Processeurs intégrés Intel
        socketMemoryMap.put("Integrated Xeon D-1541", "DDR4");
        socketMemoryMap.put("Integrated Xeon D-1537", "DDR4");
        socketMemoryMap.put("Integrated Xeon D-1521", "DDR4");
        socketMemoryMap.put("Integrated Xeon D-1520", "DDR4");
        socketMemoryMap.put("Integrated Pentium N3700", "DDR3L");
        socketMemoryMap.put("Integrated Pentium J3710", "DDR3L");
        socketMemoryMap.put("Integrated Celeron N3050", "DDR3L");
        socketMemoryMap.put("Integrated Celeron N3150", "DDR3L");
        socketMemoryMap.put("Integrated Celeron J1900", "DDR3L");
        socketMemoryMap.put("Integrated Celeron 1037U", "DDR3L");
        socketMemoryMap.put("Integrated Celeron 847", "DDR3L");
        socketMemoryMap.put("Integrated Atom C2750", "DDR3");
        socketMemoryMap.put("Integrated Atom C2550", "DDR3");
        socketMemoryMap.put("Integrated Atom C2358", "DDR3");
        socketMemoryMap.put("Integrated Atom D2700", "DDR3");
        socketMemoryMap.put("Integrated Atom D2550", "DDR3");
        socketMemoryMap.put("Integrated Atom D2500", "DDR3");
        socketMemoryMap.put("Integrated Atom D525", "DDR3");
        socketMemoryMap.put("Integrated Atom D510", "DDR3");
        socketMemoryMap.put("Integrated Atom D425", "DDR3");
        socketMemoryMap.put("Integrated Atom D410", "DDR3");
        socketMemoryMap.put("Integrated Atom N550", "DDR3");
        socketMemoryMap.put("Integrated Atom 330", "DDR2");
        socketMemoryMap.put("Integrated Atom 230", "DDR2");
        
        // Processeurs intégrés AMD
        socketMemoryMap.put("Integrated A4-5000", "DDR3");
        socketMemoryMap.put("Integrated C-Series C-70", "DDR3");
        socketMemoryMap.put("Integrated E-Series E-450", "DDR3");
        socketMemoryMap.put("Integrated E-Series E-350", "DDR3");
        socketMemoryMap.put("Integrated Athlon II X2 215", "DDR3");
    }
}
