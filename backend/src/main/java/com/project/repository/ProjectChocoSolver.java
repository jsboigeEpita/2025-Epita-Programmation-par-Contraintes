package com.project.repository;


import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Function;

import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;

import com.project.controller.contracts.CPUContract;
import com.project.controller.contracts.ConfigContract;
import com.project.controller.contracts.MotherboardContract;

public class ProjectChocoSolver<T> {

    private Model model;
    private List<Function<T, BoolVar>> functions;

    public ProjectChocoSolver() {
    }

    public ProjectChocoSolver(Model model, MotherboardContract product, ConfigContract configuration) {
        this.model = model;
        this.functions = new ArrayList<>();

        if (configuration.getCpu() != null) {
            
            Map<String, String> cpuToSocket = new HashMap<>();
            cpuToSocket.put("Zen 5", "AM5");
            cpuToSocket.put("Zen 4", "AM5");
            cpuToSocket.put("Zen 3", "AM4");
            cpuToSocket.put("Zen 2", "AM4");
            cpuToSocket.put("Zen+", "AM4");
            cpuToSocket.put("Zen", "AM4");
            cpuToSocket.put("Piledriver", "AM3+");
            cpuToSocket.put("Bulldozer", "AM3+");
            cpuToSocket.put("Raptor Lake", "LGA1700");
            cpuToSocket.put("Alder Lake", "LGA1700");
            cpuToSocket.put("Comet Lake", "LGA1200");
            cpuToSocket.put("Rocket Lake", "LGA1200");
            cpuToSocket.put("Skylake", "LGA1151");
            cpuToSocket.put("Coffee Lake", "LGA1151");
            cpuToSocket.put("Sandy Bridge", "LGA1155/LGA1150");
            cpuToSocket.put("Haswell", "LGA1155/LGA1150");

            CPUContract cpu = configuration.getCpu();
            String cpuSocket = cpuToSocket.get(cpu.getMicroarchitecture());
            for (String i : cpuSocket.split("/")) {
                BoolVar cpuBoolVar = model.boolVar(i);
                functions.add((T t) -> model.arithm(cpuBoolVar, "=", ((MotherboardContract) t).getSocketCpu()).reify());
            }
        }
    }
}
