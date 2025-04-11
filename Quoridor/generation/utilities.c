#include "utilities.h"

#include <stddef.h>
#include <stdio.h>

// Pascal triangle
static unsigned long long pascal[NB_INTER + 1][NB_INTER + 1];

// Fill Pascal triangle
void initPascal()
{
    printf("Initializing pascal triangle.\n");
    for (size_t i = 0; i < NB_INTER + 1; i++) {
        pascal[i][0] = 1;
        pascal[0][i] = 1;
        pascal[i][i] = 1;
    }
  
    for (size_t i = 2; i < NB_INTER + 1; i++)
    {
        for (size_t j = 1; j < i; j++)
        {
            pascal[i][j] = pascal[i - 1][j] + pascal[i - 1][j - 1];
            pascal[j][i] = pascal[j][i - 1] + pascal[j - 1][i - 1];
        }
    }
}

unsigned long long (*getPascal())[NB_INTER + 1][NB_INTER + 1] {
    return &pascal;
}

double power(double a, size_t b)
{
    double result = 1;

    for (; b > 0;)
    {
        result = b % 2 == 0 ? result : result * a;;
        a = a * a;
        b = b / 2;
    }

    return result;
}

size_t log_ceil(double a, size_t b)
{
    size_t result = 0;

    for (; a > 1; )
    {
        a = a / b;
        result = result + 1;
    }

    return result;
}

int min(int a, int b) {
    return a < b ? a : b;
}

int max(int a, int b) {
    return a < b ? b : a;
}