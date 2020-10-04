#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>

struct values {
    int val1;
    int val2;
};

void* add(void* inp) {
    struct values * temp = inp;    
    if (temp->val2) {
        temp->val2--;
        return (void*)(1+add((void*)temp));
    } else {              
        long ret = temp->val1;           
        free(temp);
        return (void*)ret;
    } 
}

int main(int argc, char* argv[]) {
    
    if (argc != 2) {
        fprintf(stderr, "Incorrect number of arguements\n");
        return 1;
    }

    int MAX_ADDAND = atoi(argv[1]);
    pthread_t children[MAX_ADDAND*MAX_ADDAND-1];
    
    int j;
    int i;
    int index = 0;
    for (i = 1; i < MAX_ADDAND; ++i) {
        for (j = 1; j <= MAX_ADDAND; ++j) {
            printf("Main starting thread add() with [%d + %d]\n", i, j);
            pthread_t tid;
            struct values* temp = malloc(sizeof(struct values));
            temp->val1 = i;
            temp->val2 = j;
            int val = pthread_create(&tid, NULL, add, (void*)temp);
            if (val < 0) {
                fprintf(stderr, "pthread_create() failed!\n");
                return -1;
            } else { 
                printf("Thread %ld running add() with [%d + %d]\n", tid, i, j);                 
                children[index++] = tid;}
        }
    }
    int secondaryIndex = 0;
    for (i = 1; i < MAX_ADDAND; ++i) {
        for (j = 1; j <= MAX_ADDAND; ++j) {
            long* ret_val;
            pthread_join(children[secondaryIndex],(void**)&ret_val);
            printf("In main, collecting thread %lu computed [%d + %d] = %ld\n", children[secondaryIndex++],i,j, (long)ret_val);
        }
    }

    return 0;
}