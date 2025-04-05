package com.project.service;

import java.util.ArrayList;
import java.util.List;

import org.chocosolver.solver.Model;
import org.chocosolver.solver.Solver;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;

import com.project.converter.SocketMbToCpu;
import com.project.repository.CpuRepository;
import com.project.repository.MotherboardsRepository;
import com.project.repository.entity.Motherboard;
import com.project.repository.entity.Cpu;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import org.jboss.logging.Logger;


@ApplicationScoped
public class ProjectService {


    private final Logger logger = Logger.getLogger(ProjectService.class);

    @Inject
    MotherboardsRepository motherboardsRepository;

    @Inject 
    CpuRepository cpuRepository;

    // public List<MotherboardContract> filterMotherboard(String sessionId)
    // {
    //     return motherboardsRepository.listAll().stream().map();
    // }

    @Inject
    SocketMbToCpu mbCpuConverter;



    public List<Motherboard> filterMotherboard(String sessionId) {
        
        Model model = new Model("Motherboard Compatibility Check");
        // List<MotherboardContract> compatibleMotherboards = new ArrayList<>();
        List<Motherboard> allMotherboards = motherboardsRepository.listAll();
        List<Motherboard> compatibleMotherboards = new ArrayList<>();

        Cpu cpu = cpuRepository.findAll().firstResult();

        logger.info("CPU: " + cpu.name);


        IntVar[] motherboardVars = new IntVar[allMotherboards.size()];
        logger.info("Cpu: " + cpu.microarchitecture);

        for (int i = 0; i < allMotherboards.size(); i++) {
            
            if (cpu != null)
            {

                Motherboard mb = allMotherboards.get(i);
                
                Boolean isCompatible = mbCpuConverter.socketArchitectureMap.get(mb.socketCpu).contains(cpu.microarchitecture);
                
                motherboardVars[i] = model.intVar("mb_" + i, isCompatible ? 1 : 0);
            }
        }
        
        Solver solver = model.getSolver();

        if (solver.solve()) {
            for (int i = 0; i < motherboardVars.length; i++) {
                if (motherboardVars[i].getValue() == 1) {
                    compatibleMotherboards.add(allMotherboards.get(i));
                }
            }
        }

        return compatibleMotherboards;
    }
}

        // String supportedMemoryType = cpu.getMicroarchitecture().contains("Zen 5") ? "AM5" : "AM4";
        // System.out.println("Supported Memory Type: " + supportedMemoryType);
    
        // BoolVar[] motherboardVars = new BoolVar[allMotherboards.size()];
    
        // for (int i = 0; i < allMotherboards.size(); i++) {
        //     MotherboardContract mb = allMotherboards.get(i);
        //     motherboardVars[i] = model.boolVar(String.valueOf(i));

        //     BoolVar socketCompatible = model.boolVar(mb.getSocketCpu().equals(supportedMemoryType));
        
        //     model.arithm(motherboardVars[i], "=", socketCompatible).post();
        // }
    
        // if (model.getSolver().solve()) {
        //     for (int i = 0; i < motherboardVars.length; i++) {
        //         if (motherboardVars[i].getValue() == 1) {
        //             compatibleMotherboards.add(allMotherboards.get(i));
        //         }
        //     }
        // }
    
        // System.out.println("Compatible Motherboards: " + compatibleMotherboards)
    


        // return compatibleMotherboards;