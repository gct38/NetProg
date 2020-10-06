#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <signal.h>
#include <string.h>
#include <ctype.h>
#include <sys/time.h>

#define SA struct sockaddr

struct client * clients[5];
int connected = 0;

struct client {
	int descriptor;	
	int playing;
	char userName[];
};
//Frees all allocated memory for the dictionary
void freeDict(char* dict[], int size) {
	int i;
	for (i = 0; i < size; ++i) {
		free(dict[i]);
	}
}
//Frees all allocated memory for the connected clients
void freeClients() {
	int i;
	for (i = 0; i < connected; ++i) {
		free(clients[i]);
	}
}

int validUserName(char buf[]) {
	for (int i = 0; i < connected; ++i) {
		if( !strcasecmp(buf,clients[i]->userName) ) {
			return 0;
		}
	}
	return 1;
}

int main(int argc, char* argv[]) {
	if (argc != 5) {
		fprintf(stderr,"Expected four argumments: [seed] [port] [dictonary_file] [longest_word_length]\n");
		return EXIT_FAILURE;
	}	

	srand(atoi(argv[1]));
	int port = atoi(argv[2]); 
	char *filename = argv[3];
	int longest_word_length = atoi(argv[4]);

	//opening and creating words array
	FILE* fp;
	char buf[longest_word_length];
	int n;
	int dictionary_size = 0;
	fd_set fds;

	fp = fopen(filename, "r");
	if (fp == NULL) {
		perror("Error while opening the file\n");
		exit(EXIT_FAILURE);
	}

	//Reading in and creating the dictionary
	while(fgets(buf,longest_word_length,fp)) dictionary_size++;	
	int i = 0;
	rewind(fp);
	char* dict[dictionary_size];
	while(fgets(buf,longest_word_length,fp)) {
		buf[strlen(buf)-1] = '\0';
		dict[i] = malloc(strlen(buf)+1);
		strcpy(dict[i++],buf);
	}

	//Seeding out the secret word
	char secret_word[longest_word_length];
	strcpy(secret_word, dict[rand() % dictionary_size]);

	printf("Secret word is %s\n", secret_word);	
	
	struct sockaddr_in servaddr;

	int listenfd = socket(AF_INET, SOCK_STREAM, 0);

	bzero(&servaddr, sizeof(servaddr));
	servaddr.sin_family = AF_INET;
	servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
	servaddr.sin_port = htons(port);

   bind(listenfd,(SA*)&servaddr,sizeof(servaddr));
	listen(listenfd, 5);

	while(1) {
		FD_ZERO( &fds );
		FD_SET( listenfd, &fds );

		for (i = 0; i < connected; ++i) {
			FD_SET(clients[i]->descriptor, &fds);
		}

		select(FD_SETSIZE, &fds, NULL, NULL, NULL);

		if (FD_ISSET(listenfd, &fds)) {
			int newClient = accept(listenfd, (SA*)NULL, NULL);
			write(newClient, "Welcome to Guess the Word,please enter your username.\n", 54);
			struct client * new = malloc(sizeof(struct client));
			new->descriptor = newClient;
			new->playing = 0;
			clients[connected++] = new;
		}
		//Loop through the open descriptors and check which ones had activity
		//TODO: Implement client disconnect handling
		for (i = 0; i < connected; ++i) {
			int cd = clients[i]->descriptor;
			if (FD_ISSET(cd, &fds)) {
				char buf[1024];
				char msg[1024];
				int len;
				//This logic is incomplete
				if ( !(len = read(cd,&buf,1024)) ){
					printf("User %s disconnected\n", clients[i]->userName);
				}
				buf[len-1] = 0;
				
				//Check to see if the user has started playing the game or not. If they haven't the server expects a username input next
				if (!clients[i]->playing) {
					if (validUserName(buf)) {						
						strcpy(clients[i]->userName,buf);
						strcpy(msg,"Let's start playing, ");
						strcat(msg, clients[i]->userName);
						strcat(msg, "\n");
						write(cd, msg, len+22);
						clients[i]->playing = 1;
					} else {
						strcpy(msg, "Username ");
						strcat(msg, buf);
						strcat(msg, " is already taken, please enter a different username\n");
						write(cd, msg, len+62);
					}										
				}
			}		
		} 
	}
	
	fclose(fp);
	freeDict(dict,dictionary_size);
	freeClients();	
	
	return EXIT_SUCCESS;
}
