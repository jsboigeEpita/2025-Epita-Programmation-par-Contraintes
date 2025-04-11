#ifndef LAYER_H
#define LAYER_H

#include <stddef.h>

struct queue *initLayer(size_t layer);
void computeLayer(struct queue *queue, size_t layer);
void writeLayer(size_t layer);

#endif // LAYER_H