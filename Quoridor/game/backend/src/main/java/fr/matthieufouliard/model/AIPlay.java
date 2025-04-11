package fr.matthieufouliard.model;

public class AIPlay {
    private final Boolean isValid;
    private final Boolean isMove;
    private final Direction direction;
    private final Boolean jump;
    private final Integer x;
    private final Integer y;
    private final Wall wall;

    public AIPlay() {
        this.isValid = false;
        this.isMove = null;
        this.direction = null;
        this.jump = null;
        this.x = null;
        this.y = null;
        this.wall = null;
    }

    public AIPlay(Direction direction, Boolean jump) {
        this.isValid = true;
        this.isMove = true;
        this.direction = direction;
        this.jump = jump;
        this.x = null;
        this.y = null;
        this.wall = null;
    }

    public AIPlay(Integer x, Integer y, Wall wall) {
        this.isValid = true;
        this.isMove = false;
        this.direction = null;
        this.jump = null;
        this.x = x;
        this.y = y;
        this.wall = wall;
    }

    public Boolean getValid() {
        return this.isValid;
    }

    public Boolean getMove() {
        return this.isMove;
    }

    public Direction getDirection() {
        return this.direction;
    }

    public Boolean getJump() {
        return this.jump;
    }

    public Integer getX() {
        return this.x;
    }

    public Integer getY() {
        return this.y;
    }

    public Wall getWall() {
        return this.wall;
    }
}
