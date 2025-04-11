package fr.matthieufouliard.service;

import fr.matthieufouliard.model.*;
import jakarta.enterprise.context.ApplicationScoped;

import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

@ApplicationScoped
public class AIService {
    private static final long[][] pascal = initPascal();

    private static long[][] initPascal() {
        long[][] pascal = new long[17][17];

        for (int i = 0; i < 17; i++) {
            pascal[i][0] = 1;
            pascal[0][i] = 1;
            pascal[i][i] = 1;
        }

        for (int i = 2; i < 17; i++) {
            for (int j = 1; j < i; j++) {
                pascal[i][j] = pascal[i - 1][j] + pascal[i - 1][j - 1];
                pascal[j][i] = pascal[j][i - 1] + pascal[j - 1][i - 1];
            }
        }

        return pascal;
    }

    AIPlay play(Board board) {
        long code = 0L;
        int nb_inter = (board.getSize() - 1) * (board.getSize() - 1);

        List<Integer> indexes = new ArrayList<>();
        List<Wall> orientations = new ArrayList<>();
        int layer = 0;

        for (int i = 0; i < nb_inter; i++) {
            int x = i / (board.getSize() - 1);
            int y = i % (board.getSize() - 1);

            if (board.getWalls()[x][y] != Wall.NONE) {
                indexes.add(i);
                orientations.add(board.getWalls()[x][y]);
                layer = layer + 1;
            }
        }

        int nb_walls = (layer + board.getNbWalls()[0] + board.getNbWalls()[1]) / 2;

        int start = 0;

        for (int i = 0; i < layer; i++) {
            for (int j = start; j < indexes.get(i); j++) {
                code = code + pascal[nb_inter - (j + 1)][layer - (i + 1)];
            }

            start = indexes.get(i) + 1;
        }

        for (int i = 0; i < layer; i++) {
            code = code * 2 + (orientations.get(i) == Wall.HORIZONTAL ? 1 : 0);
        }

        code = code * board.getSize() + board.getPositions()[0].getX();
        code = code * board.getSize() + board.getPositions()[0].getY();
        code = code * board.getSize() + board.getPositions()[1].getX();
        code = code * board.getSize() + board.getPositions()[1].getY();

        code = code * (1 + Math.min(2 * nb_walls - layer, nb_walls) - Math.max(0, nb_walls - layer)) + board.getNbWalls()[0] - Math.max(0, nb_walls - layer);

        code = code * 2 + (board.getTurn() == Turn.PLAYER_1 ? 0 : 1);

        return readSolution(board.getSize(), nb_walls, layer, code);
    }

    static final Direction intToDirection[] = { Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT };

    private AIPlay readSolution(int boardSize, int nbWalls, int layer, long code) {
        int result = 0;
        try {
            InputStream is = AIService.class.getResourceAsStream("/boardSize_" + boardSize + "/nbWalls_" + nbWalls + "/layer_" + layer + ".quoridor");
            assert is != null;

            if (is.skip(code * 2) < code * 2) {
                throw new RuntimeException();
            }
            result = is.read();
            result = (is.read() << 8) | result;
            is.close();

        } catch (Exception e) {
            return new AIPlay();
        }

        if (result % 2 == 0) {
            return new AIPlay();
        }

        result = result / 2;
        if (result % 2 == 0) {
            result = result / 2;

            Boolean jump = result % 2 != 0;
            result = result / 2;

            Direction direction = intToDirection[result];

            return new AIPlay(direction, jump);
        }
        else {
            result = result / 2;

            Wall wall = result % 2 != 0 ? Wall.HORIZONTAL : Wall.VERTICAL;
            result = result / 2;

            Integer y = result % boardSize;
            result = result / boardSize;

            Integer x = result;

            return new AIPlay(x, y, wall);
        }
    }
}
