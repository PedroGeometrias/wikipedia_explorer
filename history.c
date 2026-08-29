#include "history.h"

#include <stdint.h>
#include <stdlib.h>

History *history_create(void) {
    History *history = malloc(sizeof(History));

    if (!history) {
        return NULL;
    }

    if (!stack_init(&history->back, sizeof(uint32_t), 8)) {
        free(history);
        return NULL;
    }

    if (!stack_init(&history->forward, sizeof(uint32_t), 8)) {
        stack_destroy(&history->back);
        free(history);
        return NULL;
    }

    history->current = UINT32_MAX;
    history->has_current = false;

    return history;
}

void history_destroy(History *history) {
    if (!history) {
        return;
    }

    stack_destroy(&history->back);
    stack_destroy(&history->forward);

    free(history);
}

bool history_visit(History *history, uint32_t node_id) {
    if (!history) {
        return false;
    }

    // Clicking the node we're already on shouldn't create
    // another history entry.
    if (history->has_current && history->current == node_id) {
        return true;
    }

    // The old current node becomes something we can go back to.
    if (history->has_current) {
        if (!stack_push(&history->back, &history->current)) {
            return false;
        }
    }

    // A new navigation invalidates Forward history.
    stack_clear(&history->forward);

    history->current = node_id;
    history->has_current = true;

    return true;
}

uint32_t history_back(History *history) {
    if (
        !history ||
        !history->has_current ||
        stack_empty(&history->back)
    ) {
        return UINT32_MAX;
    }

    // Current node becomes available through Forward.
    if (!stack_push(&history->forward, &history->current)) {
        return UINT32_MAX;
    }

    uint32_t previous;

    if (!stack_pop(&history->back, &previous)) {
        return UINT32_MAX;
    }

    history->current = previous;

    return previous;
}

uint32_t history_forward(History *history) {
    if (
        !history ||
        !history->has_current ||
        stack_empty(&history->forward)
    ) {
        return UINT32_MAX;
    }

    // Current node becomes available through Back.
    if (!stack_push(&history->back, &history->current)) {
        return UINT32_MAX;
    }

    uint32_t next;

    if (!stack_pop(&history->forward, &next)) {
        return UINT32_MAX;
    }

    history->current = next;

    return next;
}

bool history_can_back(const History *history) {
    return history && !stack_empty(&history->back);
}

bool history_can_forward(const History *history) {
    return history && !stack_empty(&history->forward);
}

void history_clear(History *history) {
    if (!history) {
        return;
    }

    stack_clear(&history->back);
    stack_clear(&history->forward);

    history->current = UINT32_MAX;
    history->has_current = false;
}
