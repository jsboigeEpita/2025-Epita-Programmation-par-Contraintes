#ifndef QUEUE_H
#define QUEUE_H

struct node {
    struct node *next;
    unsigned long long data;
};

struct queue {
    struct node *first;
    struct node *last;
    unsigned long long nb;
};

struct queue *createQueue();
char isEmpty(struct queue *queue);
void enqueue(struct queue *queue, unsigned long long data);
unsigned long long dequeue(struct queue *queue);
void freeQueue(struct queue *queue);

#endif // QUEUE_H