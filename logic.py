import random
import math
import json
import csv
import logging


def calculate_euclidean_distance(a: list, b: list):
    logging.debug(f"calculate_euclidean_distance function called with parameters a = {a}, b = {b}")
    distance = 0
    if len(a) != len(b):
        print("Nierówna długość list")
        return
    for i in range(len(a)):
        distance += math.pow(a[i] - b[i], 2)
    distance = math.sqrt(distance)
    logging.debug(f"calculate_euclidean_distance function returns {distance}")
    return distance


class Simulation:
    def __init__(self, turns_amount: int, sheep_amount: int, init_pos_limit: float, sheep_move_dist: float,
                 wolf_move_dist: float, wait: bool, directory: str, log_level: str or int):
        if log_level:
            logging.basicConfig(filename=directory + "chase.log", level=log_level, filemode="w+")
        logging.debug(
            f" Simulation object created with values: turns_amount = {turns_amount}, sheep amount = {sheep_amount}, init_pos_limit = {init_pos_limit}, sheep_move_dist = {sheep_move_dist}, wolf_move_dist = {wolf_move_dist}, wait = {wait}, directory = {directory} ")
        self.turns_amount = turns_amount
        self.sheep_amount = sheep_amount
        self.init_pos_limit = init_pos_limit
        self.sheep_move_dist = sheep_move_dist
        self.wolf_move_dist = wolf_move_dist
        self.wolf = Wolf(wolf_move_dist)
        self.sheep = []
        self.alive_sheep = []
        for i in range(sheep_amount):
            self.add_sheep(i)
        self.dead_sheep = []
        self.turn_number = 0
        self.json_data = []
        self.csv_data = []
        self.wait = wait
        self.directory = directory

    def add_sheep(self, sheep_id, position=None):
        single_sheep = Sheep(self.init_pos_limit, self.sheep_move_dist, sheep_id, position)
        self.sheep.append(single_sheep)
        self.alive_sheep.append(single_sheep)

    def _move_sheep(self):
        logging.debug(" Simulations move_sheep method called")
        for sheep in self.alive_sheep:
            sheep.move()

    def _move_wolf(self):
        logging.debug(" Simulations move_wolf method called")
        self.wolf.move(self.alive_sheep)

    def move_wolf_manual(self, position):
        logging.debug(" Simulations move_wolf manual method called")
        self.wolf.position = position

    def _remove_dead_sheep(self):
        logging.debug(" Simulations remove_dead_sheep method called")
        for sheep in self.alive_sheep:
            if not sheep.is_alive:
                sheep.position = [None, None]
                self.dead_sheep.append(sheep)
                self.alive_sheep.remove(sheep)
                logging.info(f" Sheep {sheep.sheep_index} moved to dead_sheep list")

    def _print_status(self):
        logging.debug(" Simulations print_status method called")
        print("Numer tury: " + str(self.turn_number))
        print(" Pozycja wilka: \n    X: " + format(self.wolf.position[0], ".3f") + "\n    Y: " + format(
            self.wolf.position[1], ".3f"))
        print(" Liczba żywych owiec: " + str(len(self.alive_sheep)))
        if self.wolf.hasEaten:
            print(" Owca nr " + str(self.dead_sheep[-1].sheep_index) + " została pożarta")
        print()

    def _prepare_json(self):
        logging.debug(" Simulations prepare_json method called")
        sheep_coord_list = []
        for sheep in self.sheep:
            sheep_coord_list.append([sheep.position[0], sheep.position[1]])
        dictionary = {
            "round_no": self.turn_number,
            "wolf_pos": [self.wolf.position[0], self.wolf.position[1]],
            "sheep_pos": sheep_coord_list
        }
        self.json_data.append(dictionary)

    def _write_to_json(self):
        logging.debug(" Simulations write_to_json method called")
        with open(self.directory + 'pos.json', 'w+') as output_file:
            json.dump(self.json_data, output_file, indent=4)

    def _prepare_csv(self):
        logging.debug(" Simulations prepare_csv method called")
        self.csv_data.append([self.turn_number, len(self.alive_sheep)])

    def _write_to_csv(self):
        logging.debug(" Simulations write_to_csv method called")
        with open(self.directory + 'alive.csv', 'w+', newline='') as output_file:
            writer = csv.writer(output_file, delimiter=',')
            writer.writerows(self.csv_data)

    def run_simulation(self):
        logging.debug(" Simulations simulate method called")
        while self.turn_number < self.turns_amount and len(self.alive_sheep) != 0:
            self.simulate_turn()
            if self.wait:
                input("Naciśnij Enter aby kontynuować")
        self._write_to_json()
        self._write_to_csv()

    def simulate_turn(self):
        if not self.sheep:
            raise Exception()
        self._move_sheep()
        self._move_wolf()
        if self.wolf.hasEaten:
            self._remove_dead_sheep()
        self._print_status()
        self._prepare_json()
        self._prepare_csv()
        self.turn_number += 1

    def reset(self):
        logging.debug(" Simulations reset method called")
        self.move_wolf_manual([0, 0])
        self.sheep.clear()
        self.alive_sheep.clear()
        self.dead_sheep.clear()
        self.turn_number = 0
        self.json_data = []
        self.csv_data = []


class Sheep:
    def __init__(self, init_pos_limit: float, move_distance: float, sheep_index: int, position=None):
        logging.debug(
            f"Sheep object created with move_distance value set to {move_distance}, init_pos_limit set to {init_pos_limit}, and sheep_index set to {sheep_index}")
        self.is_alive = True
        self.sheep_index = sheep_index
        if position is None:
            self.position = [random.uniform(-init_pos_limit, init_pos_limit),
                             random.uniform(-init_pos_limit, init_pos_limit)]
        else:
            self.position = position
        logging.info(f" Sheep {self.sheep_index} position set to {self.position}")
        self.move_distance = move_distance

    def move(self):
        logging.debug(f" Sheep {self.sheep_index} move method called")
        direction = random.randint(0, 3)
        if direction == 0:
            self.position[0] += self.move_distance
        elif direction == 1:
            self.position[0] -= self.move_distance
        elif direction == 2:
            self.position[1] += self.move_distance
        else:
            self.position[1] -= self.move_distance
        logging.info(f" Sheep {self.sheep_index} moved to {self.position[0]},{self.position[1]}")

    def die(self):
        logging.debug(f" Sheep {self.sheep_index} die method called")
        logging.info(f"Sheep {self.sheep_index} is eaten")
        self.is_alive = False


class Wolf:
    def __init__(self, move_distance: float):
        logging.debug(f"Wolf object created with move_distance value set to {move_distance}")
        self.hasEaten = False
        self.position = [0.0, 0.0]
        self.move_distance = move_distance

    def find_nearest_sheep(self, sheep_list: list) -> Sheep:
        logging.debug(f" Wolf find_nearest_sheep method called with sheep_list = {sheep_list} ")
        nearest_distance = None
        nearest_sheep_index = None
        for sheep in enumerate(sheep_list):
            distance = calculate_euclidean_distance(self.position, sheep[1].position)
            if nearest_distance is None or nearest_distance > distance:
                nearest_distance = distance
                nearest_sheep_index = sheep[0]
        logging.debug(f" Wolf find_nearest_sheep returns Sheep object {sheep_list[nearest_sheep_index]}")
        return sheep_list[nearest_sheep_index]

    def move(self, sheep_list: list):
        logging.debug(f" Wolf move method called with sheep_list = {sheep_list} ")
        sheep = self.find_nearest_sheep(sheep_list)
        distance = calculate_euclidean_distance(self.position, sheep.position)
        logging.info(f"sheep nearest to wolf is Sheep {sheep.sheep_index} with distance equal to {distance}")
        if distance <= self.move_distance:
            sheep.die()
            self.hasEaten = True
        else:
            self.hasEaten = False
            self.position[0] += (sheep.position[0] - self.position[0]) * self.move_distance / distance
            self.position[1] += (sheep.position[1] - self.position[1]) * self.move_distance / distance
            logging.info(f" wolfed moved to {self.position[0]} {self.position[1]}")
