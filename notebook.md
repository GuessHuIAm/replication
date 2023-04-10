# Engineering Notebook #

## Replication Paradigm ##
For simplicity and robustness, we chose to implement a **Primary-Secondary** Replication Paradigm. This consists of utilizing three multiprocessing `Process`es, acting as three, fully functioning synchronized servers, where each process is given an index (0, 1, or 2). By default, process 0 is designated the initial primary replica (i.e., the server to which clients communicate directly), then the course

## Leader Election ##
Leader election is done in a round-robin format, where clients check down the

## Persistence ##
We chose to persist our chat application using a MySQL server. We chose to use MySQL over SQLite or simply serializing all of the vital

## Other Improvements Over Original ##
We decided to augment our original gRPC implementation, and some additional improvements include comprehensive validation of inputs such as usernames, IP addresses, and regular expressions; enhanced error handling so that user error does not result in  application crashing in tandem to a noisy, verbose error message.

## Code Organization ##
- Constants

    For enhanced modularity and customizability, we stored vital constants in the `constants.py` file, containing constants such as the host and ports of each of the replicas as well as a set of illegal characters that user input is validated against to prevent injection attacks with SQL commands,

## Testing ##
- Unit Testing

- Integration Testing
Manual testing of primary replica failure was done by programmatically terminating primary and