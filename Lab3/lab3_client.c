#include "../lib/unp.h"

int handle_connection(int sockfd, struct sockaddr_in servaddr)
{
	int val;
	char buffer[MAXLINE];

	if ((val = read(sockfd, buffer, MAXLINE)) == 0) {
		printf(">Server on %d closed.\n", ntohs(servaddr.sin_port));
		return 1;
	}
	buffer[val] = 0; 
	printf(">%d %s", ntohs(servaddr.sin_port), buffer);
	fflush(stdout);
	return 0;

}


int main(int argc, char* argv[])
{
	//printf("start\n");
	char loopback[] = "127.0.0.1";

	int					sockets[5];
	struct sockaddr_in	servaddr[5];

	fd_set connections;

	//printf("building fdset\n");
	int max_fd = fileno(stdin);
	int i;
	for (i = 0; i < 5; i++) {
		sockets[i] = socket(AF_INET, SOCK_STREAM, 0);
		max_fd = max(max_fd, sockets[i]);
		bzero(servaddr + i, sizeof(struct sockaddr_in));
		servaddr[i].sin_family = AF_INET;
	}

	while (1)
	{	
		//printf("Ready for connections\n");
		// set the fds to check for 
		FD_ZERO(&connections);
		FD_SET(fileno(stdin), &connections);
		for (i = 0; i < 5; i++) {
			if (servaddr[i].sin_port > 0) {
				FD_SET(sockets[i], &connections);
			}
		}

		// select
		int rv = select(max_fd + 1, &connections, NULL, NULL, NULL);
		//printf("%d fd(s) ready\n", rv);

		//client function
		for (i = 0; i < 5; i++) {
			if (FD_ISSET(sockets[i], &connections)) {
				int closed = handle_connection(sockets[i], servaddr[i]);
				if (closed) {
					// close this socket and reopen for another connection
					shutdown(sockets[i], SHUT_RDWR);
					close(sockets[i]);
					FD_CLR(sockets[i], &connections);
					sockets[i] = socket(AF_INET, SOCK_STREAM, 0);
					max_fd = max(max_fd, sockets[i]);
					bzero(servaddr + i, sizeof(struct sockaddr_in));
					servaddr[i].sin_family = AF_INET;
				}
			}
		}

		// read user input
		if (FD_ISSET(fileno(stdin), &connections)) {
			//printf("stdin readable\n");
			char buffer[10];
			int bytes = read(fileno(stdin), buffer, 10);
			buffer[bytes] = 0;
			int port = atoi(buffer);
			// find an available socket
			for (i = 0; i < 5; i++) {
				if (servaddr[i].sin_port == 0) {
					//printf("given port %d\n", port);
					servaddr[i].sin_port = htons(port);
					inet_pton(AF_INET, loopback, &(servaddr[i].sin_addr));
					if (connect(sockets[i], (struct sockaddr *) servaddr + i, sizeof(*(servaddr + i))) != 0) {
						//printf(">Failed to connect to port %d. Error: %s.\n", port, strerror(errno));
					}
					break;
				}
			}
		}

		
	}
	exit(0);
}
