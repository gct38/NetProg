#include <sys/types.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <netdb.h>
#include <netinet/tcp.h>

#define BUF_SIZE 500

int main(int argc, char* argv[]) {
   if (argc != 2) {
      printf("Proper usage is %s [IP Hostname]\n", argv[0]);
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

   char option_value;
   int option_len;

   memset(&hints, 0, sizeof(hints));
   hints.ai_family = AF_UNSPEC;
   hints.ai_socktype = SOCK_STREAM;
   hints.ai_flags = AI_PASSIVE;

   if ( (s = getaddrinfo(argv[1], NULL, &hints, &result)) != 0 ) {
      perror("getaddrinfo() failed!");
      fprintf(stderr, "Interpreting return status code: %s\n", gai_strerror(s));
      exit(EXIT_FAILURE);
   }

   int sock;
   for (rp = result; rp != NULL; rp = rp->ai_next) {
      sock = socket(rp->ai_family, rp->ai_socktype, rp->ai_protocol);
      if (sock == -1) continue;

      getsockopt(sock, IPPROTO_TCP, SO_RCVBUF, &option_value, &option_len);
      printf("SO_RCVBUF: %d\n", option_value);
      getsockopt(sock, IPPROTO_TCP, SO_SNDBUF, &option_value, &option_len);
      printf("SO_SENDBUF: %d\n", option_value);

      // connect(sock, rp->ai_addr, rp->ai_addrlen);
      
      close(sock);
      break;
   }

   freeaddrinfo(result);




   return EXIT_SUCCESS;
}