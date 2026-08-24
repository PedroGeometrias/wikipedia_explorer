#ifndef GRAPH_H
#define GRAPH_H

#include <stddef.h>
#include <stdint.h>

// this is the data struct used by the graph algorithms
typedef struct {
    uint32_t node_count;
    uint32_t edge_count;
    uint32_t *out_offsets;
    uint32_t *out_neighbors;
    uint32_t *in_offsets;
    uint32_t *in_neighbors;
} Graph;

// some control over the graph
Graph* graph_create(uint32_t node_count, uint32_t edge_count);
void graph_set_edges(Graph *g, const uint32_t *src, const uint32_t *dst);
void graph_free(Graph *g);

#endif
