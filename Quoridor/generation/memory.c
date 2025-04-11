#include "memory.h"

#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <unistd.h>

#include "definition.h"

static char buffer[64];
static FILE *previousLayer = NULL;
static FILE *currentLayer = NULL;

void initMemory() {
    sprintf(buffer, "data");
    if (access(buffer, F_OK) != 0) {
        mkdir(buffer, 0755);
    }
    if (chdir(buffer)) {
        printf("Could not change directory.\n");
        exit(1);
    };

    sprintf(buffer, "boardSize_%d", BOARD_SIZE);
    if (access(buffer, F_OK) != 0) {
        mkdir(buffer, 0755);
    }
    if (chdir(buffer)) {
        printf("Could not change directory.\n");
        exit(1);
    };

    sprintf(buffer, "nbWalls_%d", NB_WALLS);
    if (access(buffer, F_OK) != 0) {
        mkdir(buffer, 0755);
    }
    if (chdir(buffer)) {
        printf("Could not change directory.\n");
        exit(1);
    };
}

void initMemoryLayer(size_t layer, unsigned long long size) {
    printf("Initializing memory for layer %lu.\n", layer);
    if (previousLayer != NULL) {
        fclose(previousLayer);
    }

    previousLayer = currentLayer;

    sprintf(buffer, "layer_%lu_memory.temp", layer);
    currentLayer = fopen(buffer, "w+");

    struct indices indices;

    indices.next = 0;
    indices.moveToWin = 1;
    indices.move = 0;

    for (unsigned long long i = 0; i < size; i++) {
        if (i % (size / 10) == 0) {
            printf("%llu%%\n", i / (size / 10) * 10);
        }
        fwrite(&indices, sizeof(struct indices), 1, currentLayer);
    }
}

struct indices readMemory(unsigned long long index, char current) {
    struct indices indices;
    FILE *memory = previousLayer;

    if (current) {
        memory = currentLayer;
    }

    fseek(memory, index * sizeof(struct indices), SEEK_SET);
    if (fread(&indices, sizeof(struct indices), 1, memory) != 1) {
        printf("Could not read memory.\n");
        exit(1);
    }

    return indices;
}

void writeMemory(unsigned long long index, struct indices indices) {
    fseek(currentLayer, index * sizeof(struct indices), SEEK_SET);
    fwrite(&indices, sizeof(struct indices), 1, currentLayer);
}

void compressMemory(size_t layer, unsigned long long size) {
    printf("Compressing memory for layer %lu.\n", layer);

    sprintf(buffer, "layer_%lu.quoridor", layer);
    FILE *f = fopen(buffer, "w+");

    fseek(currentLayer, 0, SEEK_SET);

    for (unsigned long long i = 0; i < size; i++) {
        if (i % (size / 10) == 0) {
            printf("%llu%%\n", i / (size / 10) * 10);
        }
        struct indices indices;
        if (fread(&indices, sizeof(struct indices), 1, currentLayer) != 1) {
            printf("Could not read memory.\n");
            exit(1);
        }
        fwrite(&indices.move, sizeof(indices.move), 1, f);
    }

    fclose(f);
}

void freeMemory() {
    if (previousLayer != NULL) {
        fclose(previousLayer);
    }

    fclose(currentLayer);
}