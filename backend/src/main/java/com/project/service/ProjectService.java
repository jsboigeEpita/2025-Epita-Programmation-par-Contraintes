package com.project.service;

import java.util.ArrayList;
import java.util.List;

import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;

import com.project.controller.contracts.ConfigContract;
import com.project.controller.contracts.MotherboardContract;

import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class ProjectService {

    public List<MotherboardContract> filterMotherboard(List<MotherboardContract> allMotherboards, ConfigContract config) {
        Model model = new Model("Motherboard Compatibility Check");
        List<MotherboardContract> compatibleMotherboards = new ArrayList<>();
    
        String supportedMemoryType = cpu.getMicroarchitecture().contains("Zen 5") ? "AM5" : "AM4";
        System.out.println("Supported Memory Type: " + supportedMemoryType);
    
        BoolVar[] motherboardVars = new BoolVar[allMotherboards.size()];
    
        for (int i = 0; i < allMotherboards.size(); i++) {
            MotherboardContract mb = allMotherboards.get(i);
            motherboardVars[i] = model.boolVar(String.valueOf(i));

            BoolVar socketCompatible = model.boolVar(mb.getSocketCpu().equals(supportedMemoryType));
        
            model.arithm(motherboardVars[i], "=", socketCompatible).post();
        }
    
        if (model.getSolver().solve()) {
            for (int i = 0; i < motherboardVars.length; i++) {
                if (motherboardVars[i].getValue() == 1) {
                    compatibleMotherboards.add(allMotherboards.get(i));
                }
            }
        }
    
        return compatibleMotherboards;
    }
}