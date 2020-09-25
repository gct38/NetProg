#include "../unpv13e/lib/unp.h"

int counter = 0;

void handler(int sig) {
    pid_t child = waitpid(-1, NULL, WNOHANG);    
    printf("Parent sees child PID %d has terminated\n", child);
    counter += 1;
}

int main() {

    char input[2];
    signal(SIGCHLD, handler);

    printf("Number of Children to Spawn: ");
    scanf("%s", input);

    int numOfC = atoi(input);
    printf("Told to spawn %d children\n", numOfC);

    for (int i = 0; i < numOfC; ++i) {
        pid_t childPid = fork();      
        
        if (childPid > 0) {
            printf("Parent spawned child PID %d\n", childPid);            
        } else if (childPid < 0) {
            perror("fork() error!\n");
            exit(EXIT_FAILURE);
        } else {
            srand(time(NULL) + getpid());
            int death = rand() % 6;
            printf("Child %d dying in %d seconds\n", getpid(), death);
            sleep(death);
            printf("Child PID %d terminating.\n", getpid());
            return EXIT_SUCCESS;
        }
    }

    while(counter != numOfC);       

    return EXIT_SUCCESS;
}

