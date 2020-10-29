#include <stdio.h>
#include <time.h>
#include <unistd.h>
#include <stdlib.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <signal.h>

//Global Variable Declaration
char buffer[1024];
int alarms; // number of times SIGALRM has been received since last packet
int conn_fd;
int conn_msglen;
struct sockaddr_in client;

/*
Alarm Handler
Every alarm, we resend the last packet
If 10 seconds, then there's a timeout and we kill the process
*/
void handler(int sig) {
	alarms++;
	// if it's been ten seconds, kill the process
    if (alarms >= 10) {
        printf("Timeout.\n");
    	exit(1);
    } else {
    	// otherwise, resend the last packet and set a new alarm
        printf("Resending latest packet...\n");
    	sendto(conn_fd, buffer, conn_msglen, 0, (struct sockaddr *)&client, sizeof(struct sockaddr_in)); // resend packet
    	alarm(1);
    }
}

// enumeration for opcodes
enum OpCodes {
	RRQ = 1,
	WRQ,
	DATA,
	ACK,
	ERROR
};

/*
Creates ACK packet
Populates ACK opcode (2 bytes) and the block number (2 bytes)
*/
int CreateACKPacket(int block_number){
    printf("sending ACK %d\n", block_number);
	buffer[0] = 0;
	buffer[1] = ACK;
	buffer[2] = block_number >> 8;
	buffer[3] = (block_number & 0x00ff);
	return 4;
}

/*
Creates ERROR packet
Populates ERROR opcode (2 bytes), error code (2 bytes), then error message(str), then a 0 at the end (1 byte)
*/
int CreateErrorPacket(int error_code, char* error_msg, int msg_len){
    printf("sending ERROR %d\n", error_code);
	buffer[0] = 0;
	buffer[1] = ERROR;
	buffer[2] = 0;
	buffer[3] = error_code;
	int i = 0;
	for( ; i < msg_len; i++) {
		buffer[i+4] = error_msg[i];
	}
	buffer[msg_len] = 0;
	return msg_len + 5;
}


/*
Creates DATA packet
Populates DATA opcode (2 bytes), block number (2 bytes), followed by the data (n bytes)
If the data is too long, it will split itself.
We know we're at the end of the data when the data is less than 512
*/
int CreateDataPacket(FILE* f_ptr, int block_number){
    printf("sending DATA\n");
	buffer[0] = 0;
	buffer[1] = DATA;
	buffer[2] = block_number >> 8;
	buffer[3] = (block_number & 0x00ff);
	char c;
	int bytes_read = 0;
	while(bytes_read <= 512 && (c = fgetc(f_ptr)) != EOF) {
		bytes_read++;
		buffer[3 + bytes_read] = c;
	}
	return bytes_read + 4;
}


/*
This is where the main logic of our code is
It handles each individual TID.
Once we receive a packet from the client, we parse through the client's OpCode
	to and from there we have switch statement to handle the appropriate action
	to send a packet back to the client
*/
void HandleConnection(int server_port) {

	FILE* fptr;
    int block;
    int rwmode; // 0 for reading, 1 for writing
    conn_fd = socket(AF_INET, SOCK_DGRAM, 0);
    int bytes_recv;
    char clientbuf[1024];

    // special error packet
    char errbuf[5];
    errbuf[0] = 0;
    errbuf[1] = 5;
    errbuf[2] = 0;
    errbuf[3] = 5;
    errbuf[4] = 0;

    struct sockaddr_in server;
    server.sin_family = AF_INET;
    server.sin_addr.s_addr = htonl(INADDR_ANY);
    server.sin_port = htons(server_port);

    int rc = bind(conn_fd,(const struct sockaddr *)&server,sizeof(server));
    if (rc < 0) {
    	printf("sadface\n");
    } else {
        printf("connection handled on port %d\n", server_port);
    }

    unsigned short int opcode = (buffer[0] << 8)|buffer[1];
    printf("initial opcode %d\n", opcode);
    switch(opcode) {
    	case RRQ:

        rwmode = 0;

    	fptr = fopen(buffer + 2, "rb"); // opens specified file, if it exists

    	if (!fptr) {
    		// failed to open file -- send back ERROR packet
    		conn_msglen = CreateErrorPacket(1, "", 0);
    	} else {
    		// send back DATA packet
    		conn_msglen = CreateDataPacket(fptr, 1);
    	}

        block = 0;

    	break;

    	case WRQ:

        rwmode = 1;

        //check for error in file
        if (access( buffer+2, F_OK) != -1) {
            // file already exists
            conn_msglen = CreateErrorPacket(6, "", 0);
        } else {
            //send back ACK
            fptr = fopen(buffer + 2, "wb");
            conn_msglen = CreateACKPacket(0);
        }

    	break;

    	default:
    	//send back ERR 4
        printf("initial opcode not a request thingy\n");
        conn_msglen = CreateErrorPacket(4, "", 0);
    	break;
    }

    sendto(conn_fd, buffer, conn_msglen, 0, (struct sockaddr *)&client, sizeof(struct sockaddr_in)); // send packet
    alarm(1);

    // send/receive loop
    while(1) {
        struct sockaddr_in tmp_client;
        socklen_t sz = sizeof(struct sockaddr_in);
        bytes_recv = recvfrom(conn_fd,clientbuf,1024,0,(struct sockaddr *)&tmp_client,&sz); //receive packet
        clientbuf[bytes_recv] = 0;
        printf("%d\n", bytes_recv);
        if (tmp_client.sin_port != client.sin_port) {
            //send back an error packet
            sendto(conn_fd, errbuf, 5, 0, (struct sockaddr *)&tmp_client, sizeof(struct sockaddr_in));
            continue;
        }
        alarm(0); // kill timeout alarm
        opcode = (clientbuf[0] << 8)|clientbuf[1]; //parse packet
        printf("got opcode %d\n", opcode);
        switch(opcode) {
            case DATA:
                // check rwmode, return error 4 if in read mode
                if(rwmode != 1){
                    conn_msglen = CreateErrorPacket(4, "", 0);
                    break;
                }
                // get blocknum from packet
                int data_block = (clientbuf[2] << 8)|clientbuf[3];
                if(data_block > block){
                	block = data_block;
                	// write to fptr
                	fwrite(clientbuf+4, sizeof(char), bytes_recv - 4, fptr);
                	// CreateAckPacket
                	conn_msglen = CreateACKPacket(block);
                	// if we got less than 512 bytes of data, this is the last packet.
                	if (bytes_recv - 4 < 512) {
                    	fclose(fptr);
                    	rwmode = -1;
                	}
                } else {
                	conn_msglen =CreateErrorPacket(5, "", 0);
                }
                break;
            case ACK:
                // check rwmode, return error 4 if in write mode
                 if(rwmode != 0){
                    conn_msglen = CreateErrorPacket(4, "", 0);
                    break;
                }
                block++;
                // CreateDataPacket
                conn_msglen = CreateDataPacket(fptr, block);
                // if we're sending less than 512 bytes of data (packet size 517), we're done writing
                if (conn_msglen < 517) {
                    fclose(fptr);
                    rwmode = -1;
                }
                break;
            default:
                // error 4
                conn_msglen = CreateErrorPacket(4, "", 0);
                fclose(fptr);
                break;
        }
        //send response
        int ret = sendto(conn_fd, buffer, conn_msglen, 0, (struct sockaddr *)&client, sizeof(struct sockaddr_in)); // send packet
        printf("sent %d bytes\n", ret);
        alarm(1); // set timeout alarm
    }

}


//MAIN
int main(int argc, char* argv[]) {

	//Error checking the arguments
    if (argc > 3) {
        printf("Too many arguments\n");
        return EXIT_FAILURE;
    } if (argc < 2) {
        printf("Expected two arguments: [start of port range] [end of port range]\n");
        return EXIT_FAILURE;
    }

    // register the signal handler
    signal(SIGALRM, handler);

    int startPort = atoi(argv[1]);
    int currentPort = startPort;
    int endPort = atoi(argv[2]);

	//error checking the ports given
    if (startPort < 0 || endPort < 0) {
    	printf("Ports cannot have negative values\n");
    	return EXIT_FAILURE;
    } if (startPort >= endPort) {
    	printf("Starting port larger than Ending port. Exiting\n");
    	return EXIT_FAILURE;
    }


	//initialization of the server
    int udp = socket(AF_INET, SOCK_DGRAM, 0);

    if (udp < 0) {
        fprintf(stderr, "ERROR: socket() UDP!\n");
        return EXIT_FAILURE;
    }

    struct sockaddr_in server;
    socklen_t sz = sizeof(struct sockaddr_in);
    server.sin_family = AF_INET;
    server.sin_addr.s_addr = htonl(INADDR_ANY);
    server.sin_port = htons(startPort);

    int rc = bind(udp,(const struct sockaddr *)&server,sizeof(server));
    if (rc >= 0) {
        printf("listening on port %d\n", startPort);
    } else {
        exit(1);
    }

    alarms = 0;
	//while loop to go thru and handle any TIDs
	//	will fork and create new child processes
	//	to handle any TFTP action
    while(currentPort <= endPort) {

        if (currentPort == 69) {
            currentPort++;
            continue;
        }

        int msgLen = recvfrom(udp,buffer,1024,0,(struct sockaddr*)&client,&sz);
        buffer[msgLen] = '\0';
        printf("received message from client\n");
        currentPort++;

        pid_t child = fork();
        if (child > 0) {
            continue;
        } else {

            if (msgLen == -1) {
            fprintf(stderr, "recvfrom()\n");
            return EXIT_FAILURE;
            }

            HandleConnection(currentPort);

        }
    }

    close(udp);
    return EXIT_SUCCESS;
}
