package com.project.controller;

import java.io.IOException;
import java.io.InputStream;
import java.util.List;

import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;

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

import jakarta.ws.rs.DefaultValue;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.QueryParam;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

@Path("/api")
public class ProjectController {

    @GET
    @Path("/")
    @Produces(MediaType.TEXT_PLAIN)
    public Response get() {
        return Response.ok().build();
    }

    @GET
    @Path("/getCase")
    @Produces(MediaType.APPLICATION_JSON)
    public Response getCase(@QueryParam("page") @DefaultValue("1") int page, 
                               @QueryParam("size") @DefaultValue("20") int size,
                               @QueryParam("config") @DefaultValue("") String configJson) {

        ObjectMapper objectMapper = new ObjectMapper();
        objectMapper.configure(MapperFeature.ACCEPT_CASE_INSENSITIVE_PROPERTIES, true);

        ConfigContract config = null;

        try {
            if (!configJson.isEmpty()) {
                config = objectMapper.readValue(configJson, ConfigContract.class);
            }
        } catch (IOException e) {
            return Response.status(Response.Status.BAD_REQUEST)
                           .entity("Erreur de parsing du JSON de configuration : " + e.getMessage())
                           .build();
        }

        try (InputStream inputStream = getClass().getClassLoader().getResourceAsStream("case_data.json")) {

            if (inputStream == null) {
                return Response.status(Response.Status.NOT_FOUND)
                               .entity("Fichier JSON introuvable.")
                               .build();
            }

            List<CaseContract> cases = objectMapper.readValue(inputStream, new TypeReference<List<CaseContract>>() {});

            int start = (page - 1) * size;
            int end = Math.min(start + size, cases.size());
            
            if (start >= cases.size()) {
                return Response.status(Response.Status.BAD_REQUEST)
                        .entity("Page demandée trop grande. Il n'y a pas assez d'éléments.")
                        .build();
            }

            List<CaseContract> pageData = cases.subList(start, end);

            return Response.ok(pageData).build();

        } catch (IOException e) {
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
                           .entity("Erreur de lecture du fichier JSON : " + e.getMessage())
                           .build();
        }
    }

    @GET
    @Path("/getCPU")
    @Produces(MediaType.APPLICATION_JSON)
    public Response getCPU(@QueryParam("page") @DefaultValue("1") int page, 
                            @QueryParam("size") @DefaultValue("20") int size,
                            @QueryParam("config") @DefaultValue("") String configJson) {

        ObjectMapper objectMapper = new ObjectMapper();
        objectMapper.configure(MapperFeature.ACCEPT_CASE_INSENSITIVE_PROPERTIES, true);

        ConfigContract config = null;

        try {
            if (!configJson.isEmpty()) {
                config = objectMapper.readValue(configJson, ConfigContract.class);
            }
        } catch (IOException e) {
            return Response.status(Response.Status.BAD_REQUEST)
                           .entity("Erreur de parsing du JSON de configuration : " + e.getMessage())
                           .build();
        }

        try (InputStream inputStream = getClass().getClassLoader().getResourceAsStream("cpu_data.json")) {

            if (inputStream == null) {
                return Response.status(Response.Status.NOT_FOUND)
                               .entity("Fichier JSON introuvable.")
                               .build();
            }

            List<CPUContract> cases = objectMapper.readValue(inputStream, new TypeReference<List<CPUContract>>() {});

            int start = (page - 1) * size;
            int end = Math.min(start + size, cases.size());
            
            if (start >= cases.size()) {
                return Response.status(Response.Status.BAD_REQUEST)
                        .entity("Page demandée trop grande. Il n'y a pas assez d'éléments.")
                        .build();
            }

            List<CPUContract> pageData = cases.subList(start, end);

            return Response.ok(pageData).build();

        } catch (IOException e) {
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
                           .entity("Erreur de lecture du fichier JSON : " + e.getMessage())
                           .build();
        }
    }

    @GET
    @Path("/getCPUCooler")
    @Produces(MediaType.APPLICATION_JSON)
    public Response getCPUCooler(@QueryParam("page") @DefaultValue("1") int page, 
                                  @QueryParam("size") @DefaultValue("20") int size,
                                  @QueryParam("config") @DefaultValue("") String configJson) {

        ObjectMapper objectMapper = new ObjectMapper();
        objectMapper.configure(MapperFeature.ACCEPT_CASE_INSENSITIVE_PROPERTIES, true);

        ConfigContract config = null;

        try {
            if (!configJson.isEmpty()) {
                config = objectMapper.readValue(configJson, ConfigContract.class);
            }
        } catch (IOException e) {
            return Response.status(Response.Status.BAD_REQUEST)
                           .entity("Erreur de parsing du JSON de configuration : " + e.getMessage())
                           .build();
        }

        try (InputStream inputStream = getClass().getClassLoader().getResourceAsStream("cpu-cooler_data.json")) {

            if (inputStream == null) {
                return Response.status(Response.Status.NOT_FOUND)
                               .entity("Fichier JSON introuvable.")
                               .build();
            }

            List<CPUCoolerContract> cases = objectMapper.readValue(inputStream, new TypeReference<List<CPUCoolerContract>>() {});

            int start = (page - 1) * size;
            int end = Math.min(start + size, cases.size());
            
            if (start >= cases.size()) {
                return Response.status(Response.Status.BAD_REQUEST)
                        .entity("Page demandée trop grande. Il n'y a pas assez d'éléments.")
                        .build();
            }

            List<CPUCoolerContract> pageData = cases.subList(start, end);

            return Response.ok(pageData).build();

        } catch (IOException e) {
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
                           .entity("Erreur de lecture du fichier JSON : " + e.getMessage())
                           .build();
        }
    }

    @GET
    @Path("/getMemory")
    @Produces(MediaType.APPLICATION_JSON)
    public Response getMemory(@QueryParam("page") @DefaultValue("1") int page, 
                               @QueryParam("size") @DefaultValue("20") int size,
                               @QueryParam("config") @DefaultValue("") String configJson) {

        ObjectMapper objectMapper = new ObjectMapper();
        objectMapper.configure(MapperFeature.ACCEPT_CASE_INSENSITIVE_PROPERTIES, true);

        ConfigContract config = null;

        try {
            if (!configJson.isEmpty()) {
                config = objectMapper.readValue(configJson, ConfigContract.class);
            }
        } catch (IOException e) {
            return Response.status(Response.Status.BAD_REQUEST)
                           .entity("Erreur de parsing du JSON de configuration : " + e.getMessage())
                           .build();
        }

        try (InputStream inputStream = getClass().getClassLoader().getResourceAsStream("memory_data.json")) {

            if (inputStream == null) {
                return Response.status(Response.Status.NOT_FOUND)
                               .entity("Fichier JSON introuvable.")
                               .build();
            }

            List<MemoryContract> cases = objectMapper.readValue(inputStream, new TypeReference<List<MemoryContract>>() {});

            int start = (page - 1) * size;
            int end = Math.min(start + size, cases.size());
            
            if (start >= cases.size()) {
                return Response.status(Response.Status.BAD_REQUEST)
                        .entity("Page demandée trop grande. Il n'y a pas assez d'éléments.")
                        .build();
            }

            List<MemoryContract> pageData = cases.subList(start, end);

            return Response.ok(pageData).build();

        } catch (IOException e) {
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
                           .entity("Erreur de lecture du fichier JSON : " + e.getMessage())
                           .build();
        }
    }

    @GET
    @Path("/getPowerSupply")
    @Produces(MediaType.APPLICATION_JSON)
    public Response getPowerSupply(@QueryParam("page") @DefaultValue("1") int page, 
                                   @QueryParam("size") @DefaultValue("20") int size,
                                   @QueryParam("config") @DefaultValue("") String configJson) {

        ObjectMapper objectMapper = new ObjectMapper();
        objectMapper.configure(MapperFeature.ACCEPT_CASE_INSENSITIVE_PROPERTIES, true);

        ConfigContract config = null;

        try {
            if (!configJson.isEmpty()) {
                config = objectMapper.readValue(configJson, ConfigContract.class);
            }
        } catch (IOException e) {
            return Response.status(Response.Status.BAD_REQUEST)
                           .entity("Erreur de parsing du JSON de configuration : " + e.getMessage())
                           .build();
        }

        try (InputStream inputStream = getClass().getClassLoader().getResourceAsStream("power-supply_data.json")) {

            if (inputStream == null) {
                return Response.status(Response.Status.NOT_FOUND)
                               .entity("Fichier JSON introuvable.")
                               .build();
            }

            List<PowerSupplyContract> cases = objectMapper.readValue(inputStream, new TypeReference<List<PowerSupplyContract>>() {});

            int start = (page - 1) * size;
            int end = Math.min(start + size, cases.size());
            
            if (start >= cases.size()) {
                return Response.status(Response.Status.BAD_REQUEST)
                        .entity("Page demandée trop grande. Il n'y a pas assez d'éléments.")
                        .build();
            }

            List<PowerSupplyContract> pageData = cases.subList(start, end);

            return Response.ok(pageData).build();

        } catch (IOException e) {
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
                           .entity("Erreur de lecture du fichier JSON : " + e.getMessage())
                           .build();
        }
    }

    @GET
    @Path("/getVideoCard")
    @Produces(MediaType.APPLICATION_JSON)
    public Response getVideoCard(@QueryParam("page") @DefaultValue("1") int page, 
                                 @QueryParam("size") @DefaultValue("20") int size,
                                 @QueryParam("config") @DefaultValue("") String configJson) {

        ObjectMapper objectMapper = new ObjectMapper();
        objectMapper.configure(MapperFeature.ACCEPT_CASE_INSENSITIVE_PROPERTIES, true);

        ConfigContract config = null;

        try {
            if (!configJson.isEmpty()) {
                config = objectMapper.readValue(configJson, ConfigContract.class);
            }
        } catch (IOException e) {
            return Response.status(Response.Status.BAD_REQUEST)
                           .entity("Erreur de parsing du JSON de configuration : " + e.getMessage())
                           .build();
        }

        try (InputStream inputStream = getClass().getClassLoader().getResourceAsStream("video-card_data.json")) {

            if (inputStream == null) {
                return Response.status(Response.Status.NOT_FOUND)
                               .entity("Fichier JSON introuvable.")
                               .build();
            }

            List<VideoCardContract> cases = objectMapper.readValue(inputStream, new TypeReference<List<VideoCardContract>>() {});

            int start = (page - 1) * size;
            int end = Math.min(start + size, cases.size());
            
            if (start >= cases.size()) {
                return Response.status(Response.Status.BAD_REQUEST)
                        .entity("Page demandée trop grande. Il n'y a pas assez d'éléments.")
                        .build();
            }

            List<VideoCardContract> pageData = cases.subList(start, end);

            return Response.ok(pageData).build();

        } catch (IOException e) {
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
                           .entity("Erreur de lecture du fichier JSON : " + e.getMessage())
                           .build();
        }
    }

    @GET
    @Path("/getCompatibleComponents")
    @Produces(MediaType.APPLICATION_JSON)
    public Response getCompatibleComponents() {
        Model model = new Model("CPU & Motherboard Compatibility");

        // Données du CPU et de la carte mère
        String cpuSocket = "AM5";
        String cpuArchitecture = "Zen 4";
        String motherboardSocket = "AM5";
        String motherboardSupportedArchitecture = "Zen 5"; 

        // Vérification de compatibilité
        BoolVar socketCompatible = model.boolVar(cpuSocket.equals(motherboardSocket));
        BoolVar architectureCompatible = model.boolVar(cpuArchitecture.equals(motherboardSupportedArchitecture));

        // Création de l'objet réponse
        CompatibilityResponse response = new CompatibilityResponse();
        response.socketCompatible = socketCompatible.getValue() == 1;
        response.architectureCompatible = architectureCompatible.getValue() == 1;

        // Définition du message final
        response.message = (response.socketCompatible && response.architectureCompatible) 
            ? "Le CPU est compatible avec la carte mère !" 
            : "Le CPU n'est pas compatible avec la carte mère.";

        // Retourner l'objet JSON
        return Response.ok(response).build();
    }

    // Classe pour la réponse JSON
    public static class CompatibilityResponse {
        public boolean socketCompatible;
        public boolean architectureCompatible;
        public String message;
    }
}
