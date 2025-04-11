#include "layer.h"

#include <stdlib.h>
#include <stdio.h>

#include "code.h"
#include "game.h"
#include "memory.h"
#include "queue.h"
#include "utilities.h"

static char isSame(struct indices a, struct indices b) {
    return a.move == b.move && a.moveToWin == b.moveToWin;
}

static struct indices bestMove(struct indices a, struct indices b) {
    if ((a.moveToWin) % 2 == 0) {
        if (b.moveToWin % 2 == 0) {
            if (a.moveToWin <= b.moveToWin) {
                return a;
            }
            else {
                return b;
            }
        }
        else {
            return a;
        }
    }
    else {
        if (b.moveToWin % 2 == 0) {
            return b;
        }
        else {
            if (a.moveToWin < b.moveToWin) {
                return b;
            }
            else {
                return a;
            }
        }
    }
}

static unsigned int encodeMove(enum direction direction, char jump) {
    unsigned char code = direction * 2 + jump;

    return code * 4 + 1;
}

static unsigned int encodePlace(unsigned char x, unsigned char y, enum wall wall) {
    unsigned char code = x * (BOARD_SIZE - 1) + y;
    code = code * 2 + (wall == WALL_HORIZONTAL);

    return code * 4 + 3;
}

static void computeUpperLayer(struct position *position, size_t layer) {
    size_t code = encode(position, layer);

    struct indices current;
    current.next = 0;
    current.move = 0;
    current.moveToWin = 1;

    for (size_t i = 0; i < BOARD_SIZE - 1; i++) {
        for (size_t j = 0; j < BOARD_SIZE - 1; j++) {
            if (place(position, i, j, WALL_HORIZONTAL)) {
                size_t pCode = encode(position, layer + 1);
                struct indices previous = readMemory(pCode, 0);
                previous.move = encodePlace(i, j, WALL_HORIZONTAL);
                current = bestMove(current, previous);

                position->walls[i][j] = WALL_NONE;
                position->turn = (position->turn + 1) % 2;
                position->players[position->turn].w = position->players[position->turn].w + 1;
            }

            if (place(position, i, j, WALL_VERTICAL)) {
                size_t pCode = encode(position, layer + 1);
                struct indices previous = readMemory(pCode, 0);
                previous.move = encodePlace(i, j, WALL_VERTICAL);
                previous.next = pCode;
                current = bestMove(current, previous);

                position->walls[i][j] = WALL_NONE;
                position->turn = (position->turn + 1) % 2;
                position->players[position->turn].w = position->players[position->turn].w + 1;
            }
        }
    }

    current.moveToWin = current.moveToWin + 1;
    writeMemory(code, current);
}

static void defineTurn(struct queue *queue, unsigned long long code, size_t layer) {
    struct indices indices;
    indices.moveToWin = 2;
    indices.move = 0;

    if (((code / (1 + min(2 * NB_WALLS - layer, NB_WALLS) - max(0, NB_WALLS - layer))) / BOARD_SIZE) % BOARD_SIZE == BOARD_SIZE - 1) {
        writeMemory(code * 2, indices);
        enqueue(queue, (code - (1 + min(2 * NB_WALLS - layer, NB_WALLS) - max(0, NB_WALLS - layer)) * BOARD_SIZE) * 2 + 1);
    }
    else {
        writeMemory(code * 2 + 1, indices);
        enqueue(queue, (code + (1 + min(2 * NB_WALLS - layer, NB_WALLS) - max(0, NB_WALLS - layer)) * BOARD_SIZE * BOARD_SIZE * BOARD_SIZE) * 2);
    }
}

static void writeTurn(struct position *position, size_t layer) {
    for (size_t i = 0; i < 2; i++) {
        position->turn = i;
        computeUpperLayer(position, layer);
    }
}

static void defineNumberWalls(struct queue *queue, unsigned long long code, size_t layer) {
    for (size_t i = 0; i < (size_t) (1 + min(2 * NB_WALLS - layer, NB_WALLS) - max(0, NB_WALLS - layer)); i++) {
        defineTurn(queue, code * (1 + min(2 * NB_WALLS - layer, NB_WALLS) - max(0, NB_WALLS - layer)) + i, layer);
    }
}

static void writeNumberWalls(struct position *position, size_t layer) {
    for (size_t i = 0; i < (size_t) (1 + min(2 * NB_WALLS - layer, NB_WALLS) - max(0, NB_WALLS - layer)); i++) {
        position->players[0].w = i + max(0, NB_WALLS - layer);
        position->players[1].w = 2 * NB_WALLS - layer - position->players[0].w;
        writeTurn(position, layer);
    }
}

static void defineCoords(struct queue *queue, enum wall walls[BOARD_SIZE - 1][BOARD_SIZE - 1], size_t layer) {
    char playersCanBe[2][BOARD_SIZE][BOARD_SIZE];

    for (size_t i = 0; i < 2; i++) {
        for (size_t j = 0; j < BOARD_SIZE; j++) {
            for (size_t k = 0; k < BOARD_SIZE; k++) {
                playersCanBe[i][j][k] = 0;
            }
        }
    }

    for (size_t i = 0; i < 2; i++) {
        struct queue *branches = createQueue();
        for (size_t j = 0; j < BOARD_SIZE; j++) {
            playersCanBe[i][i * (BOARD_SIZE - 1)][j] = 1;
            enqueue(branches, i * (BOARD_SIZE - 1) * BOARD_SIZE + j);
        }

        for (; !isEmpty(branches); ) {
            unsigned long long data = dequeue(branches);
            unsigned char x = data / BOARD_SIZE;
            unsigned char y = data % BOARD_SIZE;

            for (size_t j = 0; j < 4; j++) {
                unsigned char px = x + directionToCoordinate[j][0];
                unsigned char py = y + directionToCoordinate[j][1];
                if (canSimpleMove(walls, x, y, j) && !playersCanBe[i][px][py]) {
                    playersCanBe[i][px][py] = 1;
                    enqueue(branches, px * BOARD_SIZE + py);
                }
            }
        }

        freeQueue(branches);
    }

    unsigned long long code = 0;

    // Get walls informations
    size_t indexes[layer];
    enum wall orientations[layer];
    size_t start = 0;

    for (size_t i = 0; i < BOARD_SIZE - 1; i++)
    {
        for (size_t j = 0; j < BOARD_SIZE - 1; j++) {
            if (walls[i][j] != WALL_NONE)
            {
                indexes[start] = i * (BOARD_SIZE - 1) + j;
                orientations[start] = walls[i][j];
                start = start + 1;
            }
        }
    }

    // Wall
    start = 0;
    for (size_t i = 0; i < layer; i++)
    {
        for (size_t j = start; j < indexes[i]; j++)
        {
            code += (*getPascal())[NB_INTER - (j + 1)][layer - (i + 1)];
        }

	    start = indexes[i] + 1;
    }

    // Wall orientation
    for (size_t i = 0; i < layer; i++)
    {
        code = code * 2 + (orientations[i] == WALL_HORIZONTAL ? 1 : 0);
    }

    for (size_t i = 0; i < BOARD_SIZE; i++) {
        for (size_t j = 0; j < BOARD_SIZE - 1; j++) {
            for (size_t k = 0; k < BOARD_SIZE; k++) {

                unsigned long long pCode;

                if (playersCanBe[0][j][k] && (j + 1 != (BOARD_SIZE - 1) || i != k)) {
                    pCode = code;
                    pCode = pCode * BOARD_SIZE + j + 1;
                    pCode = pCode * BOARD_SIZE + k;
                    pCode = pCode * BOARD_SIZE + (BOARD_SIZE - 1);
                    pCode = pCode * BOARD_SIZE + i;

                    defineNumberWalls(queue, pCode, layer);
                }

                if (playersCanBe[1][j][k] && (j != 0 || i != k)) {
                    pCode = code;
                    pCode = pCode * BOARD_SIZE;
                    pCode = pCode * BOARD_SIZE + i;
                    pCode = pCode * BOARD_SIZE + j;
                    pCode = pCode * BOARD_SIZE + k;

                    defineNumberWalls(queue, pCode, layer);
                }
            }
        }
    }

    if (layer != 2 * NB_WALLS) {
        struct position *position = malloc(sizeof(struct position));
        if (position == NULL) {
            printf("OUT OF MEMORY !\n");
            exit(1);
        }

        for (size_t i = 0; i < BOARD_SIZE - 1; i++) {
            for (size_t j = 0; j < BOARD_SIZE - 1; j++) {
                position->walls[i][j] = walls[i][j];
            }
        }

        for (size_t i = 0; i < BOARD_SIZE - 1; i++) {
            for (size_t j = 0; j < BOARD_SIZE; j++) {
                if (playersCanBe[0][i][j]) {
                    for (size_t k = 1; k < BOARD_SIZE; k++) {
                        for (size_t l = 0; l < BOARD_SIZE - 1; l++) {
                            if ((i != k || j != l) && playersCanBe[1][k][l]) {
                        
                                position->players[0].x = i;
                                position->players[0].y = j;
                                position->players[1].x = k;
                                position->players[1].y = l;

                                writeNumberWalls(position, layer);
                            }
                        }
                    }
                }
            }
        }

        free(position);
    }
}

static void placeWallsReq(struct queue *queue, enum wall walls[BOARD_SIZE - 1][BOARD_SIZE - 1], size_t layer, size_t offset, size_t nb_walls) {
    if (nb_walls == 0) {
        defineCoords(queue, walls, layer);
        return;
    }

    for (size_t i = offset; i < NB_INTER - nb_walls + 1; i++) {
        if (nb_walls == layer) {
            printf("%lu/%lu\n", i, NB_INTER - nb_walls + 1);
        }
        if (canSimplePlace(walls, i / (BOARD_SIZE - 1), i % (BOARD_SIZE - 1), WALL_HORIZONTAL)) {
            walls[i / (BOARD_SIZE - 1)][i % (BOARD_SIZE - 1)] = WALL_HORIZONTAL;
            placeWallsReq(queue, walls, layer, i + 1, nb_walls - 1);
            walls[i / (BOARD_SIZE - 1)][i % (BOARD_SIZE - 1)] = WALL_NONE;
        }
        if (canSimplePlace(walls, i / (BOARD_SIZE - 1), i % (BOARD_SIZE - 1), WALL_VERTICAL)) {
            walls[i / (BOARD_SIZE - 1)][i % (BOARD_SIZE - 1)] = WALL_VERTICAL;
            placeWallsReq(queue, walls, layer, i + 1, nb_walls - 1);
            walls[i / (BOARD_SIZE - 1)][i % (BOARD_SIZE - 1)] = WALL_NONE;
        }
    }
}

static void placeWalls(struct queue *queue, size_t layer) {
    enum wall walls[BOARD_SIZE - 1][BOARD_SIZE - 1];

    for (size_t i = 0; i < BOARD_SIZE - 1; i++) {
        for (size_t j = 0; j < BOARD_SIZE - 1; j++) {
            walls[i][j] = WALL_NONE;
        }
    }

    placeWallsReq(queue, walls, layer, 0, layer);
}

struct queue *initLayer(size_t layer) {
    printf("Initializing layer %lu.\n", layer);

    struct queue *queue = createQueue();
    placeWalls(queue, layer);

    return queue;
}

static char verifyChain(unsigned long long code, unsigned long long pCode) {
    if (pCode == code) {
        return 0;
    }

    struct indices indices = readMemory(pCode, 1);
    if (indices.moveToWin < 2) {
        return 0;
    }

    if (indices.move == 0 || indices.move / 2 % 2 == 1) {
        return 1;
    }

    return verifyChain(code, indices.next);
}

void computeLayer(struct queue *queue, size_t layer) {
    printf("Computing for layer %lu.\n", layer);
    for (size_t i = 0; !isEmpty(queue); i++) {

        if (i % 100000 == 0) {
            printf("%llu elements...\n", queue->nb);
        }

        unsigned long long code = dequeue(queue);

        struct position *position = decode(code, layer);

        unsigned char x = position->players[position->turn].x;
        unsigned char y = position->players[position->turn].y;

        struct indices current;
        current.next = 0;
        current.move = 0;
        current.moveToWin = 1;

        for (size_t i = 0; i < 4; i++) {
            for (size_t j = 0; j < 2; j++) {
                if (move(position, i, j)) {
                    unsigned long long pCode = encode(position, layer);
                    if (verifyChain(code, pCode)) {
                        struct indices projection = readMemory(pCode, 1);
                        projection.move = encodeMove(i, j);
                        projection.next = pCode;
                        current = bestMove(current, projection);
                    }

                    position->turn = (position->turn + 1) % 2;
                    position->players[position->turn].x = x;
                    position->players[position->turn].y = y;
                }
            }
        }

        current.moveToWin = current.moveToWin + 1;

        if (!isSame(current, readMemory(code, 1))) {
            writeMemory(code, current);

            x = position->players[(position->turn + 1) % 2].x;
            y = position->players[(position->turn + 1) % 2].y;

            for (size_t i = 0; i < 4; i++) {
                for (size_t j = 0; j < 2; j++) {
                    if (backMove(position, i, j)) {
                        unsigned long long pCode = encode(position, layer);
                        enqueue(queue, pCode);

                        position->turn = (position->turn + 1) % 2;
                        position->players[(position->turn + 1) % 2].x = x;
                        position->players[(position->turn + 1) % 2].y = y;
                    }
                }
            }
        }

        free(position);
    }

    freeQueue(queue);
}
