#ifndef HISTORY_H
#define HISTORY_H

#include <stdbool.h>
#include <stdint.h>

#include "stack.h"

typedef struct History {
    Stack back;
    Stack forward;

    uint32_t current;
    bool has_current;
} History;

History *history_create(void);
void history_destroy(History *history);

bool history_visit(History *history, uint32_t node_id);

uint32_t history_back(History *history);
uint32_t history_forward(History *history);

bool history_can_back(const History *history);
bool history_can_forward(const History *history);

void history_clear(History *history);

#endif
