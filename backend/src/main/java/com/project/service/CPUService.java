package com.project.service;

import java.util.ArrayList;
import java.util.List;

import org.chocosolver.solver.Model;
import org.chocosolver.solver.Solver;
import org.chocosolver.solver.variables.IntVar;
import org.jboss.logging.Logger;

import com.project.controller.contracts.CPUContract;
import com.project.controller.contracts.MotherboardContract;
import com.project.controller.contracts.PowerSupplyContract;
import com.project.converter.SocketMbToCpu;
import com.project.repository.CpuRepository;
import com.project.repository.ProductConfigRepository;
import com.project.repository.entity.Cpu;
import com.project.repository.entity.Motherboard;
import com.project.repository.entity.ProductConfig;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

@ApplicationScoped
public class CPUService
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

	public void addCpu(String sessionId, CPUContract cpu) {
		ProductConfig productConfig = getOrCreate(sessionId);
		if (productConfig.cpu != null) {
			productConfig.PowerConsumption -=  productConfig.cpu.getPowerConsumption();
			productConfig.price -= Float.parseFloat(productConfig.cpu.getPrice().replace('$', ' ').trim());
		}
		productConfig.cpu = cpu;
		productConfig.PowerConsumption +=  productConfig.cpu.getPowerConsumption();
		productConfig.price += Float.parseFloat(productConfig.cpu.getPrice().replace('$', ' ').trim());

		productConfigRepository.persistOrUpdate(productConfig);
	}


	private static final Logger logger = Logger.getLogger(CPUService.class);


	@Inject
	SocketMbToCpu mbCpuConverter;
	
	@Inject
	CpuRepository cpuRepository;


	public List<Cpu> filterCpus(String sessionId)
	{
		Model model = new Model("Cpu Compatibility");
		List<Cpu> allCpus = cpuRepository.listAll();
		List<Cpu> compatibleMotherboards = new ArrayList<>();

		ProductConfig productConfig = getOrCreate(sessionId);

		MotherboardContract motherboardContract = productConfig.motherboard;
		PowerSupplyContract powerSupplyContract = productConfig.powerSupply;


		IntVar[] cpuVars = new IntVar[allCpus.size()];
	
		int wattage = 0;
		if (powerSupplyContract != null)
		{
			wattage = Integer.parseInt(powerSupplyContract.getWattage().split(" ")[0]) - (productConfig.cpu != null ? productConfig.cpu.getPowerConsumption() : 0);
		}

		for (int i = 0; i < allCpus.size(); i++)
		{
			Cpu cpu = allCpus.get(i);
			boolean isCompatible = true;

			if (motherboardContract != null)
			{
                isCompatible &= mbCpuConverter.socketArchitectureMap.get(motherboardContract.getSocketCpu()).contains(cpu.microarchitecture);
			}
			if (isCompatible && powerSupplyContract != null)
			{
				isCompatible &= cpu.powerConsumption + productConfig.PowerConsumption <= wattage;
			}
			cpuVars[i] = model.intVar("cpu_" + i, isCompatible ? 1 : 0);
		}

        Solver solver = model.getSolver();

        if (solver.solve()) {
            for (int i = 0; i < cpuVars.length; i++) {
                if (cpuVars[i].getValue() == 1) {
                    compatibleMotherboards.add(allCpus.get(i));
                }
            }
        }

		return compatibleMotherboards;
	}

}