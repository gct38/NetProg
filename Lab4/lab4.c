#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>


int MAX_ADDAND;

//struct for 2 values to be added
struct pair {
	long x;
	long y;
} pair;


void * add(void * v) {
	struct pair *values = malloc(sizeof(pair));
	values = (struct pair*) v;
	printf("Thread %lu running add() with [%lu + %lu]\n", pthread_self(), values->x, values->y);
	if (values->y) {
			values->y--;
			return (void*)(1+add((void*)values));
	}
	else {
		return (void*)values->x--;
	}
}


int main(int argc, char* argv[]) {
	if (argc != 2) {
		printf("Need to input the proper arguments: [MAX_ADDAND]\n");
		exit(1);
	}
	MAX_ADDAND = atoi(argv[1]);
	int NUM_CHILD = (MAX_ADDAND-1) * MAX_ADDAND;

	pthread_t children[NUM_CHILD];
	printf("num children %d\n\n", NUM_CHILD);

	for (long i=0; i<MAX_ADDAND-1; i++) {
		for (long j=0; j<MAX_ADDAND; j++) {
			struct pair adders = { i+1,j+1 };	//two values to add recursively
			struct pair* addersPtr = &adders;

			pthread_t tid;
			int val = pthread_create(&tid, NULL, add, (void*)addersPtr);

			if (val < 0) return -1;
			else children[(i*MAX_ADDAND)+j] = tid;
			printf("Main starting thread %lu add() for [%lu + %lu]\n", tid, i+1, j+1);


		}
	}

	//retreiving result from threads
	for (long i=0; i<NUM_CHILD; i++) {
		long *ret_val;
		pthread_join(children[i], (void**)&ret_val);
		printf("In main, collecting thread %lu computed [x + y] = %lu\n\n", children[i], (long)ret_val);
	}



	return 0;
}
