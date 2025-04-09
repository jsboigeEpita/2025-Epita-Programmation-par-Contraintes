package com.project.service;

import java.util.ArrayList;
import java.util.List;

import org.chocosolver.solver.Model;
import org.chocosolver.solver.Solver;
import org.chocosolver.solver.variables.IntVar;
import org.jboss.logging.Logger;

import com.project.controller.contracts.CPUCoolerContract;
import com.project.controller.contracts.CaseContract;
import com.project.controller.contracts.MotherboardContract;
import com.project.controller.contracts.PowerSupplyContract;
import com.project.controller.contracts.VideoCardContract;
import com.project.converter.SocketMbToCpu;
import com.project.repository.CpuCoolerRepository;
import com.project.repository.CpuRepository;
import com.project.repository.ProductConfigRepository;
import com.project.repository.VideoCardRepository;
import com.project.repository.entity.Cpu;
import com.project.repository.entity.CpuCooler;
import com.project.repository.entity.ProductConfig;
import com.project.repository.entity.VideoCard;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

@ApplicationScoped
public class VideoCardService
{
	@Inject
	ProductConfigRepository productConfigRepository;

    @Inject
    VideoCardRepository videoCardRepository;

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

    public void addVideoCard(String sessionId, VideoCardContract videoCard) {
		ProductConfig productConfig = getOrCreate(sessionId);
		if (productConfig.memory != null) {
			productConfig.PowerConsumption -= productConfig.videoCard.getPowerConsumption();
			productConfig.price -= Float.parseFloat(productConfig.videoCard.getPrice().replace('$', ' ').trim());
		}
		productConfig.videoCard = videoCard;
		productConfig.PowerConsumption +=  productConfig.videoCard.getPowerConsumption();
		productConfig.price += Float.parseFloat(productConfig.videoCard.getPrice().replace('$', ' ').trim());

		productConfigRepository.persistOrUpdate(productConfig);
	}

    public List<VideoCard> filteVideoCards(String sessionId)
    {
        Model model = new Model("Video Card Compatibility");
        List<VideoCard> allCases = videoCardRepository.listAll();
        List<VideoCard> compatibleVideoCard = new ArrayList<>();

        System.out.println("All video cards: " + allCases.size());

        ProductConfig productConfig = getOrCreate(sessionId);
        
        PowerSupplyContract powerSupply = productConfig.powerSupply;
        CaseContract pcCase = productConfig.pcCase;

        int wattage = 0;
		if (powerSupply != null)
		{
			wattage = Integer.parseInt(powerSupply.getWattage().split(" ")[0]);
		}

        int caseWidth = 0;
        if (pcCase != null)
        {
            String temp = pcCase.getDimensions();
            if (temp != null && !temp.isEmpty()) {
                String[] caseDimensions = temp.split(",");
                caseWidth = Integer.parseInt(caseDimensions[2]);
            }
        }

        IntVar[] videoCardVars = new IntVar[allCases.size()];

        for (int i = 0; i < allCases.size(); i++) {
            Boolean isCompatible = true;
            VideoCard videoCard = allCases.get(i);
            if (isCompatible && powerSupply != null)
			{
				isCompatible &= videoCard.getPowerConsumption() + productConfig.PowerConsumption <= wattage;
			}
            if (isCompatible && pcCase != null && videoCard.getLength() != null)
            {
                try {
                    String[] videoCardDimensions = videoCard.getLength().split(" ");
                    if (videoCardDimensions.length > 0) {
                        int videoCardLength = Integer.parseInt(videoCardDimensions[0]);
                        isCompatible &= caseWidth >= videoCardLength;
                    } else {
                        isCompatible = false;
                    }
                } catch (NumberFormatException e) {
                    isCompatible = false;
                }
            }
            else{
                System.out.println("Case width: " + videoCard.getLength() + " " + caseWidth);
            }
            
            videoCardVars[i] = model.intVar("VideoCard_" + i, isCompatible ? 1 : 0);
        }

        Solver solver = model.getSolver();

        if (solver.solve()) {
            for (int i = 0; i < videoCardVars.length; i++) {
                if (videoCardVars[i].getValue() == 1) {
                    compatibleVideoCard.add(allCases.get(i));
                }
            }
        }

        return compatibleVideoCard;
    }
}