package com.project.service;

import com.project.repository.CaseRepository;
import com.project.repository.ProductConfigRepository;
import com.project.repository.entity.ProductConfig;
import com.project.repository.entity.Case;

import java.util.ArrayList;
import java.util.List;

import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import org.chocosolver.solver.Solver;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

import org.jboss.logging.Logger;
import org.kie.internal.runtime.manager.context.CaseContext;

import com.project.controller.contracts.CaseContract;
import com.project.controller.contracts.VideoCardContract;

@ApplicationScoped
public class CaseService
{
    @Inject
    ProductConfigRepository productConfigRepository;
    
    @Inject
    CaseRepository caseRepository;

    private static final Logger logger = Logger.getLogger(CaseService.class);
    
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

    public void addCase(String sessionId, CaseContract casepc) {
		ProductConfig productConfig = getOrCreate(sessionId);
		productConfig.pcCase = casepc;

		productConfigRepository.persistOrUpdate(productConfig);
	}

    public List<Case> filterCases(String sessionId)
    {
        Model model = new Model("Case Compatibility");
        List<Case> allCases = caseRepository.listAll();
        List<Case> compatibleCases = new ArrayList<>();

        ProductConfig productConfig = getOrCreate(sessionId);

        VideoCardContract videoCardContract = productConfig.videoCard;
        
        IntVar[] caseVars = new IntVar[allCases.size()];

        for (int i = 0; i < allCases.size(); i++)
        {
            Boolean isCompatible = true;
            if (videoCardContract != null)
            {
                Case caseItem = allCases.get(i);
                String temp = caseItem.getDimensions();
                if (temp == null || temp.isEmpty()) {
                    isCompatible = false;
                } else {
                    String[] caseDimensions = temp.split(",");
                    isCompatible &= Integer.parseInt(caseDimensions[2]) >= Integer.parseInt(videoCardContract.getLength().split(" ")[0]);
                }
            }

            caseVars[i] = model.intVar("case_" + i, isCompatible ? 1 : 0);
        }

        Solver solver = model.getSolver();

        if (solver.solve()) {
            for (int i = 0; i < caseVars.length; i++) {
                if (caseVars[i].getValue() == 1) {
                    compatibleCases.add(allCases.get(i));
                }
            }
        }

        return compatibleCases;
    }
}