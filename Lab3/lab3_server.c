#include "lib/unp.h"

/*TODO: not sure why you need multiple CNTRL+D
		for the program to recognize you've reached the EOF */

int main(int argc, char* argv[])
{
	//error checking the arguments given (port number)
	if (argc != 2)
	{
		printf("Did not enter the right arguments: [port number to be added to 9877]\n");
		return EXIT_FAILURE;
	}
	if (argv[1] < 0)
	{
		printf("Port number to be added is less than 0.\n");
		return EXIT_FAILURE;
	}
	//init port number
	int port = 9877+atoi(argv[1]);
	printf("port number %d\n", port);

	FILE* file;
	char* filename;
	int					listenfd, connfd;
	struct sockaddr_in servaddr;
	char buffer[MAXLINE];


	//initializing socket
	listenfd = Socket(AF_INET, SOCK_STREAM, 0);

	bzero(&servaddr, sizeof(servaddr));
	servaddr.sin_family      = AF_INET;
	servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
	servaddr.sin_port        = htons(port);

	Bind(listenfd, (SA *) &servaddr, sizeof(servaddr));
	Listen(listenfd, LISTENQ);
	connfd = Accept(listenfd, (SA *) NULL, NULL);
	printf("Accepted Connection\n");

	printf("enter char: ");
	int chr = 0; //making sure user input is not EOF
	while (chr != EOF)
	{
		chr = getchar();
		putchar(chr);
		scanf("%s", buffer);	//reading in from standard input
		memmove(buffer+1, buffer, strlen(buffer));
		buffer[0] = chr;
		buffer[strlen(buffer)] = '\0';
		Send(connfd, buffer, strlen(buffer), 0);
		printf("Just sent buffer %s to client\n", buffer);
		memset(buffer, '\0', sizeof(char)*strlen(buffer));

	}
	printf("exited while loop\n");
	Close(connfd);
	//Close(listenfd);
	printf("Shutting down due to EOF\n");

}
