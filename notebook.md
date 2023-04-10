# Engineering Notebook #

## Replication Paradigm ##
For simplicity and robustness, we chose to implement a **Primary-Secondary** Replication Paradigm. This consists of utilizing three multiprocessing `Process`es, acting as three, fully functioning synchronized servers, where each process is given an index (0, 1, or 2). By default, process 0 is designated the initial primary replica (i.e., the server to which clients communicate directly).

## Leader Election ##
Leader election is done in order of lowest index. I.e., the lowest-indexed replica available is chosen to be the primary, and both the client and secondary replicas maintain a continuous heartbeat with the primary replica, transitioning to the next replica in line in the event that a response is not detected from the primary.

Secondary replicas maintain a consistent heartbeat with the primary 

The client maintains a continuous heartbeat with the primary server through the `ListenMessages` rpc, which continuously yields messages to the client. When the client detects a `grpc._channel._MultiThreadedRendezvous` exception, we know that the current primary replica is down, so a new primary replica is done through the following process: 

## Persistence ##
We chose to persist our chat application using a MySQL server. We chose to use MySQL over SQLite or simply serializing all of the vital

## Other Improvements Over Original ##
We decided to augment our original gRPC implementation, and some additional improvements include comprehensive validation of inputs such as usernames, IP addresses, and regular expressions; enhanced error handling so that user error does not result in the application crashing in tandem with a noisy, verbose error message in the terminal.

## Code Organization ##
- Constants

    For enhanced modularity and customizability, we stored vital constants in the `constants.py` file, containing constants such as the host and ports of each of the replicas as well as a set of illegal characters that user input is validated against to prevent injection attacks with SQL commands,

## Testing ##
- Unit Testing

- Integration Testing
Manual testing of primary replica failure was done by programmatically terminating replicas by using the `Process.terminate()`