#include <stdio.h>
#include <time.h>
#include <unistd.h>
#include <stdlib.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <signal.h> 



int main(int argc, char* argv[]) {
	if (argc != 5) {
		printf("Expected four argumments: [seed] [port] [dictonary_file] [longest_word_length]\n");
		return 1;
	}

	int seed = atoi(argv[1]);
	int port = atoi(argv[2]); 
	char *filename = argv[3];
	int longest_word_length = atoi(argv[4]); 

	//opening and creating words array
	FILE *fp;
	char buffer;
	int lines = 0;

	fp = fopen(filename, "r");
	if (fp == NULL) {
		perror("Error while opening the file\n");
		exit(EXIT_FAILURE);
	}
	while ((buffer=fgetc(fp)) != EOF) lines++;	
	rewind(fp);
	printf("number of lines %d\n", lines);
	lines = 0;

	char words[lines];
	while ((buffer=fgetc(fp)) != EOF) { 
		words[lines]; 
		lines++; 
	}	

	printf("number of words %d\n", lines);
	return 0;
}
