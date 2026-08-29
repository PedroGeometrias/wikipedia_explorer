#include "stack.h"

#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdio.h>

// initializing the stack, it takes the statck, the element size like sizeof(int), and the first cap, if you pass
// 0 as the cap, it makes it 8
bool stack_init(Stack *s,size_t elem_size,size_t initial_cap){
    // some check-ins
    if(!s||elem_size==0){
        return false;
    }

    // 0 behaviour
    if(initial_cap==0){
        initial_cap=8;
    }

    // allocating the data
    s->data = malloc(elem_size*initial_cap);
    // in case it goes wrong
    if(!s->data){
        s->elem_size=0;
        s->len=0;
        s->cap=0;
        return false;
    }

    // initial vals
    s->elem_size=elem_size;
    s->len=0;
    s->cap=initial_cap;

    return true;
}

// destroying the stack, it frees it and makes the zeros the elements
void stack_destroy(Stack *s){
    // checking the if the stack exists
    if(!s){
        printf("No Stack to destroy here\n");
        return;
    }

    // freeing the data inside the stack
    free(s->data);

    // nothing to dangle here
    s->data=NULL;
    s->elem_size=0;
    s->len=0;
    s->cap=0;
}

// here we grow the stack by new_elements
static bool stack_grow(Stack *s){
    // doing the growing by this much
    size_t new_cap=s->cap * 2;

    // this can only ever happen if the stack grows an insane huge amount, never really happening in this reality
    if(new_cap<s->cap){
        printf("How did you do this? the stack is too big");
        return false;
    }

    // allocating the data 
    void *new_data=realloc(s->data,new_cap*s->elem_size);
    if(!new_data)return false;

    // equalizing stuff
    s->data=new_data;
    s->cap=new_cap;

    return true;
}

// push an element into the stack
bool stack_push(Stack *s,const void *elem){

    // checking if every thing is ok
    if(!s||!elem||!s->data){
        return false;
    }

    if(s->len>=s->cap){
        if(!stack_grow(s))return false;
    }

    // cool trick here, we basically say the dst is gonna be pointed to da data + the length times the element size
    unsigned char *dst=s->data+(s->len*s->elem_size);

    // and then we copy into dst, the element, and pass the element size as the size
    memcpy(dst,elem,s->elem_size);

    // summing up the len
    s->len++;

    return true;
}

// popping the top of the stack
bool stack_pop(Stack *s,void *out){
    if(!s||!s->data||s->len==0){
        return false;
    }

    s->len--;

    unsigned char *src=s->data+(s->len*s->elem_size);

    if(out){
        memcpy(out,src,s->elem_size);
    }

    return true;
}

// taking the top, without actually popping it
bool stack_peek(const Stack *s,void *out){
    if(!s||!s->data||!out||s->len==0)return false;

    const unsigned char *src=s->data+((s->len-1)*s->elem_size);

    memcpy(out,src,s->elem_size);

    return true;
}

void stack_clear(Stack *s) {
    if (!s) return;
    s->len = 0;
}

// these are used to control te stack
bool stack_empty(const Stack *s){
    return !s||s->len==0;
}

size_t stack_len(const Stack *s){
    if(!s)return 0;
    return s->len;
}
