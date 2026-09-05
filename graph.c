#include "graph.h"
#include <stdlib.h>

// allocating memory for te graph
Graph* graph_create(uint32_t node_count, uint32_t edge_count) {
    Graph *g = (Graph*)malloc(sizeof(Graph));
    g->node_count = node_count;
    g->edge_count = edge_count;
    g->out_offsets = (uint32_t*)calloc(node_count + 1, sizeof(uint32_t));
    g->out_neighbors = (uint32_t*)malloc(edge_count * sizeof(uint32_t));
    g->in_offsets = (uint32_t*)calloc(node_count + 1, sizeof(uint32_t));
    g->in_neighbors = (uint32_t*)malloc(edge_count * sizeof(uint32_t));
    return g;
}

void graph_set_edges(Graph *g, const uint32_t *src, const uint32_t *dst) {
    if(!g || !src || !dst){
        return;
    }
    uint32_t *out_deg = (uint32_t*)calloc(g->node_count, sizeof(uint32_t));
    uint32_t *in_deg = (uint32_t*)calloc(g->node_count, sizeof(uint32_t));
    
    for (uint32_t i = 0; i < g->edge_count; i++) {
        out_deg[src[i]]++;
        in_deg[dst[i]]++;
    }
    
    g->out_offsets[0] = 0;
    g->in_offsets[0] = 0;
    for (uint32_t i = 0; i < g->node_count; i++) {
        g->out_offsets[i + 1] = g->out_offsets[i] + out_deg[i];
        g->in_offsets[i + 1] = g->in_offsets[i] + in_deg[i];
    }
    
    uint32_t *out_cur = (uint32_t*)malloc(g->node_count * sizeof(uint32_t));
    uint32_t *in_cur = (uint32_t*)malloc(g->node_count * sizeof(uint32_t));
    for (uint32_t i = 0; i < g->node_count; i++) {
        out_cur[i] = g->out_offsets[i];
        in_cur[i] = g->in_offsets[i];
    }
    
    for (uint32_t i = 0; i < g->edge_count; i++) {
        uint32_t u = src[i];
        uint32_t v = dst[i];
        g->out_neighbors[out_cur[u]++] = v;
        g->in_neighbors[in_cur[v]++] = u;
    }
    
    free(out_deg);
    free(in_deg);
    free(out_cur);
    free(in_cur);
}

void graph_free(Graph *g) {
    if (g) {
        free(g->out_offsets);
        free(g->out_neighbors);
        free(g->in_offsets);
        free(g->in_neighbors);
        free(g);
    }
}
