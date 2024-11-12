#ifndef NTT_H
#define NTT_H

#include <stdint.h>

extern int16_t zetas[128];

void ntt(int16_t *poly);

#endif
