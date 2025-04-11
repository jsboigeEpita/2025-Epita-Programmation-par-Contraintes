#ifndef CODE_H
#define CODE_H

#include <stddef.h>

#include "definition.h"

unsigned long long dimension(unsigned char layer);
unsigned long long encode(struct position *position, size_t layer);
struct position *decode(unsigned long long code, size_t layer);

#endif // CODE_H
