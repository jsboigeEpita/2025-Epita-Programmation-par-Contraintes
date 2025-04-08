package com.project.service;

import java.util.ArrayList;
import java.util.List;

import org.chocosolver.solver.Model;
import org.chocosolver.solver.Solver;
import org.chocosolver.solver.variables.IntVar;
import org.jboss.logging.Logger;

import com.project.controller.contracts.CPUCoolerContract;
import com.project.controller.contracts.PowerSupplyContract;
import com.project.converter.SocketMbToCpu;
import com.project.repository.CpuCoolerRepository;
import com.project.repository.ProductConfigRepository;
import com.project.repository.entity.CpuCooler;
import com.project.repository.entity.ProductConfig;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

@ApplicationScoped
public class CPUCoolerService
{
	@Inject
	ProductConfigRepository productConfigRepository;

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

	public void addCpuCooler(String sessionId, CPUCoolerContract cpuCooler) {
		ProductConfig productConfig = getOrCreate(sessionId);
		if (productConfig.cpuCooler != null) {
			productConfig.PowerConsumption -=  productConfig.cpuCooler.getPowerConsumption();
			productConfig.price -= Float.parseFloat(productConfig.cpuCooler.getPrice().replace('$', ' ').trim());
		}
		productConfig.cpuCooler = cpuCooler;
		productConfig.PowerConsumption +=  productConfig.cpuCooler.getPowerConsumption();
		productConfig.price += Float.parseFloat(productConfig.cpuCooler.getPrice().replace('$', ' ').trim());

		productConfigRepository.persistOrUpdate(productConfig);
	}

	private static final Logger logger = Logger.getLogger(CPUCoolerService.class);


	@Inject
	SocketMbToCpu mbCpuConverter;
	
	@Inject
	CpuCoolerRepository cpuCoolerRepository;


	public List<CpuCooler> filterCpusCoolers(String sessionId)
	{

		logger.info("SessionId: " + sessionId);

		Model model = new Model("Cpu Compatibility");
		List<CpuCooler> allCpus = cpuCoolerRepository.listAll();
		List<CpuCooler> compatibleCpuCoolers = new ArrayList<>();

		ProductConfig productConfig = getOrCreate(sessionId);

		PowerSupplyContract powerSupplyContract = productConfig.powerSupply;


		IntVar[] cpuVars = new IntVar[allCpus.size()];
	
		int wattage = 0;
		if (powerSupplyContract != null)
		{
			wattage = Integer.parseInt(powerSupplyContract.getWattage().split(" ")[0]) - (productConfig.cpuCooler != null ? productConfig.cpuCooler.getPowerConsumption() : 0);
		}

		for (int i = 0; i < allCpus.size(); i++)
		{
			CpuCooler cpuCooler = allCpus.get(i);
			boolean isCompatible = true;

			if (isCompatible && powerSupplyContract != null)
			{
				isCompatible &= cpuCooler.getPowerConsumption() + productConfig.PowerConsumption <= wattage;
			}
			cpuVars[i] = model.intVar("cpuCooler_" + i, isCompatible ? 1 : 0);
		}

        Solver solver = model.getSolver();

        if (solver.solve()) {
            for (int i = 0; i < cpuVars.length; i++) {
                if (cpuVars[i].getValue() == 1) {
                    compatibleCpuCoolers.add(allCpus.get(i));
                }
            }
        }

		return compatibleCpuCoolers;
	}

}