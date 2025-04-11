#ifndef MEMORY_H
#define MEMORY_H

#include <stddef.h>

struct indices {
    unsigned long long next;
    unsigned short moveToWin;
    unsigned short move;
};

void initMemory();
void initMemoryLayer(size_t layer, unsigned long long size);
struct indices readMemory(unsigned long long index, char current);
void writeMemory(unsigned long long index, struct indices indices);
void compressMemory(size_t layer, unsigned long long size);
void freeMemory();

#endif // MEMORY_H