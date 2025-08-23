import json
import csv
import datetime
from heapq import heappop, heappush
from collections import defaultdict
from math import radians, cos, sin, asin, sqrt, exp
from random import random

# Calculate the straight line distance (Euclidean) between two points
# Assumes no curvature of the earth for simplicity
def euclidean_distance(lon1, lat1, lon2, lat2):
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    return sqrt(dlon*dlon + dlat*dlat)

# Unit conversion for simplicity
def convert_date(time_obj):
    return (time_obj.year * 8760 + time_obj.month * 730 + 
            24 * time_obj.day + time_obj.hour + time_obj.minute / 60)

# Uses binary search to find the closest node to a given position
def find_closest_node(pos, node_dict):
    min_distance = float('inf')
    min_node_lon, min_node_lat, min_node_key = 0, 0, -1
    
    # Find approximate position
    left, right = 0, len(node_dict) - 1
    while left < right:
        middle = (left + right) // 2
        if float(pos[1]) > node_dict[middle][0]:
            left = middle + 1
        elif float(pos[1]) < node_dict[middle][0]:
            right = middle - 1
        else:
            left = right = middle
    
    # Create search window around found position
    start_idx = max(0, left - 20)
    end_idx = min(len(node_dict), right + 21)
    sample_nodes = node_dict[start_idx:end_idx]
    
    # Find closest node in the window
    for node in sample_nodes:
        current_distance = euclidean_distance(
            float(node[0]), float(node[1]), float(pos[1]), float(pos[0])
        )
        if current_distance < min_distance:
            min_node_lon, min_node_lat, min_node_key = node[0], node[1], node[2]
            min_distance = current_distance
            
    return min_node_lon, min_node_lat, min_node_key


class Passenger:
    def __init__(self, arrival_time, start_pos, end_pos, nodes, counter):
        self.arrival_time = arrival_time
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.num = counter
        
        # Find closest nodes to start and end positions
        (self.start_closest_node_lon, self.start_closest_node_lat, 
         self.start_closest_node_key) = find_closest_node(start_pos, nodes)
        (self.end_closest_node_lon, self.end_closest_node_lat, 
         self.end_closest_node_key) = find_closest_node(end_pos, nodes)


class Driver:
    def __init__(self, avail_time, pos, nodes, counter):
        self.start_time = self.avail_time = avail_time
        self.pos = pos
        self.num = counter
        self.time_driving = 0
        self.passenger = 0
        
        # Find closest node to driver's position
        (self.closest_node_lon, self.closest_node_lat, 
         self.closest_node_key) = find_closest_node(pos, nodes)


class Algorithm:
    def __init__(self):
        self.datetime = datetime.datetime(2014, 4, 25, 0, 0, 0)
        self.time = convert_date(self.datetime)
        self.load_data()
        
        self.total_passengers = len(self.passengers_data)
        self.wait_time = self.driving_for_pickup = 0
        self.driving_passengers = self.total_rides = 0
        self.sorted_nodes = []

    # Use Dijkstra's algorithm for pathfinding
    def dijkstra(self, start, end):
        priority_queue = [(0, start)]

        time = defaultdict(lambda: 10000)
        time[start] = 0
        time[end] = 10000

        while priority_queue:
            current_time, current_node = heappop(priority_queue)

            if current_node == end:
                return time[end]

            for neighbor, connection_data in self.adjacency_edge_dict[current_node].items():
                curr_time = connection_data[0]['time']

                if time[current_node] + curr_time < time[neighbor]:
                    time[neighbor] = time[current_node] + curr_time
                    heappush(priority_queue, (time[neighbor], neighbor))

        return time[end]

    # Load data
    def load_data(self):
        with open('drivers.csv', 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)  # Skip header
            self.drivers_data = list(csv_reader)
            
            for driver in self.drivers_data:
                driver[0] = convert_date(
                    self.datetime.strptime(str(driver[0]), '%m/%d/%Y %H:%M:%S')
                )

        with open('passengers.csv', 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)  # Skip header
            self.passengers_data = list(csv_reader)
            self.passengers_data = self.passengers_data[:40]  # Limit for testing

            for passenger in self.passengers_data:
                passenger[0] = convert_date(
                    self.datetime.strptime(str(passenger[0]), '%m/%d/%Y %H:%M:%S')
                )

        # Load graph data
        with open('adjacency.json', 'r') as file:
            self.adjacency_edge_dict = json.load(file) 
        with open('node_data.json', 'r') as file:
            self.node_file = json.load(file)

    # Preprocess nodes for spatial searching - sorted in increasing longitude order 
    def preprocess_nodes(self):
        all_nodes = []
        for key, data in self.node_file.items():
            all_nodes.append((data['lon'], data['lat'], key))
        all_nodes.sort(key=lambda x: x[0])  # Sort by longitude
        self.sorted_nodes = all_nodes

    # Find the driver-passenger pair with min travel time
    def calculate_min_time(self, drivers, passengers):
        min_time = float('inf')
        min_driver = min_passenger = None
        
        for d_index, driver in enumerate(drivers):
            for p_index, passenger in enumerate(passengers):
                curr_time = self.dijkstra(driver.closest_node_key, passenger.start_closest_node_key)
                if curr_time < min_time:
                    min_driver, min_passenger, min_time = d_index, p_index, curr_time
                    
        return min_driver, min_passenger, min_time

    # Determine if the driver continues driving based on how long they have been driving
    def continue_driving(self, duration):
        decay = 0.5
        probability = exp(-decay * duration)
        return round(probability * 100, 2), random() < probability

    # Just like T4, but with Haversine Distance instead of Euclidean
    def T3(self):
        matched_pairs = []
        self.ready_drivers = []
        self.ready_passengers = []
        self.busy_drivers = []
        
        driver_counter = passenger_counter = 0
        total_done_counter = total_picked_up = 0
        
        # Reset metrics
        self.wait_time = self.driving_for_pickup = 0
        self.driving_passengers = self.total_rides = 0
        
        self.preprocess_nodes()
        
        # Main simulation loop
        while (self.drivers_data or self.ready_drivers or self.busy_drivers) and \
              (self.passengers_data or self.ready_passengers):
            
            # Determine current time
            if self.passengers_data:
                self.time = self.passengers_data[0][0]
            elif self.drivers_data:
                self.time = self.drivers_data[0][0]
            else:
                break
                
            # Add arriving passengers
            while self.passengers_data and self.passengers_data[0][0] <= self.time:
                passenger = self.passengers_data.pop(0)
                passenger_counter += 1
                new_passenger = Passenger(
                    passenger[0], (passenger[1], passenger[2]), 
                    (passenger[3], passenger[4]), self.sorted_nodes, passenger_counter
                )
                self.ready_passengers.append(new_passenger)
                
            # Add available drivers
            while self.drivers_data and self.drivers_data[0][0] <= self.time:
                driver = self.drivers_data.pop(0)
                driver_counter += 1
                new_driver = Driver(driver[0], driver[1], self.sorted_nodes, driver_counter)
                self.ready_drivers.append(new_driver)
                
            # Match drivers and passengers using min travel time
            while self.ready_drivers and self.ready_passengers:
                min_driver_index, min_passenger_index, _ = self.calculate_min_time(
                    self.ready_drivers, self.ready_passengers
                )
                driver = self.ready_drivers.pop(min_driver_index)
                passenger = self.ready_passengers.pop(min_passenger_index)
                
                # Calculate travel times using Dijkstra's
                time_to_passenger = self.dijkstra(driver.closest_node_key, passenger.start_closest_node_key)
                travel_time = self.dijkstra(passenger.start_closest_node_key, passenger.end_closest_node_key)
                
                # Update driver status
                driver.passenger = passenger.num
                driver.wait_start = max(passenger.arrival_time, driver.avail_time)
                driver.passenger_arrival = driver.wait_start + time_to_passenger
                driver.passenger_dropoff = driver.passenger_arrival + travel_time
                
                # Update driver position
                driver.closest_node_lon = passenger.end_closest_node_lon
                driver.closest_node_lat = passenger.end_closest_node_lat
                driver.closest_node_key = passenger.end_closest_node_key
                
                # Record match
                matched_pairs.append(f"Driver #{driver.num} took Passenger #{passenger.num}")
                self.busy_drivers.append(driver)
                
                # Log pickup
                print(f"Passenger #{passenger.num} Picked Up at {self.time} by Driver #{driver.num}")
                total_picked_up += 1
                
            # Process completed trips
            for driver in self.busy_drivers[:]:  # Iterate over a copy to allow removal
                if driver.passenger_dropoff <= self.time:
                    self.busy_drivers.remove(driver)
                    total_done_counter += 1
                    
                    # Update metrics
                    passenger_wait = (driver.passenger_arrival - driver.wait_start) * 60
                    trip_duration = (driver.passenger_dropoff - driver.passenger_arrival) * 60
                    self.wait_time += (driver.passenger_dropoff - driver.wait_start) * 60
                    
                    self.driving_for_pickup += (driver.passenger_arrival - driver.wait_start)
                    self.driving_passengers += (driver.passenger_dropoff - driver.passenger_arrival)
                    self.total_rides += 1
                    
                    # Log dropoff
                    print(f"Passenger #{driver.passenger} Dropped Off By Driver #{driver.num} "
                          f"Passenger waited for {passenger_wait:.2f} minutes. "
                          f"Trip took {trip_duration:.2f} minutes. "
                          f"{total_done_counter} passengers have been dropped off")
                    
                    # Determine if driver continues
                    driver.time_driving += (driver.passenger_dropoff - driver.start_time)
                    percent, cont = self.continue_driving(driver.time_driving)
                    
                    if cont:
                        print(f"With probability {percent}%, Driver #{driver.num} back on duty")
                        driver.avail_time = driver.passenger_dropoff
                        self.ready_drivers.append(driver)
                    else:
                        print(f"With probability {100 - percent}%, Driver #{driver.num} off duty")
                        
        # Print final metrics
        avg_wait = self.wait_time / self.total_passengers if self.total_passengers > 0 else 0
        avg_profit = (self.driving_passengers - self.driving_for_pickup) / self.total_rides if self.total_rides > 0 else 0
        
        print(f"Average wait time was {avg_wait:.2f} minutes")
        print(f"Average ride profit was {avg_profit:.2f} minutes")
        
        return matched_pairs


# Run the simulation
if __name__ == "__main__":
    algo = Algorithm()
    algo.T3()
