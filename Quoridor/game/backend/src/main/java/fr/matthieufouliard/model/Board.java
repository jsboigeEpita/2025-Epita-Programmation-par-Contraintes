package fr.matthieufouliard.model;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.function.Predicate;

public class Board {
    private final Integer size;
    private final Wall[][] walls;
    private final Coordinate[] positions;
    private final Integer[] nbWalls;
    private Turn turn;

    public Board(Integer size, Integer nbWalls) {
        this.size = size;
        this.walls = new Wall[this.size - 1][this.size - 1];

        for (int i = 0; i < this.size - 1; i++) {
            for (int j = 0; j < this.size - 1; j++) {
                this.walls[i][j] = Wall.NONE;
            }
        }

        Coordinate positionPlayer1 = new Coordinate(this.size - 1, (this.size - 1) / 2);
        Coordinate positionPlayer2 = new Coordinate(0, this.size / 2);
        this.positions = new Coordinate[]{ positionPlayer1, positionPlayer2 };
        this.nbWalls = new Integer[]{ nbWalls, nbWalls };
        this.turn = Turn.PLAYER_1;
    }

    public Board(Board board) {
        this.size = board.size;
        this.walls = new Wall[this.size - 1][this.size - 1];

        for (int i = 0; i < this.size - 1; i++) {
            System.arraycopy(board.walls[i], 0, this.walls[i], 0, this.size - 1);
        }

        this.positions = new Coordinate[]{ new Coordinate(board.positions[0]), new Coordinate(board.positions[1]) };
        this.nbWalls = new Integer[]{ board.nbWalls[0], board.nbWalls[1] };
        this.turn = board.turn;
    }

    public Integer getSize() {
        return this.size;
    }

    public Wall[][] getWalls() {
        return this.walls;
    }

    public Coordinate[] getPositions() {
        return this.positions;
    }

    public Integer[] getNbWalls() {
        return this.nbWalls;
    }

    public Turn getTurn() {
        return this.turn;
    }

    public Winner hasWon() {
        if (positions[0].getX() == 0) {
            return Winner.PLAYER_1;
        }
        if (positions[1].getX() == size - 1) {
            return Winner.PLAYER_2;
        }

        return Winner.NONE;
    }

    public final static Map<Turn, Integer> turnToInteger = Map.of(
            Turn.PLAYER_1, 0,
            Turn.PLAYER_2, 1
    );

    private Boolean isInBoard(Coordinate position) {
        return 0 <= position.getX() && position.getX() < this.size &&
                0 <= position.getY() && position.getY() < this.size;
    }

    private Boolean isWallUp(Coordinate coordinate) {
        if (coordinate.getX() != 0 && coordinate.getY() != 0 &&
                this.walls[coordinate.getX() - 1][coordinate.getY() - 1] == Wall.HORIZONTAL) {
            return true;
        }

        return coordinate.getX() != 0 && coordinate.getY() != this.size - 1 &&
                this.walls[coordinate.getX() - 1][coordinate.getY()] == Wall.HORIZONTAL;
    }

    private Boolean isWallRight(Coordinate coordinate) {
        if (coordinate.getX() != 0 && coordinate.getY() != this.size - 1 &&
                this.walls[coordinate.getX() - 1][coordinate.getY()] == Wall.VERTICAL) {
            return true;
        }

        return coordinate.getX() != this.size - 1 && coordinate.getY() != this.size - 1 &&
                this.walls[coordinate.getX()][coordinate.getY()] == Wall.VERTICAL;
    }

    private Boolean isWallDown(Coordinate coordinate) {
        if (coordinate.getX() != this.size - 1 && coordinate.getY() != this.size - 1 &&
                this.walls[coordinate.getX()][coordinate.getY()] == Wall.HORIZONTAL) {
            return true;
        }

        return coordinate.getX() != this.size - 1 && coordinate.getY() != 0 &&
                this.walls[coordinate.getX()][coordinate.getY() - 1] == Wall.HORIZONTAL;
    }

    private Boolean isWallLeft(Coordinate coordinate) {
        if (coordinate.getX() != this.size - 1 && coordinate.getY() != 0 &&
                this.walls[coordinate.getX()][coordinate.getY() - 1] == Wall.VERTICAL) {
            return true;
        }

        return coordinate.getX() != 0 && coordinate.getY() != 0 &&
                this.walls[coordinate.getX() - 1][coordinate.getY() - 1] == Wall.VERTICAL;
    }

    private final Map<Direction, Predicate<Coordinate>> directionToIsWall = Map.of(
            Direction.UP, this::isWallUp,
            Direction.RIGHT, this::isWallRight,
            Direction.DOWN, this::isWallDown,
            Direction.LEFT, this::isWallLeft
    );

    private final Map<Direction, Direction> oppositeDirection = Map.of(
            Direction.UP, Direction.DOWN,
            Direction.RIGHT, Direction.LEFT,
            Direction.DOWN, Direction.UP,
            Direction.LEFT, Direction.RIGHT
    );

    private Boolean canSimpleMove(Coordinate position, Direction direction) {
        if (this.directionToIsWall.get(direction).test(position)) {
            return false;
        }

        Coordinate projectionPosition = new Coordinate(position);
        projectionPosition.add(Coordinate.directionToCoordinate.get(direction));
        return isInBoard(projectionPosition);
    }

    private Boolean canMove(Direction direction, Boolean jump) {
        Coordinate playerCoordinate = this.positions[turnToInteger.get(this.turn)];
        Coordinate provisionalPosition = new Coordinate(playerCoordinate);
        if (jump) {
            Coordinate difference = new Coordinate(this.positions[(turnToInteger.get(this.turn) + 1) % 2]);
            difference.sub(provisionalPosition);

            if (difference.getX() * difference.getX() + difference.getY() * difference.getY() != 1) {
                return false;
            }

            Direction differenceDirection = difference.toDirection();
            if (oppositeDirection.get(differenceDirection).equals(direction)) {
                return false;
            }

            if (this.directionToIsWall.get(differenceDirection).test(provisionalPosition)) {
                return false;
            }
            provisionalPosition.add(difference);

            if (canSimpleMove(provisionalPosition, differenceDirection)) {
                return differenceDirection.equals(direction);
            }
        }

        if (!canSimpleMove(provisionalPosition, direction)) {
            return false;
        }
        provisionalPosition.add(Coordinate.directionToCoordinate.get(direction));
        return !provisionalPosition.equals(this.positions[(turnToInteger.get(this.turn) + 1) % 2]);
    }

    public Boolean move(Direction direction, Boolean jump) {
        if (!canMove(direction, jump)) {
            return false;
        }

        if (jump) {
            Coordinate difference = new Coordinate(this.positions[(turnToInteger.get(this.turn) + 1) % 2]);
            difference.sub(this.positions[turnToInteger.get(this.turn)]);

            this.positions[turnToInteger.get(this.turn)].add(difference);
        }

        this.positions[turnToInteger.get(this.turn)].add(Coordinate.directionToCoordinate.get(direction));
        this.turn = this.turn == Turn.PLAYER_1 ? Turn.PLAYER_2 : Turn.PLAYER_1;
        return true;
    }

    private Boolean isInWallMap(Coordinate position) {
        return 0 <= position.getX() && position.getX() < this.size - 1 &&
                0 <= position.getY() && position.getY() < this.size - 1;
    }

    private Boolean canWin() {
        for (int i = 0; i < 2; i++) {
            boolean canPlayerWin = false;

            Boolean[][] mark = new Boolean[this.size][this.size];

            for (int j = 0; j < this.size; j++) {
                for (int k = 0; k < this.size; k++) {
                    mark[j][k] = false;
                }
            }

            List<Coordinate> queue = new ArrayList<>();
            queue.add(this.positions[i]);
            mark[this.positions[i].getX()][this.positions[i].getY()] = true;

            while (!queue.isEmpty()) {
                Coordinate position = queue.removeFirst();
                if (position.getX() == i * (this.size - 1)) {
                    canPlayerWin = true;
                    break;
                }

                for (Direction direction: Direction.values()) {
                    if (canSimpleMove(position, direction)) {
                        Coordinate projectionPosition = new Coordinate(position);
                        projectionPosition.add(Coordinate.directionToCoordinate.get(direction));
                        if (!mark[projectionPosition.getX()][projectionPosition.getY()]) {
                            queue.add(projectionPosition);
                            mark[projectionPosition.getX()][projectionPosition.getY()] = true;
                        }
                    }
                }
            }

            if (!canPlayerWin) {
                return false;
            }
        }

        return true;
    }

    private Boolean canPlace(Coordinate position, Wall wall) {
        if (!isInWallMap(position)) {
            return false;
        }

        if (wall == Wall.NONE) {
            return false;
        }

        if (this.nbWalls[turnToInteger.get(this.turn)] <= 0) {
            return false;
        }

        if (this.walls[position.getX()][position.getY()] != Wall.NONE) {
            return false;
        }

        Board provisionalBoard = new Board(this);
        provisionalBoard.walls[position.getX()][position.getY()] = wall;
        if (!provisionalBoard.canWin()) {
            return false;
        }

        if (wall == Wall.HORIZONTAL) {
            Boolean isWallLeft = position.getY() != 0 &&
                    this.walls[position.getX()][position.getY() - 1] == Wall.HORIZONTAL;
            Boolean isWallRight = position.getY() != size - 1 - 1 &&
                    this.walls[position.getX()][position.getY() + 1] == Wall.HORIZONTAL;

            return !(isWallLeft || isWallRight);
        }
        else {
            Boolean isWallUp = position.getX() != 0 &&
                    this.walls[position.getX() - 1][position.getY()] == Wall.VERTICAL;
            Boolean isWallDown = position.getX() != size - 1 - 1 &&
                    this.walls[position.getX() + 1][position.getY()] == Wall.VERTICAL;

            return !(isWallUp || isWallDown);
        }
    }

    public Boolean place(Coordinate position, Wall wall) {
        if (!canPlace(position, wall)) {
            return false;
        }

        this.walls[position.getX()][position.getY()] = wall;
        this.nbWalls[turnToInteger.get(this.turn)] = this.nbWalls[turnToInteger.get(this.turn)] - 1;
        this.turn = this.turn == Turn.PLAYER_1 ? Turn.PLAYER_2 : Turn.PLAYER_1;
        return true;
    }
}
