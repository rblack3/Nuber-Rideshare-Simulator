# Incorporate Haversine dist. for accuracy

import json, csv, datetime
from heapq import heappop, heappush
from collections import defaultdict
from math import inf, radians, cos, sin, asin, sqrt, exp
from random import randint, random

class Passenger:
	def __init__(self, arrival_time, start_pos, end_pos, nodes, counter):
		self.arrival_time = arrival_time
		self.start_pos = start_pos
		self.end_pos = end_pos
		self.node_dict = nodes
		self.num = counter
		self.start_closest_node_lon, self.start_closest_node_lat, self.start_closest_node_key = self.find_closest_node(start_pos)
		self.end_closest_node_lon, self.end_closest_node_lat, self.end_closest_node_key = self.find_closest_node(end_pos)

	def haversine(self, lon1, lat1, lon2, lat2):
		lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

		dlon = lon2 - lon1
		dlat = lat2 - lat1
		a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2

		return 6371 * (2 * asin(sqrt(a)))

	def euclidean(self, lon1, lat1, lon2, lat2):
		dlon = lon2 - lon1
		dlat = lat2 - lat1
		a = (dlon*dlon) + (dlat*dlat)

		return sqrt(a)

	def find_closest_node(self, pos):
		min_distance = float('inf')
		min_node_lon = 0
		min_node_lat = 0
		min_node_key = -1

		left = 0
		right = len(self.node_dict) - 1
		sample_nodes = []
		while left < right:
			middle = (left + right) // 2
			if float(pos[1]) > self.node_dict[middle][0]:
				left = middle + 1
			elif float(pos[1]) < self.node_dict[middle][0]:
				right = middle - 1
			else:
				left = middle
				right = middle
		if left - 20 >= 0 and right + 20 <= len(self.node_dict):
			sample_nodes = self.node_dict[left-20:right+20]
		elif left - 20 < 0:
			sample_nodes = self.node_dict[0:right+20]
		else:
			sample_nodes = self.node_dict[left-20:len(self.node_dict)]

		for node in sample_nodes:
			current_distance = self.haversine(float(node[0]), float(node[1]), float(pos[1]), float(pos[0]))
			if current_distance < min_distance:
				min_node_lon = node[0]
				min_node_lat = node[1]
				min_node_key = node[2]
				min_distance = current_distance
		return min_node_lon, min_node_lat, min_node_key

class Driver:
	def __init__(self, avail_time, pos, nodes, counter):
		self.start_time = avail_time
		self.avail_time = avail_time
		self.pos = pos
		self.node_dict = nodes
		self.closest_node_lon, self.closest_node_lat, self.closest_node_key = self.find_closest_node(pos)
		self.num = counter
		self.time_driving = 0
		self.passenger = 0

	def haversine(self, lon1, lat1, lon2, lat2):
		lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

		dlon = lon2 - lon1
		dlat = lat2 - lat1
		a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2

		return 6371 * (2 * asin(sqrt(a)))

	def euclidean(self, lon1, lat1, lon2, lat2):
		dlon = lon2 - lon1
		dlat = lat2 - lat1
		a = (dlon*dlon) + (dlat*dlat)

		return sqrt(a)

	def find_closest_node(self, pos):
		min_distance = float('inf')
		min_node_lon = 0
		min_node_lat = 0
		min_node_key = -1

		left = 0
		right = len(self.node_dict) - 1
		sample_nodes = []
		while left < right:
			middle = (left + right) // 2
			if float(pos[1]) > self.node_dict[middle][0]:
				left = middle + 1
			elif float(pos[1]) < self.node_dict[middle][0]:
				right = middle - 1
			else:
				left = middle
				right = middle
		if left - 20 >= 0 and right + 20 <= len(self.node_dict):
			sample_nodes = self.node_dict[left-20:right+20]
		elif left - 20 < 0:
			sample_nodes = self.node_dict[0:right+20]
		else:
			sample_nodes = self.node_dict[left-20:len(self.node_dict)]
		for node in sample_nodes:
			current_distance = self.haversine(float(node[0]), float(node[1]), float(pos[1]), float(pos[0]))
			if current_distance < min_distance:
				min_node_lon = node[0]
				min_node_lat = node[1]
				min_node_key = node[2]
				min_distance = current_distance
		return min_node_lon, min_node_lat, min_node_key

class Algorithm:
	def __init__(self):
		self.datetime = datetime.datetime(2014, 4, 25, 0,0,0)
		self.time = self.convertDate(self.datetime)
		self.load_data()

		self.total_passengers = len(self.passengers_data)
		self.wait_time = 0
		self.driving_for_pickup = 0
		self.driving_passengers = 0
		self.total_rides = 0
		self.sorted_nodes = []

	def haversine(self, lon1, lat1, lon2, lat2):
		lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

		dlon = lon2 - lon1
		dlat = lat2 - lat1
		a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2

		return 6371 * (2 * asin(sqrt(a)))

	def euclidean(self, lon1, lat1, lon2, lat2):
		dlon = lon2 - lon1
		dlat = lat2 - lat1
		a = (dlon*dlon) + (dlat*dlat)

		return sqrt(a)

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

	def A_star(self, start, end):
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
					heappush(priority_queue, (time[neighbor] + self.euclidean(float(self.node_file[current_node]['lon']), float(self.node_file[current_node]['lat']), float(self.node_file[end]['lon']), float(self.node_file[end]['lat'])), neighbor))

		return time[end]

	def convertDate(self, time):
		return time.year * 8760 + time.month * 730 + 24 * time.day + time.hour + (time.minute / 60)

	def load_data(self):
		with open('drivers.csv', 'r') as csv_file:

			csv_reader = csv.reader(csv_file)
			next(csv_reader)
			self.drivers_data = list(csv_reader)

			for driver in self.drivers_data:
				driver[0] = self.convertDate(self.datetime.strptime(str(driver[0]),'%m/%d/%Y %H:%M:%S'))

		with open('passengers.csv', 'r') as csv_file:

			csv_reader = csv.reader(csv_file)
			next(csv_reader)

			self.passengers_data = list(csv_reader)
			self.passengers_data = self.passengers_data[0:40]   #### Keep this line in to run test with less passengers

			for count, passenger in enumerate(self.passengers_data):
				passenger[0] = self.convertDate(self.datetime.strptime(str(passenger[0]),'%m/%d/%Y %H:%M:%S'))

		# Keys are strings, not integers
		with open('adjacency.json', 'r') as file:
			self.adjacency_edge_dict = json.load(file)

		with open('node_data.json', 'r') as file:
			self.node_file = json.load(file)

	def preprocess_nodes(self):
			all_nodes = []
			for key in self.node_file.keys():
					all_nodes.append((self.node_file[key]['lon'], self.node_file[key]['lat'], key))
			all_nodes.sort(key=lambda x: x[0])
			self.sorted_nodes = all_nodes

	def calculate_min_pair(self, drivers, passengers):
		min_distance = float('inf')
		min_driver = None
		min_passenger = None

		for d_index, driver in enumerate(drivers):
			for p_index, passenger in enumerate(passengers):
				current_distance = self.haversine(float(self.node_file[driver.closest_node_key]['lat']), float(self.node_file[driver.closest_node_key]['lon']), float(self.node_file[passenger.start_closest_node_key]['lat']), float(self.node_file[passenger.start_closest_node_key]['lon']))
				if current_distance < min_distance:
					min_driver = d_index
					min_passenger = p_index
					min_distance = current_distance
		return min_driver, min_passenger, min_distance

	def calculate_min_time(self, drivers, passengers):
		min_time = float('inf')
		min_driver = None
		min_passenger = None

		for d_index, driver in enumerate(drivers):
			for p_index, passenger in enumerate(passengers):
				curr_time = self.A_star(driver.closest_node_key, passenger.start_closest_node_key)
				if curr_time < min_time:
					min_driver = d_index
					min_passenger = p_index
					min_time = curr_time
		return min_driver, min_passenger, min_time

	def continue_driving(self, duration):
		decay = 0.5
		probability = exp(-decay * duration)
		return round(probability *100, 2), random() < probability

	def T1(self):
			matched_pairs = []

			self.ready_drivers = []
			self.ready_passengers = []
			self.busy_drivers = []
			self.finished_passengers = []

			driver_counter = 0
			passenger_counter = 0
			total_done_counter = 0
			total_picked_up = 0

			self.drivers_data
			self.passengers_data

			self.preprocess_nodes()

			while (len(self.drivers_data) > 0 or len(self.ready_drivers) > 0 or len(self.busy_drivers) > 0) and (len(self.passengers_data) > 0 or len(self.ready_passengers) > 0 or len(self.busy_drivers) > 0):
				if len(self.passengers_data) > 0:
					self.time = self.passengers_data[0][0]
				else:
					self.time = self.drivers_data[0][0]

				if len(self.passengers_data) > 0 and self.passengers_data[0][0] <= self.time:

					passenger = self.passengers_data.pop(0)
					passenger_counter += 1

					new_passenger = Passenger(passenger[0], (passenger[1], passenger[2]), (passenger[3], passenger[4]), self.sorted_nodes, passenger_counter)
					self.ready_passengers.append(new_passenger)

				while self.drivers_data[0][0] <= self.time:

					driver = self.drivers_data.pop(0)
					driver_counter += 1
					new_driver = Driver(driver[0], driver[1], self.sorted_nodes, driver_counter)

					self.ready_drivers.append(new_driver)

				while len(self.ready_drivers) > 0 and len(self.ready_passengers) > 0:
					driver = self.ready_drivers.pop(0)
					passenger = self.ready_passengers.pop(0)

					time_to_passenger = self.dijkstra(driver.closest_node_key, passenger.start_closest_node_key)
					travel_time = self.dijkstra(passenger.start_closest_node_key, passenger.end_closest_node_key)

					driver.passenger = passenger.num

					print("Passenger #"+ str(passenger.num) + " Picked Up at " + str(self.time) + " by Driver #" + str(driver.num))
					total_picked_up += 1
					driver.wait_start = max(passenger.arrival_time, driver.avail_time)

					driver.passenger_arrival = driver.wait_start + time_to_passenger
					driver.passenger_dropoff = driver.passenger_arrival + travel_time

					driver.closest_node_lon = passenger.end_closest_node_lon
					driver.closest_node_lat = passenger.end_closest_node_lat
					driver.closest_node_key = passenger.end_closest_node_key

					matched_pairs.append(("Driver #" + str(driver.num) + " took Passenger #" + str(passenger.num)))
					del passenger

					self.busy_drivers.append(driver)

				for driver in self.busy_drivers:
					if driver.passenger_dropoff <= self.time:
						self.busy_drivers.remove(driver)
						total_done_counter += 1

						self.wait_time += (driver.passenger_dropoff - driver.wait_start) * 60
						print("Passenger #" + str(driver.passenger) + " Dropped Off By Driver #" + str(driver.num) + "    Passenger waited for " + str((driver.passenger_arrival - driver.wait_start) *60)+ " minutes. Trip took " + str((driver.passenger_dropoff - driver.passenger_arrival)*60) + " minutes. " + str(total_done_counter) + " passengers have been dropped off")

						self.driving_for_pickup += (driver.passenger_arrival - driver.wait_start)
						self.driving_passengers += (driver.passenger_dropoff - driver.passenger_arrival)
						self.total_rides += 1

						driver.time_driving += (driver.passenger_dropoff - driver.start_time)
						percent, cont = self.continue_driving(driver.time_driving)

						if cont:
							print("With probability " + str(percent) + "%, Driver #" + str(driver.num) + " back on duty")
							driver.avail_time = driver.passenger_dropoff
							self.ready_drivers.append(driver)
						else:
							print("With probability " + str(100 - percent) + "%, Driver #" + str(driver.num) + " off duty")
							del driver

			print("Average wait time was " + str(self.wait_time / self.total_passengers) + " minutes")
			print("Average ride profit was " + str((self.driving_passengers - self.driving_for_pickup)/self.total_rides) + " minutes")

			return matched_pairs

	def T2(self):
		matched_pairs = []

		self.ready_drivers = []
		self.ready_passengers = []
		self.busy_drivers = []
		self.finished_passengers = []

		driver_counter = 0
		passenger_counter = 0
		total_done_counter = 0
		total_picked_up = 0

		self.drivers_data
		self.passengers_data
		print(len(self.passengers_data), len(self.drivers_data))

		self.preprocess_nodes()

		while (len(self.drivers_data) > 0 or len(self.ready_drivers) > 0 or len(self.busy_drivers) > 0) and (len(self.passengers_data) > 0 or len(self.ready_passengers) > 0 or len(self.busy_drivers) > 0):
			if len(self.passengers_data) == 0 and len(self.ready_passengers) == 0 and len(self.busy_drivers) == 0:
				break

			if len(self.passengers_data) > 0:
				self.time = self.passengers_data[0][0]
			else:
				self.time = self.drivers_data[0][0]

			if len(self.passengers_data) > 0 and self.passengers_data[0][0] <= self.time:

				passenger = self.passengers_data.pop(0)
				passenger_counter += 1

				new_passenger = Passenger(passenger[0], (passenger[1], passenger[2]), (passenger[3], passenger[4]), self.sorted_nodes, passenger_counter)
				self.ready_passengers.append(new_passenger)

			while self.drivers_data[0][0] <= self.time:

				driver = self.drivers_data.pop(0)
				driver_counter += 1
				new_driver = Driver(driver[0], driver[1], self.sorted_nodes, driver_counter)

				self.ready_drivers.append(new_driver)

			while len(self.ready_drivers) > 0 and len(self.ready_passengers) > 0:
				min_driver_index, min_passenger_index, _ = self.calculate_min_pair(self.ready_drivers, self.ready_passengers)

				driver = self.ready_drivers.pop(min_driver_index)
				passenger = self.ready_passengers.pop(min_passenger_index)

				time_to_passenger = self.dijkstra(driver.closest_node_key, passenger.start_closest_node_key)
				travel_time = self.dijkstra(passenger.start_closest_node_key, passenger.end_closest_node_key)

				driver.passenger = passenger.num

				print("Passenger #"+ str(passenger.num) + " Picked Up at " + str(self.time) + " by Driver #" + str(driver.num))
				total_picked_up += 1
				driver.wait_start = max(passenger.arrival_time, driver.avail_time)

				driver.passenger_arrival = driver.wait_start + time_to_passenger
				driver.passenger_dropoff = driver.passenger_arrival + travel_time

				driver.closest_node_lon = passenger.end_closest_node_lon
				driver.closest_node_lat = passenger.end_closest_node_lat
				driver.closest_node_key = passenger.end_closest_node_key

				matched_pairs.append(("Driver #" + str(driver.num) + " took Passenger #" + str(passenger.num)))
				del passenger

				self.busy_drivers.append(driver)

			for driver in self.busy_drivers:
				if driver.passenger_dropoff <= self.time:
					self.busy_drivers.remove(driver)
					total_done_counter += 1

					self.wait_time += (driver.passenger_dropoff - driver.wait_start) * 60
					print("Passenger #" + str(driver.passenger) + " Dropped Off By Driver #" + str(driver.num) + "    Passenger waited for " + str((driver.passenger_arrival - driver.wait_start) *60)+ " minutes. Trip took " + str((driver.passenger_dropoff - driver.passenger_arrival)*60) + " minutes. " + str(total_done_counter) + " passengers have been dropped off")

					self.driving_for_pickup += (driver.passenger_arrival - driver.wait_start)
					self.driving_passengers += (driver.passenger_dropoff - driver.passenger_arrival)
					self.total_rides += 1

					driver.time_driving += (driver.passenger_dropoff - driver.start_time)
					percent, cont = self.continue_driving(driver.time_driving)

					if cont:
						print("With probability " + str(percent) + "%, Driver #" + str(driver.num) + " back on duty")
						driver.avail_time = driver.passenger_dropoff
						self.ready_drivers.append(driver)
					else:
						print("With probability " + str(100 - percent) + "%, Driver #" + str(driver.num) + " off duty")
						del driver

		print("Average wait time was " + str(self.wait_time / self.total_passengers) + " minutes")
		print("Average ride profit was " + str((self.driving_passengers - self.driving_for_pickup)/self.total_rides) + " minutes")
		return matched_pairs

	def T3(self):
		matched_pairs = []

		self.ready_drivers = []
		self.ready_passengers = []
		self.busy_drivers = []
		self.finished_passengers = []

		driver_counter = 0
		passenger_counter = 0
		total_done_counter = 0
		total_picked_up = 0

		self.drivers_data
		self.passengers_data
		print(len(self.passengers_data), len(self.drivers_data))

		self.preprocess_nodes()

		while (len(self.drivers_data) > 0 or len(self.ready_drivers) > 0 or len(self.busy_drivers) > 0) and (len(self.passengers_data) > 0 or len(self.ready_passengers) > 0 or len(self.busy_drivers) > 0):
			if len(self.passengers_data) == 0 and len(self.ready_passengers) == 0 and len(self.busy_drivers) == 0:
				break

			if len(self.passengers_data) > 0:
				self.time = self.passengers_data[0][0]
			else:
				self.time = self.drivers_data[0][0]

			if len(self.passengers_data) > 0 and self.passengers_data[0][0] <= self.time:

				passenger = self.passengers_data.pop(0)
				passenger_counter += 1

				new_passenger = Passenger(passenger[0], (passenger[1], passenger[2]), (passenger[3], passenger[4]), self.sorted_nodes, passenger_counter)
				self.ready_passengers.append(new_passenger)

			while self.drivers_data[0][0] <= self.time:

				driver = self.drivers_data.pop(0)
				driver_counter += 1
				new_driver = Driver(driver[0], driver[1], self.sorted_nodes, driver_counter)

				self.ready_drivers.append(new_driver)

			while len(self.ready_drivers) > 0 and len(self.ready_passengers) > 0:
				min_driver_index, min_passenger_index, _ = self.calculate_min_time(self.ready_drivers, self.ready_passengers)

				driver = self.ready_drivers.pop(min_driver_index)
				passenger = self.ready_passengers.pop(min_passenger_index)

				time_to_passenger = self.A_star(driver.closest_node_key, passenger.start_closest_node_key)
				travel_time = self.A_star(passenger.start_closest_node_key, passenger.end_closest_node_key)

				driver.passenger = passenger.num

				print("Passenger #"+ str(passenger.num) + " Picked Up at " + str(self.time) + " by Driver #" + str(driver.num))
				total_picked_up += 1
				driver.wait_start = max(passenger.arrival_time, driver.avail_time)

				driver.passenger_arrival = driver.wait_start + time_to_passenger
				driver.passenger_dropoff = driver.passenger_arrival + travel_time

				driver.closest_node_lon = passenger.end_closest_node_lon
				driver.closest_node_lat = passenger.end_closest_node_lat
				driver.closest_node_key = passenger.end_closest_node_key

				matched_pairs.append(("Driver #" + str(driver.num) + " took Passenger #" + str(passenger.num)))
				del passenger

				self.busy_drivers.append(driver)

			for driver in self.busy_drivers:
				if driver.passenger_dropoff <= self.time:
					self.busy_drivers.remove(driver)
					total_done_counter += 1

					self.wait_time += (driver.passenger_dropoff - driver.wait_start) * 60
					print("Passenger #" + str(driver.passenger) + " Dropped Off By Driver #" + str(driver.num) + "    Passenger waited for " + str((driver.passenger_arrival - driver.wait_start) *60)+ " minutes. Trip took " + str((driver.passenger_dropoff - driver.passenger_arrival)*60) + " minutes. " + str(total_done_counter) + " passengers have been dropped off")

					self.driving_for_pickup += (driver.passenger_arrival - driver.wait_start)
					self.driving_passengers += (driver.passenger_dropoff - driver.passenger_arrival)
					self.total_rides += 1

					driver.time_driving += (driver.passenger_dropoff - driver.start_time)
					percent, cont = self.continue_driving(driver.time_driving)

					if cont:
						print("With probability " + str(percent) + "%, Driver #" + str(driver.num) + " back on duty")
						driver.avail_time = driver.passenger_dropoff
						self.ready_drivers.append(driver)
					else:
						print("With probability " + str(100 - percent) + "%, Driver #" + str(driver.num) + " off duty")
						del driver

		print("Average wait time was " + str(self.wait_time / self.total_passengers) + " minutes")
		print("Average ride profit was " + str((self.driving_passengers - self.driving_for_pickup)/self.total_rides) + " minutes")
		return matched_pairs


algo = Algorithm()
#algo.T1()
#algo.T2()
algo.T3()