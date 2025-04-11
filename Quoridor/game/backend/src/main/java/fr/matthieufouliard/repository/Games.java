package fr.matthieufouliard.repository;

import fr.matthieufouliard.model.Game;
import jakarta.enterprise.context.ApplicationScoped;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@ApplicationScoped
public class Games {
    private final Map<UUID, Game> games;
    private final static int inactivityTime = 1000 * 60 * 10;

    public Games() {
        this.games = new HashMap<>();
    }

    public Map<UUID, Game> getGames() {
        return this.games;
    }

    public UUID createGame(UUID[] players, Integer size, Integer nbWalls) {
        UUID UUID = java.util.UUID.randomUUID();
        this.games.put(UUID, new Game(players, size, nbWalls));
        return UUID;
    }

    public Game getGame(UUID UUID) {
        return this.games.get(UUID);
    }

    public void clearDead() {
        games.entrySet().removeIf((entry) ->
                entry.getValue().getLastUpdateDate() + inactivityTime < System.currentTimeMillis()
        );
    }
}
