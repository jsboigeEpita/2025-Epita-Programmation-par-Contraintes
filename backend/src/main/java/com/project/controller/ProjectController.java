package com.project.controller;

import java.io.IOException;
import java.io.InputStream;
import java.util.List;

import com.project.controller.contracts.ConfigContract;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.MapperFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.project.controller.contracts.CaseContract;
import com.project.controller.contracts.CPUContract;
import com.project.controller.contracts.CPUCoolerContract; 
import com.project.controller.contracts.MemoryContract;
import com.project.controller.contracts.MotherboardContract;
import com.project.controller.contracts.PowerSupplyContract;
import com.project.controller.contracts.VideoCardContract;
import com.project.repository.CpuCoolerRepository;
import com.project.repository.entity.CpuCooler;
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
import jakarta.ws.rs.DefaultValue;
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

    // @GET
    // @Path("/getCase")
    // @Produces(MediaType.APPLICATION_JSON)
    // public Response getCase(@QueryParam("page") @DefaultValue("1") int page, 
    //                            @QueryParam("size") @DefaultValue("20") int size,
    //                            @QueryParam("config") @DefaultValue("") String configJson) {

    //     ObjectMapper objectMapper = new ObjectMapper();
    //     objectMapper.configure(MapperFeature.ACCEPT_CASE_INSENSITIVE_PROPERTIES, true);

    //     ConfigContract config = null;

    //     try {
    //         if (!configJson.isEmpty()) {
    //             config = objectMapper.readValue(configJson, ConfigContract.class);
    //         }
    //     } catch (IOException e) {
    //         return Response.status(Response.Status.BAD_REQUEST)
    //                        .entity("Erreur de parsing du JSON de configuration : " + e.getMessage())
    //                        .build();
    //     }

    //     try (InputStream inputStream = getClass().getClassLoader().getResourceAsStream("case_data.json")) {

    //         if (inputStream == null) {
    //             return Response.status(Response.Status.NOT_FOUND)
    //                            .entity("Fichier JSON introuvable.")
    //                            .build();
    //         }

    //         List<CaseContract> cases = objectMapper.readValue(inputStream, new TypeReference<List<CaseContract>>() {});

    //         int start = (page - 1) * size;
    //         int end = Math.min(start + size, cases.size());
            
    //         if (start >= cases.size()) {
    //             return Response.status(Response.Status.BAD_REQUEST)
    //                     .entity("Page demandée trop grande. Il n'y a pas assez d'éléments.")
    //                     .build();
    //         }

    //         List<CaseContract> pageData = cases.subList(start, end);

    //         return Response.ok(pageData).build();

    //     } catch (IOException e) {
    //         return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
    //                        .entity("Erreur de lecture du fichier JSON : " + e.getMessage())
    //                        .build();
    //     }
    // }

    // @GET
    // @Path("/getCPU")
    // @Produces(MediaType.APPLICATION_JSON)
    // public Response getCPU(@QueryParam("page") @DefaultValue("1") int page, 
    //                         @QueryParam("size") @DefaultValue("20") int size,
    //                         @QueryParam("config") @DefaultValue("") String configJson) {

    //     ObjectMapper objectMapper = new ObjectMapper();
    //     objectMapper.configure(MapperFeature.ACCEPT_CASE_INSENSITIVE_PROPERTIES, true);

    //     ConfigContract config = null;

    //     try {
    //         if (!configJson.isEmpty()) {
    //             config = objectMapper.readValue(configJson, ConfigContract.class);
    //         }
    //     } catch (IOException e) {
    //         return Response.status(Response.Status.BAD_REQUEST)
    //                        .entity("Erreur de parsing du JSON de configuration : " + e.getMessage())
    //                        .build();
    //     }

    //     try (InputStream inputStream = getClass().getClassLoader().getResourceAsStream("cpu_data.json")) {

    //         if (inputStream == null) {
    //             return Response.status(Response.Status.NOT_FOUND)
    //                            .entity("Fichier JSON introuvable.")
    //                            .build();
    //         }

    //         List<CPUContract> cases = objectMapper.readValue(inputStream, new TypeReference<List<CPUContract>>() {});

    //         int start = (page - 1) * size;
    //         int end = Math.min(start + size, cases.size());
            
    //         if (start >= cases.size()) {
    //             return Response.status(Response.Status.BAD_REQUEST)
    //                     .entity("Page demandée trop grande. Il n'y a pas assez d'éléments.")
    //                     .build();
    //         }

    //         List<CPUContract> pageData = cases.subList(start, end);

    //         return Response.ok(pageData).build();

    //     } catch (IOException e) {
    //         return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
    //                        .entity("Erreur de lecture du fichier JSON : " + e.getMessage())
    //                        .build();
    //     }
    // }

    // @GET
    // @Path("/getCPUCooler")
    // @Produces(MediaType.APPLICATION_JSON)
    // public Response getCPUCooler(@QueryParam("page") @DefaultValue("1") int page, 
    //                               @QueryParam("size") @DefaultValue("20") int size,
    //                               @QueryParam("config") @DefaultValue("") String configJson) {

    //     ObjectMapper objectMapper = new ObjectMapper();
    //     objectMapper.configure(MapperFeature.ACCEPT_CASE_INSENSITIVE_PROPERTIES, true);

    //     ConfigContract config = null;

    //     try {
    //         if (!configJson.isEmpty()) {
    //             config = objectMapper.readValue(configJson, ConfigContract.class);
    //         }
    //     } catch (IOException e) {
    //         return Response.status(Response.Status.BAD_REQUEST)
    //                        .entity("Erreur de parsing du JSON de configuration : " + e.getMessage())
    //                        .build();
    //     }

    //     try (InputStream inputStream = getClass().getClassLoader().getResourceAsStream("cpu-cooler_data.json")) {

    //         if (inputStream == null) {
    //             return Response.status(Response.Status.NOT_FOUND)
    //                            .entity("Fichier JSON introuvable.")
    //                            .build();
    //         }

    //         List<CPUCoolerContract> cases = objectMapper.readValue(inputStream, new TypeReference<List<CPUCoolerContract>>() {});

    //         int start = (page - 1) * size;
    //         int end = Math.min(start + size, cases.size());
            
    //         if (start >= cases.size()) {
    //             return Response.status(Response.Status.BAD_REQUEST)
    //                     .entity("Page demandée trop grande. Il n'y a pas assez d'éléments.")
    //                     .build();
    //         }

    //         List<CPUCoolerContract> pageData = cases.subList(start, end);

    //         return Response.ok(pageData).build();

    //     } catch (IOException e) {
    //         return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
    //                        .entity("Erreur de lecture du fichier JSON : " + e.getMessage())
    //                        .build();
    //     }
    // }

    // @GET
    // @Path("/getMemory")
    // @Produces(MediaType.APPLICATION_JSON)
    // public Response getMemory(@QueryParam("page") @DefaultValue("1") int page, 
    //                            @QueryParam("size") @DefaultValue("20") int size,
    //                            @QueryParam("config") @DefaultValue("") String configJson) {

    //     ObjectMapper objectMapper = new ObjectMapper();
    //     objectMapper.configure(MapperFeature.ACCEPT_CASE_INSENSITIVE_PROPERTIES, true);

    //     ConfigContract config = null;

    //     try {
    //         if (!configJson.isEmpty()) {
    //             config = objectMapper.readValue(configJson, ConfigContract.class);
    //         }
    //     } catch (IOException e) {
    //         return Response.status(Response.Status.BAD_REQUEST)
    //                        .entity("Erreur de parsing du JSON de configuration : " + e.getMessage())
    //                        .build();
    //     }

    //     try (InputStream inputStream = getClass().getClassLoader().getResourceAsStream("memory_data.json")) {

    //         if (inputStream == null) {
    //             return Response.status(Response.Status.NOT_FOUND)
    //                            .entity("Fichier JSON introuvable.")
    //                            .build();
    //         }

    //         List<MemoryContract> cases = objectMapper.readValue(inputStream, new TypeReference<List<MemoryContract>>() {});

    //         int start = (page - 1) * size;
    //         int end = Math.min(start + size, cases.size());
            
    //         if (start >= cases.size()) {
    //             return Response.status(Response.Status.BAD_REQUEST)
    //                     .entity("Page demandée trop grande. Il n'y a pas assez d'éléments.")
    //                     .build();
    //         }

    //         List<MemoryContract> pageData = cases.subList(start, end);

    //         return Response.ok(pageData).build();

    //     } catch (IOException e) {
    //         return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
    //                        .entity("Erreur de lecture du fichier JSON : " + e.getMessage())
    //                        .build();
    //     }
    // }

    // @GET
    // @Path("/getPowerSupply")
    // @Produces(MediaType.APPLICATION_JSON)
    // public Response getPowerSupply(@QueryParam("page") @DefaultValue("1") int page, 
    //                                @QueryParam("size") @DefaultValue("20") int size,
    //                                @QueryParam("config") @DefaultValue("") String configJson) {

    //     ObjectMapper objectMapper = new ObjectMapper();
    //     objectMapper.configure(MapperFeature.ACCEPT_CASE_INSENSITIVE_PROPERTIES, true);

    //     ConfigContract config = null;

    //     try {
    //         if (!configJson.isEmpty()) {
    //             config = objectMapper.readValue(configJson, ConfigContract.class);
    //         }
    //     } catch (IOException e) {
    //         return Response.status(Response.Status.BAD_REQUEST)
    //                        .entity("Erreur de parsing du JSON de configuration : " + e.getMessage())
    //                        .build();
    //     }

    //     try (InputStream inputStream = getClass().getClassLoader().getResourceAsStream("power-supply_data.json")) {

    //         if (inputStream == null) {
    //             return Response.status(Response.Status.NOT_FOUND)
    //                            .entity("Fichier JSON introuvable.")
    //                            .build();
    //         }

    //         List<PowerSupplyContract> cases = objectMapper.readValue(inputStream, new TypeReference<List<PowerSupplyContract>>() {});

    //         int start = (page - 1) * size;
    //         int end = Math.min(start + size, cases.size());
            
    //         if (start >= cases.size()) {
    //             return Response.status(Response.Status.BAD_REQUEST)
    //                     .entity("Page demandée trop grande. Il n'y a pas assez d'éléments.")
    //                     .build();
    //         }

    //         List<PowerSupplyContract> pageData = cases.subList(start, end);

    //         return Response.ok(pageData).build();

    //     } catch (IOException e) {
    //         return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
    //                        .entity("Erreur de lecture du fichier JSON : " + e.getMessage())
    //                        .build();
    //     }
    // }

    // @GET
    // @Path("/getMotherboard")
    // @Produces(MediaType.APPLICATION_JSON)
    // public Response getMotherboard(@QueryParam("page") @DefaultValue("1") int page, 
    //                              @QueryParam("size") @DefaultValue("20") int size,
    //                              @QueryParam("config") @DefaultValue("") String configJson) {

    //     ObjectMapper objectMapper = new ObjectMapper();
    //     objectMapper.configure(MapperFeature.ACCEPT_CASE_INSENSITIVE_PROPERTIES, true);

    //     ConfigContract config = null;

    //     try {
    //         if (!configJson.isEmpty()) {
    //             config = objectMapper.readValue(configJson, ConfigContract.class);
    //         }
    //     } catch (IOException e) {
    //         return Response.status(Response.Status.BAD_REQUEST)
    //                        .entity("Erreur de parsing du JSON de configuration : " + e.getMessage())
    //                        .build();
    //     }

    //     try (InputStream inputStream = getClass().getClassLoader().getResourceAsStream("motherboard_data.json")) {

    //         if (inputStream == null) {
    //             return Response.status(Response.Status.NOT_FOUND)
    //                            .entity("Fichier JSON introuvable.")
    //                            .build();
    //         }

    //         List<MotherboardContract> cases = objectMapper.readValue(inputStream, new TypeReference<List<MotherboardContract>>() {});

    //         System.out.println("Nombre de cartes mères avant le filtrage : " + cases.size());
    //         cases = projectService.filterMotherboard(cases, config);
    //         System.out.println("Filtered Motherboards: " + cases.size());

    //         int start = (page - 1) * size;
    //         int end = Math.min(start + size, cases.size());
            
    //         if (start >= cases.size()) {
    //             return Response.status(Response.Status.BAD_REQUEST)
    //                     .entity("Page demandée trop grande. Il n'y a pas assez d'éléments.")
    //                     .build();
    //         }

    //         List<MotherboardContract> pageData = cases.subList(start, end);

    //         return Response.ok(pageData).build();

    //     } catch (IOException e) {
    //         return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
    //                        .entity("Erreur de lecture du fichier JSON : " + e.getMessage())
    //                        .build();
    //     }
    // }

    // @GET
    // @Path("/getVideoCard")
    // @Produces(MediaType.APPLICATION_JSON)
    // public Response getVideoCard(@QueryParam("page") @DefaultValue("1") int page, 
    //                              @QueryParam("size") @DefaultValue("20") int size,
    //                              @QueryParam("config") @DefaultValue("") String configJson) {

    //     ObjectMapper objectMapper = new ObjectMapper();
    //     objectMapper.configure(MapperFeature.ACCEPT_CASE_INSENSITIVE_PROPERTIES, true);

    //     ConfigContract config = null;

    //     try {
    //         if (!configJson.isEmpty()) {
    //             config = objectMapper.readValue(configJson, ConfigContract.class);
    //         }
    //     } catch (IOException e) {
    //         return Response.status(Response.Status.BAD_REQUEST)
    //                        .entity("Erreur de parsing du JSON de configuration : " + e.getMessage())
    //                        .build();
    //     }

    //     try (InputStream inputStream = getClass().getClassLoader().getResourceAsStream("video-card_data.json")) {

    //         if (inputStream == null) {
    //             return Response.status(Response.Status.NOT_FOUND)
    //                            .entity("Fichier JSON introuvable.")
    //                            .build();
    //         }

    //         List<VideoCardContract> cases = objectMapper.readValue(inputStream, new TypeReference<List<VideoCardContract>>() {});

    //         int start = (page - 1) * size;
    //         int end = Math.min(start + size, cases.size());
            
    //         if (start >= cases.size()) {
    //             return Response.status(Response.Status.BAD_REQUEST)
    //                     .entity("Page demandée trop grande. Il n'y a pas assez d'éléments.")
    //                     .build();
    //         }

    //         List<VideoCardContract> pageData = cases.subList(start, end);

    //         return Response.ok(pageData).build();

    //     } catch (IOException e) {
    //         return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
    //                        .entity("Erreur de lecture du fichier JSON : " + e.getMessage())
    //                        .build();
    //     }
    // }
}
