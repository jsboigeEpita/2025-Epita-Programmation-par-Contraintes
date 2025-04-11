package fr.matthieufouliard.service;

import fr.matthieufouliard.controller.QuoridorController;
import fr.matthieufouliard.model.*;
import fr.matthieufouliard.model.Respond.CreateGameRespond;
import fr.matthieufouliard.model.Respond.CreateUserRespond;
import fr.matthieufouliard.model.Respond.GetGameRespond;
import fr.matthieufouliard.repository.Games;
import fr.matthieufouliard.repository.Players;
import io.quarkus.scheduler.Scheduled;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import org.jboss.logging.Logger;

import java.util.*;

@ApplicationScoped
public class QuoridorService {
    
    @Inject
    Games games;
    
    @Inject
    Players players;

    @Inject
    AIService aiService;

    private static final Logger logger = Logger.getLogger(QuoridorController.class);

    private final static UUID AIUUID = UUID.fromString("00000000-0000-0000-0000-000000000000");
    
    public CreateUserRespond createUser(String username) {
        return new CreateUserRespond(this.players.createPlayer(username));
    }

    public CreateGameRespond createGame(UUID playerID, Integer size, Integer nbWalls, TurnStart turnStart, Boolean ai) {
        int playerNb;
        if (turnStart == TurnStart.NONE) {
            playerNb = (int) Math.round(Math.random());
        } else if (turnStart == TurnStart.FIRST) {
            playerNb = 0;
        }
        else {
            playerNb = 1;
        }

        UUID[] players = new UUID[]{ null, null };
        players[playerNb] = playerID;
        if (ai) {
            players[(playerNb + 1) % 2] = AIUUID;
        }

        return new CreateGameRespond(this.games.createGame(players, size, nbWalls));
    }
    
    public Boolean doesPlayerExist(UUID playerID) {
        return this.players.getUsername(playerID) != null;
    }

    public Boolean doesGameExist(UUID gameID) {
        return this.games.getGame(gameID) != null;
    }

    private Boolean isWaiting(GetGameRespond getGameRespond) {
        return getGameRespond.usernames[0] == null || getGameRespond.usernames[1] == null;
    }

    private Boolean isRunning(GetGameRespond getGameRespond) {
        return getGameRespond.winner == Winner.NONE;
    }

    private Boolean isOver(GetGameRespond getGameRespond) {
        return getGameRespond.winner != Winner.NONE;
    }

    private int compareDate(GetGameRespond getGameRespond1, GetGameRespond getGameRespond2) {
        long creationDate1 = games.getGame(getGameRespond1.UUID).getCreationDate();
        long creationDate2 = games.getGame(getGameRespond2.UUID).getCreationDate();
        return creationDate1 < creationDate2 ? 1 : -1;
    }

    public int compareGameResponds(GetGameRespond getGameRespond1, GetGameRespond getGameRespond2) {
        if (isWaiting(getGameRespond1)) {
            return isWaiting(getGameRespond2) ? compareDate(getGameRespond1, getGameRespond2) : -1;
        }
        else if (isRunning(getGameRespond1)) {
            if (isWaiting(getGameRespond2)) {
                return 1;
            }
            else if (isRunning(getGameRespond2)) {
                return compareDate(getGameRespond1, getGameRespond2);
            }
            else {
                return -1;
            }
        }
        else {
            return isOver(getGameRespond2) ? compareDate(getGameRespond1, getGameRespond2) : 1;
        }
    }

    public List<GetGameRespond> getGames(UUID playerID) {
        Map<UUID, Game> games = this.games.getGames();
        List<GetGameRespond> getGameResponds = new ArrayList<>(games.keySet().stream().map(
                gameID -> getGame(playerID, gameID)).toList());
        getGameResponds.sort(this::compareGameResponds);

        return getGameResponds;
    }

    public GetGameRespond getGame(UUID playerID, UUID gameID) {
        Game game = this.games.getGame(gameID);
        UUID[] players = game.getPlayers();
        String[] usernames = Arrays.stream(players).map(player -> this.players.getUsername(player))
                .toArray(String[]::new);
        Board board = game.getBoard();
        Boolean isYourTurn = playerID.equals(players[Board.turnToInteger.get(game.getBoard().getTurn())]);
        Winner winner = game.getWinner();
        return new GetGameRespond(gameID, usernames, board, isYourTurn, winner);
    }

    public Boolean join(UUID playerID, UUID gameID) {
        Game game = this.games.getGame(gameID);

        for (int i = 0; i < 2; i++) {
            if (game.getPlayers()[i] != null && game.getPlayers()[i].equals(playerID)) {
                return false;
            }
        }

        for (int i = 0; i < 2; i++) {
            if (game.getPlayers()[i] == null) {
                game.getPlayers()[i] = playerID;
                game.setLastUpdateDate();
                return true;
            }
        }

        return false;
    }

    public Boolean move(UUID playerID, UUID gameID, Direction direction, Boolean jump) {
        Game game = this.games.getGame(gameID);
        UUID[] players = game.getPlayers();
        if (!playerID.equals(players[Board.turnToInteger.get(game.getBoard().getTurn())])) {
            return false;
        }

        if (game.getWinner() != Winner.NONE) {
            return false;
        }

        if (players[0] == null || players[1] == null) {
            return false;
        }

        Boolean hasMoved = game.getBoard().move(direction, jump);
        if (hasMoved) {
            game.setWinner(game.getBoard().hasWon());
            game.setLastUpdateDate();
        }
        return hasMoved;
    }

    public Boolean place(UUID playerID, UUID gameID, Integer x, Integer y, Wall wall) {
        Game game = this.games.getGame(gameID);
        UUID[] players = game.getPlayers();
        if (!playerID.equals(players[Board.turnToInteger.get(game.getBoard().getTurn())])) {
            return false;
        }

        if (game.getWinner() != Winner.NONE) {
            return false;
        }

        if (players[0] == null || players[1] == null) {
            return false;
        }

        Boolean hasPlaced = game.getBoard().place(new Coordinate(x, y), wall);
        if (hasPlaced) {
            game.setLastUpdateDate();
        }

        return hasPlaced;
    }

    @Scheduled(every = "60s")
    public void clearDead() {
        this.games.clearDead();
    }

    @Scheduled(every = "2s")
    public void AIPlay() {
        this.games.getGames().forEach((UUID, game) -> {
            if ((game.getPlayers()[0] == AIUUID && game.getBoard().getTurn() == Turn.PLAYER_1) ||
                    (game.getPlayers()[1] == AIUUID && game.getBoard().getTurn() == Turn.PLAYER_2)) {
                logger.info("The AI is trying to play.");
                AIPlay aiPlay = aiService.play(game.getBoard());
                if (aiPlay.getValid()) {
                    if (aiPlay.getMove()) {
                        if (!move(AIUUID, UUID, aiPlay.getDirection(), aiPlay.getJump())) {
                            logger.error("The AI move was incorrect.");
                        } else {
                            logger.info("The AI moved successfully.");
                        }
                    } else {
                        if (place(AIUUID, UUID, aiPlay.getX(), aiPlay.getY(), aiPlay.getWall())) {
                            logger.error("The AI place was incorrect.");
                        } else {
                            logger.info("The AI placed successfully.");
                        }
                    }
                } else {
                    logger.error("Could not get AI data.");
                }
            }
        });
    }
}