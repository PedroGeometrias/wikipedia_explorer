#ifndef PAGERANK_H
#define PAGERANK_H

#include "graph.h"

void compute_degrees(const Graph *g, uint32_t *out_degrees, uint32_t *in_degrees);
uint32_t pagerank(const Graph *g, double damping, double tolerance, uint32_t max_iter, double *scores);

#endif
