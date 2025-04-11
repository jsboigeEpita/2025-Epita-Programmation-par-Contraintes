package fr.matthieufouliard.model.Request;

import fr.matthieufouliard.model.Direction;

public class MoveRequest {
    public Direction direction;
    public Boolean jump;

    @Override
    public String toString() {
        return "{\n" +
                "direction: " + this.direction + "\n" +
                "jump: " + this.jump + "\n" +
                "}";
    }
}
