package com.project.service;

import java.util.ArrayList;
import java.util.List;

import org.chocosolver.solver.Model;
import org.chocosolver.solver.Solver;
import org.chocosolver.solver.variables.IntVar;
import org.jboss.logging.Logger;

import com.project.controller.contracts.CPUCoolerContract;
import com.project.controller.contracts.MotherboardContract;
import com.project.controller.contracts.PowerSupplyContract;
import com.project.converter.SocketMbToCpu;
import com.project.repository.CpuCoolerRepository;
import com.project.repository.CpuRepository;
import com.project.repository.PowerSupplyRepository;
import com.project.repository.ProductConfigRepository;
import com.project.repository.entity.Cpu;
import com.project.repository.entity.CpuCooler;
import com.project.repository.entity.ProductConfig;
import com.project.repository.entity.PowerSupply;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

@ApplicationScoped
public class PowerSupplyService
{
	@Inject
	ProductConfigRepository productConfigRepository;

    @Inject
    PowerSupplyRepository powerSupplyRepository;

	private ProductConfig getOrCreate(String sessionId)
	{
		ProductConfig productConfig = productConfigRepository.find("sessionId", sessionId).firstResult();
		if (productConfig == null)
		{
			productConfig = new ProductConfig();
			productConfig.sessionId = sessionId;
			productConfigRepository.persist(productConfig);
		}
		return productConfig;
	}

    public void addPowerSupply(String sessionId, PowerSupplyContract powerSupply) {
		ProductConfig productConfig = getOrCreate(sessionId);
		productConfig.powerSupply = powerSupply;

		productConfigRepository.persistOrUpdate(productConfig);
	}

    public List<PowerSupply> filterPowerSupply(String sessionId)
    {
        Model model = new Model("Power Supply Compatibility");
        List<PowerSupply> allCases = powerSupplyRepository.listAll();
        List<PowerSupply> compatibleCases = new ArrayList<>();

        ProductConfig productConfig = getOrCreate(sessionId);
        
        IntVar[] powerSupplyVars = new IntVar[allCases.size()];

        for (int i = 0; i < allCases.size(); i++) {
            powerSupplyVars[i] = model.intVar("PowerSupply_" + i, 0, 1);
        }

        Solver solver = model.getSolver();

        if (solver.solve()) {
            for (int i = 0; i < powerSupplyVars.length; i++) {
                if (powerSupplyVars[i].getValue() == 1) {
                    compatibleCases.add(allCases.get(i));
                }
            }
        }

        return compatibleCases;
    }
}