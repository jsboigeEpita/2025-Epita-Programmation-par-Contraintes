package fr.matthieufouliard.model;

import java.util.Map;

public class Coordinate {
    private Integer x;
    private Integer y;

    public Coordinate(Integer x, Integer y) {
        this.x = x;
        this.y = y;
    }

    public Coordinate(Coordinate coordinate) {
        this.x = coordinate.x;
        this.y = coordinate.y;
    }

    public final static Map<Direction, Coordinate> directionToCoordinate = Map.of(
            Direction.UP, new Coordinate(-1, 0),
            Direction.RIGHT, new Coordinate(0, 1),
            Direction.DOWN, new Coordinate(1, 0),
            Direction.LEFT, new Coordinate(0, -1)
    );

    public void add(Coordinate vector) {
        this.x = this.x + vector.x;
        this.y = this.y + vector.y;
    }

    public void sub(Coordinate position) {
        this.x = this.x - position.x;
        this.y = this.y - position.y;
    }

    public Integer getX() {
        return this.x;
    }

    public Integer getY() {
        return this.y;
    }

    @Override
    public boolean equals(Object obj) {
        if (obj == null || this.getClass() != obj.getClass()) {
            return false;
        }
        Coordinate coordinate = (Coordinate) obj;
        return this.x.equals(coordinate.x) && this.y.equals(coordinate.y);
    }

    @Override
    public int hashCode() {
        return 31 * x.hashCode() + y.hashCode();
    }

    public Direction toDirection() {
        for (Map.Entry<Direction, Coordinate> entry: directionToCoordinate.entrySet()) {
            if (entry.getValue().equals(this)) {
                return entry.getKey();
            }
        }

        return null;
    }
}
