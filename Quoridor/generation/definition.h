#ifndef DEFINITION_H
#define DEFINITION_H

// Basic parametters
#define BOARD_SIZE 4
#define NB_WALLS 0

#define NB_INTER ((BOARD_SIZE - 1) * (BOARD_SIZE - 1))

enum wall {
    WALL_NONE,
    WALL_HORIZONTAL,
    WALL_VERTICAL,
};

enum turn {
    TURN_PLAYER_1,
    TURN_PLAYER_2,
};

struct player {
    unsigned char w;
    unsigned char x;
    unsigned char y;
};

struct position {
    struct player players[2];
    enum turn turn;
    enum wall walls[BOARD_SIZE - 1][BOARD_SIZE - 1];
};

enum winner {
  WINNER_NONE,
  WINNER_PLAYER_1,
  WINNER_PLAYER_2,
};

enum direction {
    UP,
    RIGHT,
    LEFT,
    DOWN,
};

// Static variable
static const char directionToCoordinate[4][2] = { { -1, 0 }, { 0, 1 }, { 1, 0 }, { 0, -1 } };

#endif // DEFINITION_H