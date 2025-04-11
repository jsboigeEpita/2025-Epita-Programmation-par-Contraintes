#include "queue.h"

#include <stdio.h>
#include <stdlib.h>

struct queue *createQueue() {
    struct queue *queue = malloc(sizeof(struct queue));
    if (queue == NULL) {
        printf("OUT OF MEMORY !\n");
        exit(1);
    }
    queue->first = NULL;
    queue->last = NULL;
    queue->nb = 0;

    return queue;
}

char isEmpty(struct queue *queue) {
    return queue->first == NULL;
}

void enqueue(struct queue *queue, unsigned long long data) {
    struct node *node = malloc(sizeof(struct node));
    if (node == NULL) {
        printf("OUT OF MEMORY !\n");
        exit(1);
    } 
    node->data = data;
    node->next = NULL;

    if (queue->first == NULL) {
        queue->first = node;
    }
    else {
        queue->last->next = node;
    }

    queue->last = node;
    queue->nb = queue->nb + 1;
}

unsigned long long dequeue(struct queue *queue) {
    struct node *node = queue->first;
    unsigned long long data = node->data;

    queue->first = node->next;
    if (queue->first == NULL) {
        queue->last = NULL;
    }

    queue->nb = queue->nb - 1;

    free(node);
    return data;
}

void freeQueue(struct queue *queue) {
    for (; !isEmpty(queue); ) {
        dequeue(queue);
    }

    free(queue);
}