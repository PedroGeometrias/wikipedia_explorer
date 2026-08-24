#ifndef BFS_H
#define BFS_H

#include "graph.h"

void bfs(const Graph *g, uint32_t start_node, uint32_t *distances);
void bfs_paths(const Graph *g, uint32_t start_node, uint32_t *distances, uint32_t *predecessors);

#endif
