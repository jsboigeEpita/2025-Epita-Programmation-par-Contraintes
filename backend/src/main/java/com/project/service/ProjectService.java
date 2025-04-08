package com.project.service;

import java.util.ArrayList;
import java.util.List;

import org.chocosolver.solver.Model;
import org.chocosolver.solver.Solver;
import org.chocosolver.solver.variables.IntVar;
import org.jboss.logging.Logger;

import com.project.converter.SocketMbToCpu;
import com.project.repository.CpuRepository;
import com.project.repository.MotherboardsRepository;
import com.project.repository.ProductConfigRepository;
import com.project.repository.entity.Cpu;
import com.project.repository.entity.Motherboard;
import com.project.repository.entity.ProductConfig;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;


@ApplicationScoped
public class ProjectService {


    private final Logger logger = Logger.getLogger(ProjectService.class);

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
        logger.info(productConfig.id.toString());

		return productConfig;
	}

    public int removeComponents(String sessionId, String componentType) {
        ProductConfig productConfig = getOrCreate(sessionId);
        logger.info("Removing component: " + productConfig.memory);
        switch (componentType)
        {
            case "cpu":
                if (productConfig.cpu != null)
                {
                    productConfig.price -= Float.parseFloat(productConfig.cpu.getPrice().replace('$', ' ').trim());
                    productConfig.PowerConsumption -= productConfig.cpu.getPowerConsumption();
                    productConfig.cpu = null;
                }
                break;
            case "motherboard":
                if (productConfig.motherboard != null)
                {
                    productConfig.price -= Float.parseFloat(productConfig.motherboard.getPrice().replace('$', ' ').trim());
                    productConfig.PowerConsumption -= productConfig.motherboard.getPowerConsumption();
                    productConfig.motherboard = null;
                }
                break;
            case "ram":
                if (productConfig.memory != null)
                {
                    logger.info("Removing RAM: " + productConfig.memory.getName());
                    productConfig.price -= Float.parseFloat(productConfig.memory.getPrice().replace('$', ' ').trim());
                    productConfig.PowerConsumption -= productConfig.memory.getPowerConsumption();
                    productConfig.memory = null;
                }
                break;
            case "gpu":
                if (productConfig.videoCard != null)
                {
                    productConfig.price -= Float.parseFloat(productConfig.videoCard.getPrice().replace('$', ' ').trim());
                    productConfig.PowerConsumption -= productConfig.videoCard.getPowerConsumption();
                    productConfig.videoCard = null;
                }
                break;
            case "case":
                if (productConfig.pcCase != null)
                {
                    productConfig.price -= Float.parseFloat(productConfig.pcCase.getPrice().replace('$', ' ').trim());
                    productConfig.pcCase = null;
                }   
                break;
            case "powerSupply":
                if (productConfig.powerSupply != null)
                {
                    productConfig.price -= Float.parseFloat(productConfig.powerSupply.getPrice().replace('$', ' ').trim());
                    productConfig.powerSupply = null;
                }   
                break;
            case "cpuCooler":
                if (productConfig.cpuCooler != null)
                {
                    productConfig.price -= Float.parseFloat(productConfig.cpuCooler.getPrice().replace('$', ' ').trim());
                    productConfig.PowerConsumption -= productConfig.cpuCooler.getPowerConsumption();
                    productConfig.cpuCooler = null;
                }
                break;
            // case "storage":
                // productConfig. = null;
                // break;
            default:
                return 400;
        
        }
        logger.info(productConfig.id.toString());
        productConfig.update();
        // productConfigRepository.update(productConfig);

        return 200;
    }

    public ProductConfig getProductConfig(String sessionId) {
        ProductConfig productConfig = getOrCreate(sessionId);
        return productConfig;
    }

}