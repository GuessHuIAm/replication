# Engineering Notebook #

## Replication Paradigm ##
For simplicity and robustness, we chose to implement a Primary-Secondary Replication Paradigm. This consists of utilizing three `multiprocessing` `Process`es, acting as three, fully functioning synchronized servers, where each process is assigned an index (0, 1, or 2). By default, process 0 is designated the initial primary replica (i.e., the server to which clients communicate directly).

- Synchronization

Synchronization between primary and secondary replicas is done in the following manner: Each action dependent on persistence (account creation, message delivery, account deletion, listing accounts) is first relayed by the primary replica to each of its secondary replicas (all replicas with a higher index than it), the secondary replicas perform those actions and update their databases, and then the primary performs the action itself.

## Leader Election ##
Leader election is done in order of lowest index. I.e., the lowest-indexed replica available is chosen to be the primary, and both the client and secondary replicas maintain a continuous heartbeat with the primary replica, transitioning to the next replica in line in the event that a response is not detected from the primary.

Secondary replicas maintain a consistent heartbeat with the primary by using the `Heartbeat` rpc, which simply involves the transfer of a `NoParam` message between both replicas to signify successful interprocess communication. Once secondary replicas fail to receive a `NoParam` message response from the primary replica, each secondary replica moves on to declaring the next available replica (lowest-indexed process that returns a heartbeat check) as the primary. The failure to receive a `NoParam` message response from a primary replica that has failed is done by catching an `grpc._channel._InactiveRpcError`.

The client maintains a continuous heartbeat with the primary server through the `ListenMessages` rpc, which continuously yields messages to the client. When the client detects a `grpc._channel._MultiThreadedRendezvous` exception, we know that the current primary replica is down, so a new primary replica is chosen through the identical process to the heartbeat mechanism implemented by the secondary replicas. That is, it selects the next available replica (lowest-indexed; availabity ensured through a `Heartbeat` ping) as the replica it will now begin communicating with.

## Persistence ##
We chose to persist our chat application using a MySQL server. We chose to use three individual SQLite databases over MySQL or simply serializing all pertinent data structures into JSON format. We did not use MySQL because although MySQL inherently is compatible with multiple machines, solely having one MySQL server would result in one point of failure, rather making our application 2-fault tolerant. We chose not to use a JSON file because instead of having to rewrite the entire JSON file every time information needed to be persisted, SQLite allows for incremental updates and is overall more robust.

## Other Improvements Over Original ##
We decided to augment our original gRPC implementation, and some additional improvements include comprehensive validation of inputs such as usernames, IP addresses, and regular expressions; enhanced error handling so that user error does not result in the application crashing in tandem with a noisy, verbose error message in the terminal.

## Code Organization ##
- Constants

    For enhanced modularity and customizability, we stored vital constants in the `constants.py` file, containing constants such as the host and ports of each of the replicas as well as a set of illegal characters that user input is validated against to prevent injection attacks with SQL commands as well as interfering with regular expression matching functionality.

## Testing ##
- Unit Testing

We performed a number of unit tests on our suite of input validation functions, namely, `validate_input`, `validate_ip`, `validate_user`, and `validate_regex`. We noted that it is rather difficult to perform unit tests on the majority of our program, so much of our testing depended on manually terminating our replicas/processes and see how they react (more details in the following section on Integration Testing).

- Integration Testing

Manual testing of primary replica failure was done by programmatically terminating replicas by using the `Process.terminate()` and demonstrating that no gap in functionality occurred on the client's end, given that one replica was still functional. An additional test proving synchronization of data was done by creating new accounts when Replica 0 had already failed and Replica 1 became primary, then terminating Replica 1 (thus rendering Replica 2 the new primary), and ensuring that the accounts made previously were still recognized as registered, not new, users.

Furthermore, we ran test workflows for each use case dependent on persistence (account creation, message delivery, account deletion, listing accounts) to verify that the appropriate table was being updated in the SQL database, as well as that the correct contents were being read and/or written from it.