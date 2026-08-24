#include "bfs.h"
#include <stdlib.h>

// computes the shortest distance from start_node to every other node in an unweighted directed graph (digraph), basic computer science
void bfs(const Graph *g, uint32_t start_node, uint32_t *distances) {
    // alocating queue
    uint32_t *queue = (uint32_t*)malloc(g->node_count * sizeof(uint32_t));
    uint32_t head = 0, tail = 0;

    // initializing distance to a huge value, which basicallt means infinite distance, just like we are zero allocating this
    for (uint32_t i = 0; i < g->node_count; i++) {
        distances[i] = UINT32_MAX;
    }
    

    // start node starts with 0, and we unqueue it
    distances[start_node] = 0;
    queue[tail++] = start_node;

    // doing the good stuff(processing untile the queue is empty)
    while (head < tail) {
        uint32_t u = queue[head++];
        // for the current node u, we find its outgoing neighbors
        uint32_t start_edge = g->out_offsets[u];
        uint32_t end_edge = g->out_offsets[u + 1];

        for (uint32_t i = start_edge; i < end_edge; i++) {
            uint32_t v = g->out_neighbors[i];
            // if it hasn't been visited yer
            if (distances[v] == UINT32_MAX) {
                // we set the correct distance
                distances[v] = distances[u] + 1;
                queue[tail++] = v;
            }
        }
    }
    free(queue);
}

// same stuff as the normal bfs, but it records the predecessor of each visited node too
void bfs_paths(const Graph *g, uint32_t start_node, uint32_t *distances, uint32_t *predecessors) {
    uint32_t *queue = (uint32_t*)malloc(g->node_count * sizeof(uint32_t));
    uint32_t head = 0, tail = 0;

    for (uint32_t i = 0; i < g->node_count; i++) {
        distances[i] = UINT32_MAX;
        predecessors[i] = UINT32_MAX;
    }
    
    distances[start_node] = 0;
    queue[tail++] = start_node;

    while (head < tail) {
        uint32_t u = queue[head++];
        uint32_t start_edge = g->out_offsets[u];
        uint32_t end_edge = g->out_offsets[u + 1];

        for (uint32_t i = start_edge; i < end_edge; i++) {
            uint32_t v = g->out_neighbors[i];
            if (distances[v] == UINT32_MAX) {
                distances[v] = distances[u] + 1;
                predecessors[v] = u;
                queue[tail++] = v;
            }
        }
    }
    free(queue);
}
