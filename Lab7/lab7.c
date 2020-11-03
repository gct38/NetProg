#include <sys/types.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <netdb.h>

#define BUF_SIZE 500

int main(int argc, char* argv[]) {
   
   if (argc != 2) {
      fprintf(stderr, "Incorrect number of arguements!\n");
      return EXIT_FAILURE;
   }

   char* hostname = argv[1];

   struct addrinfo hints;
   struct addrinfo *result, *rp;
   int s;
   struct sockaddr_storage peer_addr;
   socklen_t peer_addr_len;
   ssize_t nread;
   char buf[BUF_SIZE];

   memset(&hints, 0, sizeof(hints));
   hints.ai_family = AF_UNSPEC;
   hints.ai_socktype = SOCK_STREAM;
   hints.ai_flags = AI_PASSIVE;
   
   if ( (s = getaddrinfo(argv[1], NULL, &hints, &result)) != 0 ) {
      perror("getaddrinfo() failed!");
      fprintf(stderr, "Interpreting return status code: %s\n", gai_strerror(s));
      exit(EXIT_FAILURE);
   }

   for (rp = result; rp != NULL; rp = rp->ai_next) {
      getnameinfo(rp->ai_addr, rp->ai_addrlen, buf, sizeof (buf), NULL, 0, NI_NUMERICHOST);
      puts(buf);
   }

   freeaddrinfo(result);



   return EXIT_SUCCESS;
}