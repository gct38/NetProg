#include "lib/unp.h"

/* TODO: seems like there's an issue where there
		 client is 1 behind from the server */

/* TODO: need to implement something to prevent
		 client from closing when server closes*/

/* TODO: test and make sure that we can connect
		 multiple servers simultaneously
		 (don't actually think this is working..)*/

int connections = 0;
int userPort;

void str_cli(FILE *fp, int sockfd)
{
	int inputEOF, maxfdp1, val;
	fd_set rset;
	char buffer[MAXLINE];


	printf("str_cli function, connections: %d\n", connections);
	FD_ZERO(&rset);
	for ( ; ; )
	{
		if (!inputEOF)
		{
			FD_SET(fileno(fp), &rset);
		}

		FD_SET(sockfd, &rset);
		maxfdp1 = max(fileno(fp), sockfd) + 1;
		//printf("entering select\n");
		Select(maxfdp1, &rset, NULL, NULL, NULL);

		//printf("Got info from socket!!\n");

		/* socket is readable */
		if (FD_ISSET(sockfd, &rset))
		{
			if (val = Readline(sockfd, buffer, MAXLINE) == 0)
			{
				if (feof(&sockfd))
				{
					return;
				}
				else
				{
					connections--;
					printf("Premature Client Termination\n");
					exit(1);
				}
			}
			//printf("trying to write this stdout to socket.. buffer: %s\n", buffer);
			Write(fileno(stdout), buffer, val);
		}
		//printf("past the socket is readable portion\n");
		/* input is readable */
		if (FD_ISSET(fileno(fp), &rset))
		{
			if (val = Read(fileno(fp), buffer, MAXLINE) == 0)
			{
				inputEOF = 1;
				Shutdown(sockfd, SHUT_WR);
				FD_CLR(fileno(fp), &rset);
				continue;
			}
			//printf("trying to write to the socket.. buffer: %s\n", buffer);
			Write(sockfd, buffer, val);
		}
		buffer[strlen(buffer)-1] = '\0';
		printf("printing..... %d %s\n", userPort, buffer);
	}
}


int main(int argc, char* argv[])
{
	char loopback[] = "127.0.0.1";

	int					sockfd;
	struct sockaddr_in	servaddr;


	sockfd = Socket(AF_INET, SOCK_STREAM, 0);

	bzero(&servaddr, sizeof(servaddr));
	servaddr.sin_family = AF_INET;

	while (1)
	{
		if (connections < 5)
		{
			scanf("%d", &userPort);
			printf("given port %d\n", userPort);
			servaddr.sin_port = htons(userPort);
			Inet_pton(AF_INET, loopback, &servaddr.sin_addr);
			Connect(sockfd, (SA *) &servaddr, sizeof(servaddr));
			printf("connected to %s at port %d\n", loopback, userPort);
		}
		connections++;
		//client function;
		str_cli(stdin, sockfd);		/* do it all */
	}
	exit(0);
}
