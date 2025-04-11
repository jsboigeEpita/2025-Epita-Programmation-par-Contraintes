package fr.matthieufouliard.model.Request;

import fr.matthieufouliard.model.Wall;

public class PlaceRequest {
    public Integer x;
    public Integer y;
    public Wall wall;

    @Override
    public String toString() {
        return "{\n" +
                "x: " + this.x + "\n" +
                "y: " + this.y + "\n" +
                "wall: " + this.wall + "\n" +
                "}";
    }
}
