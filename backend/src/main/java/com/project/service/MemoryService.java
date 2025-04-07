package com.project.service;

import java.util.ArrayList;
import java.util.List;

import org.jboss.logging.Logger;

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


	public List<Ram> filterRam(String sessionId)
	{
		List<Ram> allRam = ramRepository.listAll();
		List<Ram> compatibleRams = new ArrayList<>();

		ProductConfig productConfig = getOrCreate(sessionId);


		


		return compatibleRams;
	}

}