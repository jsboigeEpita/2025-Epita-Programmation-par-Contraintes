package com.project.service;

import java.util.ArrayList;
import java.util.List;
import org.chocosolver.solver.Model;
import org.chocosolver.solver.Solver;
import org.chocosolver.solver.variables.IntVar;
import org.jboss.logging.Logger;


import com.project.controller.contracts.MemoryContract;
import com.project.controller.contracts.MotherboardContract;
import com.project.converter.SockerMbToRam;
import com.project.repository.ProductConfigRepository;
import com.project.repository.RamRepository;
import com.project.repository.entity.ProductConfig;
import com.project.repository.entity.Ram;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

@ApplicationScoped
public class MemoryService
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

	public void addMemory(String sessionId, MemoryContract ram) {
		ProductConfig productConfig = getOrCreate(sessionId);
		if (productConfig.memory != null) {
			productConfig.PowerConsumption -=  productConfig.memory.getPowerConsumption();
			productConfig.price -= Float.parseFloat(productConfig.memory.getPrice().replace('$', ' ').trim());
		}
		productConfig.memory = ram;
		productConfig.PowerConsumption +=  productConfig.memory.getPowerConsumption();
		productConfig.price += Float.parseFloat(productConfig.memory.getPrice().replace('$', ' ').trim());

		productConfigRepository.persistOrUpdate(productConfig);
	}



	private static final Logger logger = Logger.getLogger(MemoryService.class);

	@Inject
	RamRepository ramRepository;

	@Inject
	SockerMbToRam sockerMbToRam;

	@Inject
	SockerMbToRam socketMbToRamConverter;

	public List<Ram> filterRam(String sessionId)
	{
		Model model = new Model("Ram Filter");
		List<Ram> allRam = ramRepository.listAll().stream().filter(c -> c.price.length() != 0).toList();
		List<Ram> compatibleRams = new ArrayList<>();

		ProductConfig productConfig = getOrCreate(sessionId);

		MotherboardContract mb = productConfig.motherboard;

		int MbMemoryMax = 0;
		String MbMemoryType = "";
		int MbMemorySlot = 0;

		logger.info("Motherboard: " + mb);

		if (mb != null)
		{
			MbMemoryMax = Integer.parseInt(mb.maxMemory.split(" ")[0]);
			MbMemoryType = mb.maxMemory.split(" ")[1];
			MbMemorySlot = Integer.parseInt(mb.memorySlots);
		}


        IntVar[] ramVars = new IntVar[allRam.size()];


		for (int i = 0; i < allRam.size(); i++)
		{
			Ram ram = allRam.get(i);
			boolean isCompatible = true;
			
			if (mb != null)
			{
				String[] ramData = ram.modules.split(" x ");
				int ramSlots = Integer.parseInt(ramData[0]);
				try
				{

					String ramMemoryType = "";
					int ramQuantity = 0;
					if (ramData[1].contains("GB"))
					{
						ramMemoryType = "GB";
						ramQuantity = Integer.parseInt(ramData[1].replace("GB", ""));
					}
					else if (ramData[1].contains("MB"))
					{
						ramMemoryType = "MB";
						ramQuantity = Integer.parseInt(ramData[1].replace("MB", ""));
					}

					String ramSpeed = ram.speed.split("-")[0];	
					
					
					isCompatible &= socketMbToRamConverter.socketMemoryMap.get(mb.socketCpu).contains(ramSpeed);
					isCompatible &= ramMemoryType.equals(MbMemoryType);
					isCompatible &= MbMemorySlot >= ramSlots;
					isCompatible &= MbMemoryMax >= ramQuantity * ramSlots;
				}
				catch (Exception e)
				{
					isCompatible = false;
				}
			}

			ramVars[i] = model.intVar("ram_" + i, isCompatible ? 1 : 0);
		}

        Solver solver = model.getSolver();

        if (solver.solve()) {
            for (int i = 0; i < ramVars.length; i++) {
                if (ramVars[i].getValue() == 1) {
                    compatibleRams.add(allRam.get(i));
                }
            }
        }		


		return compatibleRams;
	}

}