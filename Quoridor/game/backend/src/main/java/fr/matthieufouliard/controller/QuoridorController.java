package fr.matthieufouliard.controller;

import fr.matthieufouliard.model.Request.CreateGameRequest;
import fr.matthieufouliard.model.Request.CreateUserRequest;
import fr.matthieufouliard.model.Request.MoveRequest;
import fr.matthieufouliard.model.Request.PlaceRequest;
import fr.matthieufouliard.service.QuoridorService;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

import org.jboss.logging.Logger;

import java.util.UUID;

@Path("/")
@Consumes(MediaType.APPLICATION_JSON)
@Produces(MediaType.APPLICATION_JSON)
@ApplicationScoped
public class QuoridorController {

    @Inject
    QuoridorService quoridorService;

    private static final Logger logger = Logger.getLogger(QuoridorController.class);

    @POST
    @Path("/user")
    public Response createUser(CreateUserRequest createUserRequest) {
        logger.info("Received a request to create a user.");
        if (createUserRequest == null || createUserRequest.username == null) {
            logger.info("The request is empty or missing a field. Returning 400.");
            return Response.status(400).build();
        }
        if (createUserRequest.username.isBlank() ||
                createUserRequest.username.trim().length() < 3 || createUserRequest.username.trim().length() > 20) {
            logger.info("The username is not valid. Returning 400.");
            return Response.status(400).build();
        }

        logger.info("The Request is valid. Returning 200.");
        return Response.ok(this.quoridorService.createUser(createUserRequest.username)).build();
    }

    @POST
    @Path("/game")
    public Response createGame(@HeaderParam("X-Player-UUID") UUID PlayerID, CreateGameRequest createGameRequest) {
        logger.info("Received a request to create a game.");
        if (PlayerID == null || !this.quoridorService.doesPlayerExist(PlayerID)) {
            logger.info("The player UUID is not valid. Returning 400.");
            return Response.status(400).build();
        }
        if (createGameRequest == null || createGameRequest.size == null ||
                createGameRequest.nbWalls == null || createGameRequest.turnStart == null ||
                createGameRequest.ai == null ) {
            logger.info("The request is empty or missing a field. Returning 400.");
            return Response.status(400).build();
        }
        if (createGameRequest.size < 2 || 9 < createGameRequest.size) {
            logger.info("The size is not valid. Returning 400.");
            return Response.status(400).build();
        }
        if (createGameRequest.nbWalls < 0 || 10 < createGameRequest.nbWalls) {
            logger.info("The number of walls is not valid. Returning 400.");
            return Response.status(400).build();
        }

        logger.info("The Request is valid. Returning 200.");
        return Response.ok(this.quoridorService.createGame(
                PlayerID,
                createGameRequest.size,
                createGameRequest.nbWalls,
                createGameRequest.turnStart,
                createGameRequest.ai)
        ).build();
    }

    @GET
    @Path("/games")
    public Response getGames(@HeaderParam("X-Player-UUID") UUID playerID) {
        logger.info("Received a request to get all games.");
        if (playerID == null || !this.quoridorService.doesPlayerExist(playerID)) {
            logger.info("The player UUID is not valid. Returning 400.");
            return Response.status(400).build();
        }

        logger.info("The Request is valid. Returning 200.");
        return Response.ok(this.quoridorService.getGames(playerID)).build();
    }

    @GET
    @Path("/game/{UUID}")
    public Response getGame(@HeaderParam("X-Player-UUID") UUID playerID, @PathParam("UUID") UUID gameID) {
        logger.info("Received a request to get a game.");
        if (playerID == null || !this.quoridorService.doesPlayerExist(playerID)) {
            logger.info("The player UUID is not valid. Returning 400.");
            return Response.status(400).build();
        }

        if (gameID == null || !this.quoridorService.doesGameExist(gameID)) {
            logger.info("The game UUID is not valid. Returning 404.");
            return Response.status(404).build();
        }

        logger.info("The Request is valid. Returning 200.");
        return Response.ok(this.quoridorService.getGame(playerID, gameID)).build();
    }

    @POST
    @Path("/game/{UUID}/join")
    public Response joinGame(@HeaderParam("X-Player-UUID") UUID playerID, @PathParam("UUID") UUID gameID) {
        logger.info("Received a request to join a game.");
        if (playerID == null || !this.quoridorService.doesPlayerExist(playerID)) {
            logger.info("The player UUID is not valid. Returning 400.");
            return Response.status(400).build();
        }

        if (gameID == null || !this.quoridorService.doesGameExist(gameID)) {
            logger.info("The game UUID is not valid. Returning 404.");
            return Response.status(404).build();
        }

        if (!this.quoridorService.join(playerID, gameID)) {
            logger.info("Could not join the game. Returning 400.");
            return Response.status(400).build();
        }

        logger.info("The Request is valid. Returning 200.");
        return Response.ok().build();
    }

    @POST
    @Path("/game/{UUID}/move")
    public Response move(@HeaderParam("X-Player-UUID") UUID playerID,
                         @PathParam("UUID") UUID gameID, MoveRequest moveRequest) {
        logger.info("Received a request to move.");
        if (playerID == null || !this.quoridorService.doesPlayerExist(playerID)) {
            logger.info("The player UUID is not valid. Returning 400.");
            return Response.status(400).build();
        }

        if (gameID == null || !this.quoridorService.doesGameExist(gameID)) {
            logger.info("The game UUID is not valid. Returning 404.");
            return Response.status(404).build();
        }

        if (moveRequest == null || moveRequest.direction == null) {
            logger.info("The request is empty or missing a field. Returning 400.");
            return Response.status(400).build();
        }

        if (!this.quoridorService.move(playerID, gameID, moveRequest.direction, moveRequest.jump)) {
            logger.info("Move action is not valid. Returning 400.");
            return Response.status(400).build();
        }

        logger.info("The Request is valid. Returning 200.");
        return Response.ok().build();
    }

    @POST
    @Path("/game/{UUID}/place")
    public Response place(@HeaderParam("X-Player-UUID") UUID playerID,
                         @PathParam("UUID") UUID gameID, PlaceRequest placeRequest) {
        logger.info("Received a request to place.");
        if (playerID == null || !this.quoridorService.doesPlayerExist(playerID)) {
            logger.info("The player UUID is not valid. Returning 400.");
            return Response.status(400).build();
        }

        if (gameID == null || !this.quoridorService.doesGameExist(gameID)) {
            logger.info("The game UUID is not valid. Returning 404.");
            return Response.status(404).build();
        }

        if (placeRequest == null || placeRequest.x == null || placeRequest.y == null || placeRequest.wall == null) {
            logger.info("The request is empty or missing a field. Returning 400.");
            return Response.status(400).build();
        }

        if (!this.quoridorService.place(playerID, gameID, placeRequest.x, placeRequest.y, placeRequest.wall)) {
            logger.info("Place action is not valid. Returning 400.");
            return Response.status(400).build();
        }

        logger.info("The Request is valid. Returning 200.");
        return Response.ok().build();
    }
}
