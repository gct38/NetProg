#include "lib/unp.h"

//This should be fully implemented correctly.
//Want to test it more thoroughly

int connections = 0;

void str_cli(FILE *fp, int sockfd)
{
	int inputEOF, maxfdp1, val;
	fd_set rset;
	char buffer[MAXLINE];
	/*
	while (Fgets(sendline, MAXLINE, fp) != NULL) {

		Writen(sockfd, sendline, strlen(sendline));

		if (Readline(sockfd, recvline, MAXLINE) == 0)
			err_quit("str_cli: server terminated prematurely");

		Fputs(recvline, stdout);
	}
	*/

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
		Select(maxfdp1, &rset, NULL, NULL, NULL);

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
			Write(fileno(stdout), buffer, val);
		}

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
			Write(sockfd, buffer, val);
		}
	}
}


int main(int argc, char* argv[])
{
	int userPort;
	char loopback[] = "127.0.0.1";

	int					sockfd;
	struct sockaddr_in	servaddr;


	sockfd = Socket(AF_INET, SOCK_STREAM, 0);

	bzero(&servaddr, sizeof(servaddr));
	servaddr.sin_family = AF_INET;
	//servaddr.sin_addr.s_addr = htonl(INADDR_ANY);

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
		//TODO: client function;
		str_cli(stdin, sockfd);		/* do it all */
	}
	exit(0);
}
