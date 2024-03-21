### Introduction
Welcome to the Nüber! In this company, we operate a ride-sharing service in New York City, where 
passengers request rides through a mobile app, and drivers sign into the app whenever they're available to drive.

So far NU has been subcontracting to another taxi dispatcher to make real-time assignments of
drivers to passengers. This project designs the next generation algorithmic system for automating these decisions.

### Problem Formulation
All trips will take place on a road network, modeled as a weighted undirected graph where edges
represent road segments. Pickup and drop-off coordinates may not be vertices of the graph and may
not even be on the road network, in which case trips should be from the closest network vertices
to these locations.

### Event-Driven Decisions
A matching algorithm can make a decision whenever an event happens, at which point it can either
wait (do nothing) or assign an unmatched driver to an unmatched passenger. Once a driver is
matched to a passenger, the driver travels to the passenger pickup location and then to their drop-off location. 
The events that can change the state of the world and result in a match opportunity for the algorithm include:
• New unmatched passengers may appear (along with a pickup and desired drop-off location).
• New unmatched drivers may appear, along with a current location, in two ways.
• A brand new driver may appear at an arbitrary location,
• Or, a matched driver with passenger may arrive at the drop-off location. The passenger
then exits. With some probability, the driver may also exit and no event takes place.
•Otherwise, the driver becomes a new unmatched driver at their current location (note
this was the drop-off location of the passenger who just exited).
• Imagine that most drivers will typically want to finish several rides over a period of a
few hours before exiting.

### Desiderata
The algorithm will balance three fundamental desiderata (desirable properties) listed
below as D1-D3.
• D1. Passengers want to be dropped off as soon as possible, that is, to minimize the amount
of time (in minutes) between when they appear as an unmatched passenger, and when they
are dropped off at their destination.
• D2. Drivers want to maximize ride profit, defined as the number of minutes they spend
driving passengers from pickup to drop-off locations minus the number of minutes they spend
driving to pickup passengers. For simplicity, there is no penalty for the time when a driver is
idle.
• D3. The algorithm will be empirically efficient and scalable.

### Constraints
The algorithm will also optimize the algorithm with the following constraints C1-C3.
• C1. A driver can only have one passenger onboard at any given time.
• C2. Passengers can only be picked up or dropped off at their requested pickup and drop-off
locations.
• C3. Once you assign a driver to a passenger, that match continues until the passenger is
dropped off at their correct location - matches made by your algorithm cannot be canceled.

### Algorithm Design and Implementation Tasks
The app uses a dataset representing the NYC road network as a graph in an adjacency
list format. In addition to vertex coordinates, neighbors, and edge lengths, the dataset includes
information about the average speed along each road segment, which varies. Speed estimates are
included for different hours of the day on both weekdays and weekends.
We also have a dataset with the location of drivers logging on at different times and passengers,
along with their pickup and drop-off locations, requesting rides at different times. Both are sorted by
increasing order of date-time.

### Steps
The project was done in 5 steps, T1 through T5, each with increasingly complexity.

### T1
A very simple baseline that just keeps track of queues of available
drivers and unmatched passengers and assigns the longest waiting passenger to the first
available driver, whenever possible. 

### T2
A slightly improved baseline that, whenever there is a choice,
schedules the driver-passenger pair with minimum straight-line distance between the driver
and pickup location of the passenger. 

### T3
A further improvement that, whenever there is a choice, schedules
the driver-passenger pair with minimum estimated time for the driver 
to traverse the network to the passenger pickup location. 

### T4
Further improved runtime efficiency while maintaining the same general scheduling strategy as in T3. 
This was done using two optimizations:
(i) Preprocessed the nodes of the road network to efficiently
find the closest (in terms of straight-line distance) node to a given query point (at least
approximately). 
(ii) Computed shortest paths between two nodes of the road network using an A* heuristic,
which is more efficient than Dijkstra's, which was used in T1-T3.
