package com.project.controller;

import com.project.controller.contracts.CPUContract;
import com.project.controller.contracts.CPUCoolerContract; 
import com.project.controller.contracts.MemoryContract;
import com.project.controller.contracts.MotherboardContract;
import com.project.service.CPUCoolerService;
import com.project.service.CPUService;
import com.project.service.MemoryService;
import com.project.service.MotherboardService;
import com.project.service.ProjectService;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.CookieParam;
import jakarta.ws.rs.DELETE;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.PathParam;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.QueryParam;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import org.jboss.logging.Logger;


@ApplicationScoped
@Path("/api")
public class ProjectController {

    @Inject
    ProjectService projectService;

    @Inject
    MotherboardService motherboardService;

    @Inject
    CPUService cpuService;

    @Inject
    CPUCoolerService cpuCoolerService;

    @Inject
    MemoryService memoryService;


    private final Logger logger = Logger.getLogger(ProjectController.class);

    //SessionId - Utile pour conserver le build de l'utilisateur a travers les requetes.
    @GET
    @Path("{components}")
    @Produces(MediaType.APPLICATION_JSON)
    public Response getComponents(@PathParam("components") String component, @QueryParam("page") int page, @CookieParam("SessionId") String sessionId)
    {
        logger.info("SessionId: " + sessionId);
        logger.info("Component: " + component);
        logger.info("Page: " + page);
        switch (component)
        {
            case "motherboard":
                return Response.ok(motherboardService.filterMotherboard(sessionId)).build();
            case "cpu":
                return Response.ok(cpuService.filterCpus(sessionId)).build();
            case "cpu-cooler":
                return Response.ok(cpuCoolerService.filterCpusCoolers(sessionId)).build();
            case "ram":
                return Response.ok(memoryService.filterRam(sessionId)).build();
        }
        return Response.ok().build();
    }

    @DELETE
    @Path("{component}")
    @Produces(MediaType.APPLICATION_JSON)
    public Response deleteComponents(@PathParam("component") String component, @CookieParam("SessionId") String sessionId)
    {
        logger.info("SessionId: " + sessionId);
        logger.info("Component: " + component);
        return Response.status(projectService.removeComponents(sessionId, component)).build();
    }
    @GET
    @Path("config")
    @Produces(MediaType.APPLICATION_JSON)
    public Response getConfig(@CookieParam("SessionId") String sessionId)
    {
        return Response.ok(projectService.getProductConfig(sessionId)).build();
    }

    @POST
    @Path("motherboard")
    @Consumes(MediaType.APPLICATION_JSON)
    public Response postMotherBoard(MotherboardContract motherboardContract, @CookieParam("SessionId") String sessionId)
    {
        motherboardService.addMotherboard(sessionId, motherboardContract);
        return Response.ok().build();
    }


    @POST
    @Path("cpu")
    @Consumes(MediaType.APPLICATION_JSON)
    public Response postCpu(CPUContract cpuContract, @CookieParam("SessionId") String sessionId)
    {
        cpuService.addCpu(sessionId, cpuContract);
        return Response.ok().build();
    }


    @POST
    @Path("cpu-cooler")
    @Consumes(MediaType.APPLICATION_JSON)
    public Response postCpuCooler(CPUCoolerContract cpuCoolerContract, @CookieParam("SessionId") String sessionId)
    {
        cpuCoolerService.addCpuCooler(sessionId, cpuCoolerContract);
        return Response.ok().build();
    }


    @POST
    @Path("ram")
    @Consumes(MediaType.APPLICATION_JSON)
    public Response postRam(MemoryContract ramContract, @CookieParam("SessionId") String sessionId)
    {
        memoryService.addMemory(sessionId, ramContract);
        return Response.ok().build();
    }



    @GET
    @Path("/")
    @Produces(MediaType.TEXT_PLAIN)
    public Response get() {
        return Response.ok().build();
    }
}
