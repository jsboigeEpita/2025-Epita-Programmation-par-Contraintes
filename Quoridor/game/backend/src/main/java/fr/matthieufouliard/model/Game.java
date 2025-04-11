package fr.matthieufouliard.model;

import java.util.UUID;

public class Game {
    private final UUID[] players;
    private final Board board;
    private Winner winner;
    private final long creationDate;
    private long lastUpdateDate;

    public Game(UUID[] players, Integer size, Integer nbWalls) {
        this.players = players;
        this.board = new Board(size, nbWalls);
        this.winner = Winner.NONE;
        this.creationDate = System.currentTimeMillis();
        this.lastUpdateDate = System.currentTimeMillis();
    }

    public UUID[] getPlayers() {
        return this.players;
    }

    public Board getBoard() {
        return this.board;
    }

    public Winner getWinner() {
        return this.winner;
    }

    public long getCreationDate() {
        return this.creationDate;
    }

    public long getLastUpdateDate() {
        return this.lastUpdateDate;
    }

    public void setWinner(Winner winner) {
        this.winner = winner;
    }

    public void setLastUpdateDate() {
        this.lastUpdateDate = System.currentTimeMillis();
    }
}
