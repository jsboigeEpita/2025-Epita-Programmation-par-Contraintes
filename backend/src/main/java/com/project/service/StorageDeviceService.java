package com.project.service;

import java.util.ArrayList;
import java.util.List;

import org.chocosolver.solver.Model;
import org.chocosolver.solver.Solver;
import org.chocosolver.solver.variables.IntVar;

import com.project.controller.contracts.StorageDeviceContract;
import com.project.repository.ProductConfigRepository;
import com.project.repository.StorageDeviceRepository;
import com.project.repository.entity.ProductConfig;
import com.project.repository.entity.StorageDevice;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

import org.jboss.logging.Logger;;

@ApplicationScoped
public class StorageDeviceService
{
	@Inject
	ProductConfigRepository productConfigRepository;

    @Inject
    StorageDeviceRepository storageDeviceRepository;

    private static final Logger logger = Logger.getLogger(StorageDeviceService.class);

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

    public void addStorageDevice(String sessionId, StorageDeviceContract storagevideo) {
		ProductConfig productConfig = getOrCreate(sessionId);
		productConfig.storageDevice = storagevideo;

		productConfigRepository.persistOrUpdate(productConfig);
	}

    public List<StorageDevice> filteStorageDevices(String sessionId)
    {
        Model model = new Model("Storage Device Compatibility");
        List<StorageDevice> allCases = storageDeviceRepository.listAll();
        List<StorageDevice> compatibleStorageDevice = new ArrayList<>();

        
        logger.info(allCases.size());

        ProductConfig productConfig = getOrCreate(sessionId);
        
        IntVar[] storageDeviceVars = new IntVar[allCases.size()];

        for (int i = 0; i < allCases.size(); i++) {
            storageDeviceVars[i] = model.intVar("StorageDevice_" + i, 0, 1);
        }

        Solver solver = model.getSolver();

        if (solver.solve()) {
            for (int i = 0; i < storageDeviceVars.length; i++) {
                if (storageDeviceVars[i].getValue() == 1) {
                    compatibleStorageDevice.add(allCases.get(i));
                }
            }
        }

        return allCases;
    }
}