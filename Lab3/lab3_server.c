#include "../lib/unp.h"

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

	FILE* file;
	char* filename;
	int					listenfd, connfd;
	struct sockaddr_in servaddr;
	char buffer[MAXLINE];


	//initializing socket
	listenfd = socket(AF_INET, SOCK_STREAM, 0);

	bzero(&servaddr, sizeof(servaddr));
	servaddr.sin_family      = AF_INET;
	servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
	servaddr.sin_port        = htons(port);

	bind(listenfd, (struct sockaddr *) &servaddr, sizeof(servaddr));

	//look for a connection
	while(1) {
		listen(listenfd, LISTENQ);
		connfd = accept(listenfd, (struct sockaddr *) NULL, NULL);
		printf(">Accepted connection\n");

		//we need to check for input from stdin and check if the client has closed the connection
		//select is the solution
		while(1) {
			fd_set fds;
			FD_ZERO(&fds);
			FD_SET(fileno(stdin), &fds);
			FD_SET(connfd, &fds);
			int max_fd = max(fileno(stdin), connfd);

			select(max_fd + 1, &fds, 0, 0, 0);

			// client is readable -- this should only happen if the connection has closed
			if (FD_ISSET(connfd, &fds)) {
				printf(">str_cli: client disconnected\n");
				close(connfd);
				FD_CLR(connfd, &fds);
				// get rid of anything in the input stream as well (consume it without using it)
				if (FD_ISSET(fileno(stdin), &fds)) {
					read(fileno(stdin), buffer, MAXLINE);
				}
				break;
			}

			// stdin is readable -- we have a line to send to the client
			if (FD_ISSET(fileno(stdin), &fds)) {
				int val = read(fileno(stdin), buffer, MAXLINE);
				if (val == 0) {
					//EOF
					printf(">Shutting down due to EOF\n");
					close(connfd);
					exit(0);
				} else {
					buffer[val] = 0;
					send(connfd, buffer, val, 0);
				}
			}
		}
	}
}
