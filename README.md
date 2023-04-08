# Replication: Chat Application
Created by Michael Hu, Jonathan Luo and Matt Kiley.

## Description

A chat system that is both persistent (it can be stopped and re-started without losing messages that were sent during the time it was running) and 2-fault tolerant in the face of crash/failstop failures.

The replication can be done in multiple processes on the same machine, but it also works over multiple machines.

We also included an engineering notebook that details the design and implementation decisions that you make while implementing the system. 

## Usage
### Requirements
To make sure you have all the required modules for this application, run `pip install -r requirements.txt` before continuing!
### Server
To get started, one machine needs to start the server by running `python server.py` once they are in this directory. They must make sure this server remains active for clients to connect.
### Client
Then, other machines can connect to the server by running `python client.py`. The client server will prompt the user to enter the IP address of the server machine. To find the IP address of a Mac, go to <span style="color:#528AAE">System Settings > Wi-Fi > [Your Network] > Details > TCP/IP</span>. To find the IP address of a Windows machine, go to <span style="color:#528AAE">Start > Settings > Network & Internet > Wi-Fi > Properties > IPv4 </span>. Once the client is successfully connected to the server, our application is now up and running--enjoy chatting!
