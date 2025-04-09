package com.project.service;

import java.util.ArrayList;
import java.util.List;

import org.chocosolver.solver.Model;
import org.chocosolver.solver.Solver;
import org.chocosolver.solver.variables.IntVar;

import com.project.controller.contracts.PowerSupplyContract;
import com.project.repository.PowerSupplyRepository;
import com.project.repository.ProductConfigRepository;
import com.project.repository.entity.PowerSupply;
import com.project.repository.entity.ProductConfig;

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
        List<PowerSupply> compatiblePowerSupplys = new ArrayList<>();

        System.out.println("All Cases: " + allCases.size());

        ProductConfig productConfig = getOrCreate(sessionId);
        int powerConsumption = productConfig.PowerConsumption;
        System.out.println("Power Consumption: " + powerConsumption);
        
        IntVar[] powerSupplyVars = new IntVar[allCases.size()];

        for (int i = 0; i < allCases.size(); i++) {
            Boolean isCompatible = true;
            PowerSupply powerSupply = allCases.get(i);

            int powerSupplyPower = 0;

            if (powerSupply.getWattage() != null)
            {
                powerSupplyPower = Integer.parseInt(powerSupply.getWattage().split(" ")[0]);
            }
            if (powerSupplyPower < powerConsumption) {
                isCompatible = false;
            }

            powerSupplyVars[i] = model.intVar("PowerSupply_" + i, isCompatible ? 1 : 0);
        }

        Solver solver = model.getSolver();

        if (solver.solve()) {
            for (int i = 0; i < powerSupplyVars.length; i++) {
                if (powerSupplyVars[i].getValue() == 1) {
                    compatiblePowerSupplys.add(allCases.get(i));
                }
            }
        }

        return compatiblePowerSupplys;
    }
}