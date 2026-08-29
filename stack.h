#ifndef STACK_H
#define STACK_H

#include <stdbool.h>
#include <stddef.h>

// our stack
typedef struct Stack{
    // block of bytes
    unsigned char *data;
    // each element size
    size_t elem_size;
    // the lenght of the stack
    size_t len;
    // cap
    size_t cap;
}Stack;

// memory operations
bool stack_init(Stack *s,size_t elem_size,size_t initial_cap);
void stack_destroy(Stack *s);

// stack operations
bool stack_push(Stack *s,const void *elem);
bool stack_pop(Stack *s,void *out);
bool stack_peek(const Stack *s,void *out);
void stack_clear(Stack *s);

// control operations
bool stack_empty(const Stack *s);
size_t stack_len(const Stack *s);

#endif
