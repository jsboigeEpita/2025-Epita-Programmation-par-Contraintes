#ifndef GAME_H
#define GAME_H

#include "definition.h"

char canSimpleMove(enum wall walls[BOARD_SIZE - 1][BOARD_SIZE - 1], unsigned char x, unsigned char y, enum direction direction);
char move(struct position *position, enum direction direction, char jump);
char backMove(struct position *position, enum direction direction, char jump);
char canSimplePlace(enum wall walls[BOARD_SIZE - 1][BOARD_SIZE - 1], unsigned char x, unsigned char y, enum wall wall);
char place(struct position *position, unsigned char x, unsigned char y, enum wall wall);

#endif // GAME_H