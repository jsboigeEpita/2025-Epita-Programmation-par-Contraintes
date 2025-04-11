package fr.matthieufouliard.model.Request;

import fr.matthieufouliard.model.TurnStart;

public class CreateGameRequest {
    public Integer size;
    public Integer nbWalls;
    public TurnStart turnStart;
    public Boolean ai;

    @Override
    public String toString() {
        return "{\n" +
                "size: " + this.size + "\n" +
                "nbWalls: " + this.nbWalls + "\n" +
                "turnStart: " + this.turnStart + "\n" +
                "ai: " + this.ai + "\n" +
                "}";
    }
}
