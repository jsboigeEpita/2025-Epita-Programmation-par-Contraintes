#ifndef UTILITIES_H
#define UTILITIES_H

#include <stddef.h>

#include "definition.h"

void initPascal();
unsigned long long (*getPascal())[NB_INTER + 1][NB_INTER + 1];
double power(double a, size_t b);
size_t log_ceil(double a, size_t b);
int min(int a, int b);
int max(int a, int b);

#endif // UTILITIES_H
