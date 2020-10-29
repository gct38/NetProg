Network Programming Homework 1 README


Team Members:
Gordon Tsang 
Sappy Ganguly
Joseph Gonzales
Dani Reil

-------------------------------------------------------------------------------------------------------------------------------------------------

Files Submitted:
HW1.c - main code for the TFTP server.
Makefile - compiles necessary files and creates an out file to run.
README.txt 

-------------------------------------------------------------------------------------------------------------------------------------------------

Program:
The purpose of this program is a Trivial File Transfer Protocol (TFTP) server in accordance with RFC1350 standards written in C.
This TFTP server only supports octect mode. There is no support for the mail or netascii modes.

The program takes 2 arguments, the start port and the end port. The start port is where the server is listening for clients 
and for every transfer, the transfer id (TID) will use its own port. The TID port will start off one greater than the server port. 
Once we reach a TID port that is greater than the given end port argument, the server will close.
For every transfer that occurs, the port will increase by 1 each time. Each transfer that happens will be forked into its own process.
The server will handle the request from the client and either return a DATA, ACK, or ERROR packet accordingly. 
If the server sends out a packet and does not receive any data back within 1 second, it will resend the same packet packet out 
again. Regardless of how many packets it sends out, once the server receives some data back with the same block, then the server
will continue sending out packets. This is in accordance with RFC1350 standards where we work around the Sorcerer's Apprentice Syndrome.

After 10 seconds of inactivity from the client, the server will close the port and exit the program.

-------------------------------------------------------------------------------------------------------------------------------------------------

Issues Encountered:
We ran into an issue where we were struggling to build the packet at first. After playing around with building the packet and using WireShark
to check on the packets, we were able to successfully build the packets.

We also ran into an issue when we had to resend the packet because we didn't receive an ACK packet in time where it wouldn't resend the packet.
This caused our transferred files to be cut off halfway through. We adjusted the code to ensure that we were actually resending the packet
if our 1 second alarm was timing out. 

-------------------------------------------------------------------------------------------------------------------------------------------------

Approximate Time Spent on the Homework: ~15hours

-------------------------------------------------------------------------------------------------------------------------------------------------

Breakdown of Work:
Gordon Tsang - development of packet creation and handling
Sapyp Ganguly - development of handling the connection
Joseph Gonzales - development of alarms and handling of them
Dani Reil - development of packet creation and handling
