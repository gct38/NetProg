#include <sys/types.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <netdb.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>

int main(int argc, char* argv[]) {
   int option_value[1];
   socklen_t option_len = sizeof(option_value);
   int sock;
   struct sockaddr_in servaddr;


   if (argc != 2) {
      printf("Proper usage is %s [IP Hostname]\n", argv[0]);
      return EXIT_FAILURE;
   }
   
   bzero(&servaddr,sizeof(servaddr));
   servaddr.sin_family = AF_INET;
   servaddr.sin_port = htons(80);
   inet_aton(argv[1], &servaddr.sin_addr);

   sock = socket(AF_INET, SOCK_STREAM, 0);

   getsockopt(sock, IPPROTO_TCP, TCP_MAXSEG, option_value, &option_len);
   printf("Prior values:\nMMS: %d\n", *option_value);

   option_len = sizeof(option_value);
   getsockopt(sock, IPPROTO_TCP, SO_RCVBUF, option_value, &option_len);
   printf("RCVBUF: %d\n\n", *option_value);

   connect(sock, (struct sockaddr*)&servaddr, sizeof(servaddr));

   option_len = sizeof(option_value);
   getsockopt(sock, IPPROTO_TCP, TCP_MAXSEG, option_value, &option_len);
   printf("After connection\nMMS: %d\n", *option_value);

   option_len = sizeof(option_value);
   getsockopt(sock, IPPROTO_TCP, SO_RCVBUF, option_value, &option_len);
   printf("RCVBUF: %d\n", *option_value);

   close(sock);

   return EXIT_SUCCESS;
}