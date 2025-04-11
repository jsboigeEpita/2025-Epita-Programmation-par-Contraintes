#include "game.h"

#include <stddef.h>

#include "definition.h"
#include "queue.h"

static char isInBoard(unsigned char x, unsigned char y) {
    return x < BOARD_SIZE && y < BOARD_SIZE;
}

static char isInWallBoard(unsigned char x, unsigned char y) {
    return x < BOARD_SIZE - 1 && y < BOARD_SIZE - 1;
}

static char isWall(enum wall walls[BOARD_SIZE - 1][BOARD_SIZE - 1], unsigned char x, unsigned char y, enum direction direction) {
    static const char dx[4][2] = { { -1, -1 } , { -1, 0 } , { 0, 0 } , { 0, -1 } };
    static const char dy[4][2] = { { -1, 0 } , { 0, 0 } , { 0, -1 } , { -1, -1 } };

    static const unsigned char lx[4][2] = { { 0, 0 } , { 0, BOARD_SIZE - 1 } , { BOARD_SIZE - 1, BOARD_SIZE - 1 } , { BOARD_SIZE - 1, 0 } };
    static const unsigned char ly[4][2] = { { 0, BOARD_SIZE - 1 } , { BOARD_SIZE - 1, BOARD_SIZE - 1 } , { BOARD_SIZE - 1, 0 } , { 0, 0 } };

    for (size_t i = 0; i < 2; i++) {
        if (x != lx[direction][i] && y != ly[direction][i] && walls[x + dx[direction][i]][y + dy[direction][i]] == direction % 2 + 1) {
            return 1;
        }
    }

    return 0;
}

char canSimpleMove(enum wall walls[BOARD_SIZE - 1][BOARD_SIZE - 1], unsigned char x, unsigned char y, enum direction direction) {
    if (isWall(walls, x, y, direction)) {
        return 0;
    }

    return isInBoard(x + directionToCoordinate[direction][0], y + directionToCoordinate[direction][1]);
}

static char canMove(struct position *position, enum direction direction, char jump) {
    unsigned char x = position->players[position->turn].x;
    unsigned char y = position->players[position->turn].y;

    if (jump) {
        char dx = position->players[(position->turn + 1) % 2].x - x;
        char dy = position->players[(position->turn + 1) % 2].y - y;

        if (dx * dx + dy * dy != 1) {
            return 0;
        }

        enum direction d;

        for (size_t i = 0; i < 4; i++) {
            if (directionToCoordinate[i][0] == dx && directionToCoordinate[i][1] == dy) {
                d = i;
            }
        }

        if (d == (direction + 2) % 4) {
            return 0;
        }

        if (isWall(position->walls, x, y, d)) {
            return 0;
        }

        x = x + dx;
        y = y + dy;

        if (canSimpleMove(position->walls, x, y, d)) {
            return d == direction;
        }
    }

    if (!canSimpleMove(position->walls, x, y, direction)) {
        return 0;
    }

    x = x + directionToCoordinate[direction][0];
    y = y + directionToCoordinate[direction][1];
    return x != position->players[(position->turn + 1) % 2].x || y != position->players[(position->turn + 1) % 2].y;
}

char move(struct position *position, enum direction direction, char jump) {
    if (!canMove(position, direction, jump)) {
        return 0;
    }

    if (jump) {
        position->players[position->turn].x = position->players[(position->turn + 1) % 2].x;
        position->players[position->turn].y = position->players[(position->turn + 1) % 2].y;
    }

    position->players[position->turn].x = position->players[position->turn].x + directionToCoordinate[direction][0];
    position->players[position->turn].y = position->players[position->turn].y + directionToCoordinate[direction][1];

    position->turn = (position->turn + 1) % 2;

    return 1;
}

static char canBackMove(struct position *position, enum direction direction, char jump) {
    unsigned char x = position->players[(position->turn + 1) % 2].x;
    unsigned char y = position->players[(position->turn + 1) % 2].y;

    if (jump) {
        char dx = position->players[position->turn].x - x;
        char dy = position->players[position->turn].y - y;

        if (dx * dx + dy * dy != 1) {
            return 0;
        }

        enum direction d;

        for (size_t i = 0; i < 4; i++) {
            if (directionToCoordinate[i][0] == dx && directionToCoordinate[i][1] == dy) {
                d = i;
            }
        }

        if (d == (direction + 2) % 4) {
            return 0;
        }

        if (isWall(position->walls, x, y, d)) {
            return 0;
        }

        x = x + dx;
        y = y + dy;

        if (d != direction) {
            return canSimpleMove(position->walls, x, y, direction) && !canSimpleMove(position->walls, x, y, (direction + 2) % 4);
        }
    }

    if (!canSimpleMove(position->walls, x, y, direction)) {
        return 0;
    }

    x = x + directionToCoordinate[direction][0];
    y = y + directionToCoordinate[direction][1];
    return x != position->players[position->turn].x || y != position->players[position->turn].y;
}

char backMove(struct position *position, enum direction direction, char jump) {
    if (!canBackMove(position, direction,jump)) {
        return 0;
    }

    if (jump) {
        position->players[(position->turn + 1) % 2].x = position->players[position->turn].x;
        position->players[(position->turn + 1) % 2].y = position->players[position->turn].y;
    }

    position->players[(position->turn + 1) % 2].x = position->players[(position->turn + 1) % 2].x + directionToCoordinate[direction][0];
    position->players[(position->turn + 1) % 2].y = position->players[(position->turn + 1) % 2].y + directionToCoordinate[direction][1];

    position->turn = (position->turn + 1) % 2;

    return 1;
}

static char canWin(struct position *position) {
    for (size_t i = 0; i < 2; i++) {
        char canPlayerWin = 0;

        char mark[BOARD_SIZE][BOARD_SIZE];
        
        for (size_t j = 0; j < BOARD_SIZE; j++) {
            for (size_t k = 0; k < BOARD_SIZE; k++) {
                mark[j][k] = 0;
            }
        }

        struct queue *queue = createQueue();
        enqueue(queue, position->players[i].x * BOARD_SIZE + position->players[i].y);
        mark[position->players[i].x][position->players[i].y] = 1;

        for (; !isEmpty(queue); ) {
            unsigned long long data = dequeue(queue);
            unsigned char x = data / BOARD_SIZE;
            unsigned char y = data % BOARD_SIZE;

            if (x == i * (BOARD_SIZE - 1)) {
                canPlayerWin = 1;
                break;
            }

            for (size_t j = 0; j < 4; j++) {
                unsigned char px = x + directionToCoordinate[j][0];
                unsigned char py = y + directionToCoordinate[j][1];
                if (canSimpleMove(position->walls, x, y, j) && !mark[px][py]) {
                    enqueue(queue, px * BOARD_SIZE + py);
                    mark[px][py] = 1;
                }
            }
        }

        freeQueue(queue);

        if (!canPlayerWin) {
            return 0;
        }
    }

    return 1;
}

char canSimplePlace(enum wall walls[BOARD_SIZE - 1][BOARD_SIZE - 1], unsigned char x, unsigned char y, enum wall wall) {
    char dx = wall == WALL_VERTICAL;
    char dy = wall == WALL_HORIZONTAL;

    return !((isInWallBoard(x - dx, y - dy) && walls[x - dx][y - dy] == wall) || (isInWallBoard(x + dx, y + dy) && walls[x + dx][y + dy] == wall));
}

static char canPlace(struct position *position, unsigned char x, unsigned char y, enum wall wall) {
    if(!isInWallBoard(x, y)) {
        return 0;
    }

    if (wall == WALL_NONE) {
        return 0;
    }

    if (position->players[position->turn].w == 0) {
        return 0;
    }

    if (position->walls[x][y] != WALL_NONE) {
        return 0;
    }

    position->walls[x][y] = wall;
    if (!canWin(position)) {
        position->walls[x][y] = WALL_NONE;
        return 0;
    }

    position->walls[x][y] = WALL_NONE;

    return canSimplePlace(position->walls, x, y, wall);
}

char place(struct position *position, unsigned char x, unsigned char y, enum wall wall) {
    if (!canPlace(position, x, y, wall)) {
        return 0;
    }

    position->walls[x][y] = wall;
    position->players[position->turn].w = position->players[position->turn].w - 1;
    position->turn = (position->turn + 1) % 2;

    return 1;
}