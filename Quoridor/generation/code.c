#include "code.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "definition.h"
#include "utilities.h"

unsigned long long dimension(unsigned char layer) {
    unsigned long long result = 1;

    // Maximum number of walls combinaisons.
    result = result * (*getPascal())[NB_INTER][layer];

    // Walls' orientation
    result = result * (1 << layer);

    // Players coordonates
    result = result * (BOARD_SIZE * BOARD_SIZE * BOARD_SIZE * BOARD_SIZE);

    // Walls differences
    result = result * (1 + min(2 * NB_WALLS - layer, NB_WALLS) - max(0, NB_WALLS - layer));

    // Turn
    result = result * 2;

    return result;
}

// Order of data (Strong bit to weak bit)
//
// - Combinaison              Modulo pascal[NB_INTER][layer]
// - Wall orientation         Modulo 2 ** layer
// - Player 1 x coordinate    Modulo BOARD_SIZE
// - Player 1 y coordinate    Modulo BOARD_SIZE
// - Player 2 x coordinate    Modulo BOARD_SIZE
// - Player 2 y coordinate    Modulo BOARD_SIZE
// - Player 1 w number        Modulo 1 + min(2 * NB_WALLS - layer, NB_WALLS) - max(0, NB_WALLS - layer)
// - Turn                     Modulo 2

// Encode a position to an index
unsigned long long encode(struct position *position, size_t layer)
{
    unsigned long long result = 0;

    // Get walls informations
    size_t indexes[layer];
    enum wall orientations[layer];
    size_t start = 0;

    for (size_t i = 0; i < NB_INTER; i++)
    {
        size_t x = i / (BOARD_SIZE - 1);
        size_t y = i % (BOARD_SIZE - 1);
        if (position->walls[x][y] != WALL_NONE)
        {
            indexes[start] = i;
            orientations[start] = position->walls[x][y];
            start = start + 1;
        }
    }

    // Wall
    start = 0;
    for (size_t i = 0; i < layer; i++)
    {
        for (size_t j = start; j < indexes[i]; j++)
        {
            result += (*getPascal())[NB_INTER - (j + 1)][layer - (i + 1)];
        }

	    start = indexes[i] + 1;
    }

    // Wall orientation
    for (size_t i = 0; i < layer; i++)
    {
        result = result * 2 + (orientations[i] == WALL_HORIZONTAL ? 1 : 0);
    }

    // Player 1 x
    result = result * BOARD_SIZE + position->players[0].x;

    // Player 1 y
    result = result * BOARD_SIZE + position->players[0].y;
    
    // Player 2 x
    result = result * BOARD_SIZE + position->players[1].x;
    
    // Player 2 y
    result = result * BOARD_SIZE + position->players[1].y;

    // Player w
    result = result * (1 + min(2 * NB_WALLS - layer, NB_WALLS) - max(0, NB_WALLS - layer)) + position->players[0].w - max(0, NB_WALLS - layer);

    // Turn
    result = result * 2 + position->turn;

    return result;
}

// Decode an index to a position
struct position *decode(unsigned long long code, size_t layer)
{
    struct position *result = malloc(sizeof(struct position));
    if (result == NULL) {
        printf("OUT OF MEMORY !\n");
        exit(1);
    }
    memset(result, 0, sizeof(struct position));

    // Turn
    result->turn = code % 2;
    code = code / 2;

    // Player w
    result->players[0].w = code % (1 + min(2 * NB_WALLS - layer, NB_WALLS) - max(0, NB_WALLS - layer)) + max(0, NB_WALLS - layer);
    result->players[1].w = 2 * NB_WALLS - layer - result->players[0].w;
    code = code / (1 + min(2 * NB_WALLS - layer, NB_WALLS) - max(0, NB_WALLS - layer));

    // Player 2 y
    result->players[1].y = code % BOARD_SIZE;
    code = code / BOARD_SIZE;

    // Player 2 x
    result->players[1].x = code % BOARD_SIZE;
    code = code / BOARD_SIZE;

    // Player 1 y
    result->players[0].y = code % BOARD_SIZE;
    code = code / BOARD_SIZE;

    // Player 1 x
    result->players[0].x = code % BOARD_SIZE;
    code = code / BOARD_SIZE;

    // Wall orientation
    enum wall orientations[layer];
    for (size_t i = layer; i > 0; i--)
    {
        orientations[i - 1] = (code % 2) ? WALL_HORIZONTAL : WALL_VERTICAL;
        code = code / 2;
    }

    // Wall
    size_t start = 0;
    for (size_t i = 0; i < layer; i++)
    {
      for (size_t j = start; j < NB_INTER; j++)
        {
            unsigned long long c = (*getPascal())[NB_INTER - (j + 1)][layer - (i + 1)];
            if (code < c)
            {
                size_t x = j / (BOARD_SIZE - 1);
                size_t y = j % (BOARD_SIZE - 1);
                result->walls[x][y] = orientations[i];
                start = j + 1;
                break;
            }

            code = code - c;
        }
    }

    return result;
}
