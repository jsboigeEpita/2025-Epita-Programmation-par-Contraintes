package com.project.service;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import org.jboss.logging.Logger;

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
		List<Ram> allRam = ramRepository.listAll();
		List<Ram> compatibleRams = new ArrayList<>();

		ProductConfig productConfig = getOrCreate(sessionId);

		MotherboardContract mb = productConfig.motherboard;

		int MbMemoryMax = 0;
		String MbMemoryType = "";
		int MbMemorySlot = 0;

		if (mb == null)
		{
			MbMemoryMax = Integer.parseInt(mb.maxMemory.split(" ")[0]);
			MbMemoryType = mb.maxMemory.split(" ")[1];
			MbMemorySlot = Integer.parseInt(mb.memorySlots);
		}


        IntVar[] ramVars = new IntVar[allRam.size()];


		for (int i = 0; i < compatibleRams.size(); i++)
		{
			Ram ram = allRam.get(i);
			boolean isCompatible = true;
			
			if (mb != null)
			{
				String[] ramData = ram.modules.split(" x ");
				int ramSlots = Integer.parseInt(ramData[0]);
				
				Pattern pattern = Pattern.compile("(\\\\d+)([a-zA-Z]+)");
				Matcher matcher = pattern.matcher(ramData[1]);

				int ramQuantity = Integer.parseInt(matcher.group(1));
				String ramMemoryType = matcher.group(2);

				String ramSpeed = ram.speed.split(" ")[0];
				
				isCompatible &= socketMbToRamConverter.socketMemoryMap.get(mb.socketCpu).contains(ramSpeed);
				isCompatible &= ramMemoryType.equals(MbMemoryType);
				isCompatible &= MbMemorySlot >= ramSlots;
				isCompatible &= MbMemoryMax >= ramQuantity * ramSlots;
			}

			ramVars[i] = model.intVar("mb_" + i, isCompatible ? 1 : 0);
		}
		


		return compatibleRams;
	}

}