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
char* secret_word;
int swlen;
fd_set fds;

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
//Validates that the username is not already in use
int validUserName(char buf[]) {
	for (int i = 0; i < connected; ++i) {
		if( !strcasecmp(buf,clients[i]->userName) ) {
			return 0;
		}
	}
	return 1;
}
//Find the disconnected user and delete its presence
void removeUser(int fd) {
   int i;
   int j;
   for (i = 0; i < connected; ++i) {
      if (clients[i]->descriptor == fd) {
         free(clients[i]);
         for (j = i; j < connected-1; ++j) {
            clients[j] = clients[j+1];
         } 
         connected--;
         break;
      } 
   }
}
//Send the current number of users connected to the newly connected player
void sendNumUsers(int fd) {
   char msg[256];
   sprintf(msg, "There are %d player(s) playing. The secret word is %d letter(s).\n",connected, swlen);
   write(fd, msg, strlen(msg));
}

void disconnectAll() {
   int i;
   for (i = 0; i < connected; ++i) {
      close(clients[i]->descriptor);
      FD_CLR(clients[i]->descriptor, &fds);
      free(clients[i]);
   } 
   connected = 0;
}

void guessedWord(char user[]) {
   int i;
   for (i = 0; i < connected; ++i) {
		if (clients[i]->playing) {
			char msg[1024];
			sprintf(msg, "%s has correctly guessed the word %s\n", user, secret_word);
			printf("%s",msg);
			write(clients[i]->descriptor, msg, strlen(msg));
		}
   }
}

int handleGuess(char guess_word[], struct client * client) {

   if (!strcasecmp(guess_word,secret_word)) {
      return 1;
   }

   int correctPlace = 0;
   int correctLetter = 0;

   int i;
   int j;
   int* consumed = calloc(swlen, sizeof(int));   
   for (i = 0; i < swlen; ++i) {
      if ( tolower(guess_word[i]) == tolower(secret_word[i]) ) {
         correctPlace++;
      }
      for (j = 0; j < swlen; ++j) {
         if ( tolower(secret_word[i]) == tolower(guess_word[j]) && !consumed[j] ) {
            correctLetter++;
            consumed[j] = 1;
            break;
         }
      }
   }
   free(consumed);
   char msg[1024];
   sprintf(msg, "%s guessed %s: %d letter(s) were correct and %d letter(s) were correctly placed.\n", client->userName, guess_word, correctLetter, correctPlace);
   printf("%s",msg);
   for (i = 0; i < connected; ++i) {
		if (clients[i]->playing) {
      write(clients[i]->descriptor, msg, strlen(msg));
		}
   }

   return 0;
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
		dict[i] = calloc(strlen(buf)+1, sizeof(char));
		strcpy(dict[i++],buf);
	} fclose(fp);

	//Seeding out the secret word
   int temp = rand() % dictionary_size;
   secret_word = calloc(strlen(dict[temp])+1, sizeof(char));
   strcpy(secret_word, dict[temp]);
   swlen = strlen(secret_word);

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
		FD_ZERO(&fds);
		FD_SET(listenfd, &fds);

		for (i = 0; i < connected; ++i) {
			FD_SET(clients[i]->descriptor, &fds);
		}

		select(FD_SETSIZE, &fds, NULL, NULL, NULL);

		if (FD_ISSET(listenfd, &fds)) {
			int newClient = accept(listenfd, (SA*)NULL, NULL);
			write(newClient, "Welcome to Guess the Word, please enter your username.\n", 55);
			struct client * new = calloc(1, sizeof(struct client));
			new->descriptor = newClient;
			new->playing = 0;
			clients[connected++] = new;
		}
		//Loop through the open descriptors and check which ones had activity
		for (i = 0; i < connected; ++i) {
			int cd = clients[i]->descriptor;
			if (FD_ISSET(cd, &fds)) {
				char buf[1024];
				char msg[4096];
				int len;
				if ( !(len = read(cd,&buf,1024)) ){
					printf("User %s disconnected\n", clients[i--]->userName);
               close(cd);
               FD_CLR(cd,&fds);
               removeUser(cd);
               continue;               
				}
				buf[--len] = 0;
				
				//Check to see if the user has started playing the game or not. If they haven't the server expects a username input next
				if (!clients[i]->playing) {
					if (validUserName(buf)) {						
						strcpy(clients[i]->userName,buf);
                  printf("User %s connected successfully\n", buf);						
						clients[i]->playing = 1;
                  sprintf(msg, "Let's start playing, %s\n", clients[i]->userName);
                  write(cd, msg, strlen(msg));
                  sendNumUsers(cd);
					} else {
                  sprintf(msg, "Username %s is already taken, please enter a different username\n", buf);
						write(cd, msg, strlen(msg));
					}										
				} else {
               if (len != swlen) {
                  sprintf(msg, "Invalid guess length. The secret word is %d letter(s).\n",swlen);
                  write(cd, msg, strlen(msg));
               } else {
                  int guessed = handleGuess(buf,clients[i]);
                  if (guessed) {
                     guessedWord(clients[i]->userName);
                     disconnectAll();
                     int temp = rand() % dictionary_size;
                     secret_word = realloc(secret_word, strlen(dict[temp])+1);
                     strcpy(secret_word,dict[temp]);
                     swlen = strlen(secret_word);
                     printf("Secret word is %s\n", secret_word);
                  }
               }               
            }
			}		
		}
	}	
	
	freeDict(dict,dictionary_size);
	freeClients();
   free(secret_word);
	
	return EXIT_SUCCESS;
}
