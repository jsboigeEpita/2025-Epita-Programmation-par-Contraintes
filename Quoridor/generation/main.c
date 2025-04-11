#include <stdio.h>
#include <stdlib.h>

#include "definition.h"
#include "code.h"
#include "layer.h"
#include "memory.h"
#include "utilities.h"

int main()
{
    /*
    initPascal();
	
    struct position *position = malloc(sizeof(struct position));
    position->players[0].x = 1;
    position->players[0].y = 2;
    position->players[1].x = 3;
    position->players[1].y = 4;
    position->players[0].w = 0;
    position->players[1].w = 2;
    position->turn = 1;

    for (size_t i = 0; i < BOARD_SIZE - 1; i++)
    {
        for (size_t j = 0; j < BOARD_SIZE - 1; j++)
        {
            position->walls[i][j] = 0;
        }
    }

    position->walls[0][0] = 1;
    position->walls[0][1] = 2;
    position->walls[1][0] = 1;
    position->walls[3][3] = 2;
    position->walls[2][1] = 1;
    position->walls[1][1] = 2;

    printf("player_1.x = %hhu\n", position->players[0].x);
    printf("player_1.y = %hhu\n", position->players[0].y);
    printf("player_2.x = %hhu\n", position->players[1].x);
    printf("player_2.y = %hhu\n", position->players[1].y);
    printf("player_1.w = %hhu\n", position->players[0].w);
    printf("player_2.w = %hhu\n", position->players[1].w);

    for (size_t i = 0; i < BOARD_SIZE - 1; i++)
    {
        for (size_t j = 0; j < BOARD_SIZE - 1; j++)
        {
            printf("%hhu ", position->walls[i][j]);
        }
        printf("\n");
    }

    unsigned long long a = encode(position, 6);
    free(position);

    position = decode(a, 6);

    printf("player_1.x = %hhu\n", position->players[0].x);
    printf("player_1.y = %hhu\n", position->players[0].y);
    printf("player_2.x = %hhu\n", position->players[1].x);
    printf("player_2.y = %hhu\n", position->players[1].y);
    printf("player_1.w = %hhu\n", position->players[0].w);
    printf("player_2.w = %hhu\n", position->players[1].w);

    for (size_t i = 0; i < BOARD_SIZE - 1; i++)
    {
        for (size_t j = 0; j < BOARD_SIZE - 1; j++)
        {
            printf("%hhu ", position->walls[i][j]);
        }
        printf("\n");
    }

    free(position);
    */

    printf("BOARD_SIZE: %d\n", BOARD_SIZE);
    printf("NB_WALLS: %d\n", NB_WALLS);

    initPascal();
    initMemory();

    size_t layer = NB_WALLS * 2;
    printf("Number of posible position: %llu.\n", dimension(layer));

    for (long i = NB_WALLS * 2; i >= 0; i--) {
        initMemoryLayer(i, dimension(i));
        struct queue *queue = initLayer(i);
        computeLayer(queue, i);
        compressMemory(i, dimension(i));
    }

    freeMemory();
}
