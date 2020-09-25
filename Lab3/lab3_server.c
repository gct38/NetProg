#include "lib/unp.h"

//TODO: implement a way to read that the client closed the Socket
//		will then need to gracefully close the server.
//		perform Read or Recv action on client?

/*TODO: seems like there's a bug where the server segfaults everytime there's
		input from the server. */

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

	//file = fopen(filename, "r");
	//int chr = getc(file);
	int chr = getchar();
	while (chr != EOF or )
	{
		putchar(chr);
		scanf(chr, buffer);

	}
	Send(connfd, buffer, strlen(buffer), 0);
	Close(connfd);
	//Close(listenfd);
	printf("Shutting down due to EOF\n");

}
