package fr.matthieufouliard.model.Respond;

import fr.matthieufouliard.model.Board;
import fr.matthieufouliard.model.Winner;

import java.util.Arrays;
import java.util.UUID;

public class GetGameRespond {
    public UUID UUID;
    public String[] usernames;
    public Board board;
    public Boolean isYourTurn;
    public Winner winner;

    public GetGameRespond(UUID UUID, String[] usernames, Board board, Boolean isYourTurn, Winner winner) {
        this.UUID = UUID;
        this.usernames = usernames;
        this.board = board;
        this.isYourTurn = isYourTurn;
        this.winner = winner;
    }

    @Override
    public String toString() {
        return "{\n" +
                "UUID: " + this.UUID + "\n" +
                "usernames: " + Arrays.toString(this.usernames) + "\n" +
                "nbWalls: " + this.board + "\n" +
                "isYourTurn: " + this.isYourTurn + "\n" +
                "}";
    }
}
