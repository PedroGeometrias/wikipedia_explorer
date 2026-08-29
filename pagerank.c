#include "pagerank.h"
#include <stdlib.h>
#include <math.h>

// pagerank is an algorithm used by google to rank their pages, crazy stuff

// this fills out_degrees with outgoing edges from node i, and indegrees, with the incoming edges to node i
void compute_degrees(const Graph *g, uint32_t *out_degrees, uint32_t *in_degrees) {
    if(!g && !out_degrees && !in_degrees){
        return;
    }
    for (uint32_t i = 0; i < g->node_count; i++) {
        out_degrees[i] = g->out_offsets[i + 1] - g->out_offsets[i];
        in_degrees[i] = g->in_offsets[i + 1] - g->in_offsets[i];
    }
}



// actual pagerank algorithm
uint32_t pagerank(const Graph *g, double damping, double tolerance, uint32_t max_iteration, double *scores) {
    if(!g && !scores){
        return 0;
    }
    // initialization
    uint32_t n = g->node_count;
    if (n == 0) return 0;

    double *next_scores = (double*)malloc(n * sizeof(double));
    uint32_t *out_deg = (uint32_t*)malloc(n * sizeof(uint32_t));
    uint32_t *in_deg = (uint32_t*)malloc(n * sizeof(uint32_t));
    
    compute_degrees(g, out_deg, in_deg);
    
    // every node starts with the value of 1/n
    for (uint32_t i = 0; i < n; i++) {
        scores[i] = 1.0 / n;
    }
    
    uint32_t iteration = 0;
    double diff = tolerance + 1.0;
    
    // The loop runs until either the maximum number of iterations is reached or the scores have converged
     while (iteration < max_iteration && diff >= tolerance) {
        // the actual logic is quite simple
        double sink_sum = 0.0;
        for (uint32_t i = 0; i < n; i++) {
            if (out_deg[i] == 0) {
                sink_sum += scores[i];
            }
        }
        
        diff = 0.0;
        for (uint32_t i = 0; i < n; i++) {
            double sum = 0.0;
            uint32_t start_edge = g->in_offsets[i];
            uint32_t end_edge = g->in_offsets[i + 1];
            
            for (uint32_t j = start_edge; j < end_edge; j++) {
                uint32_t u = g->in_neighbors[j];
                sum += scores[u] / out_deg[u];
            }
            
            next_scores[i] = ((1.0 - damping) / n) + damping * (sum + sink_sum / n);
        }
        
        for (uint32_t i = 0; i < n; i++) {
            diff += fabs(next_scores[i] - scores[i]);
            scores[i] = next_scores[i];
        }
        
        iteration++;
    }
    
    free(next_scores);
    free(out_deg);
    free(in_deg);
    
    return iteration;
}
