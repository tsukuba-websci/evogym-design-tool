CELL_EMPTY = 0
CELL_RIGID = 1
CELL_SOFT = 2
CELL_ACT_H = 3
CELL_ACT_V = 4
CELL_FIXED = 5

VOXELS = 0
EDGES = 1
SELECT = 2

ARROW_CURSOR = 0
HAND_CURSOR = 1

import random
import numpy as np
import time
from typing import Tuple, Optional

class Timer():
    """
    Helpful timer class to set a target step/render frequency. Used for visualizations.

    Args:
        target_step_frequency (int): target frequency (in steps per second). If `None`, always steps. (default = None)
    """
    def __init__(self, target_step_frequency: Optional[int] = None) -> None:
        self._target_rps = target_step_frequency if target_step_frequency is not None else float('inf')
        self._total_steps = 0
        self.total_count = 0
        self._steps = 0
        self._old_time = self._current_time()

    def _current_time(self) -> int:
        """
        Get the current time in ms.

        Returns:
            int: current time.
        """
        return int(round(time.time() * 1000))

    def should_step(self) -> bool:
        """
        Returns whether or not to step at the current time to maintin the target step frequency.

        Returns:
            bool: whether or not to step (True = should step).
        """
        if self._steps >= (self._target_rps-1)*(self._current_time() - self._old_time)/1000:
            return False
        return True

    def step(self, verbose=False):
        """
        Step the timer.

        Args:
            verbose (bool): whether or not to print out the current step frequency and the average step frequency since starting the timer. (default = False)
        """
        self._steps += 1
        if self._current_time() - self._old_time > 1000:
            self._total_steps += self._steps
            self.total_count += 1
            self._old_time += 1000
            if verbose:
                print(f'rps: {self._steps} | avg rps: {round(self._total_steps/self.total_count*100.0)/100.0}')
            self._steps = 0

class Node:
    def __init__(self, type):
        self.type = type
        self.neighbors = {}
        self.id = None
        self.old_id = None

class Object:
    def __init__(self):
        self.name = None
        self.nodes = {}

    def copy(self,):
        obj = Object()
        obj.name = self.name
        obj.nodes = self.nodes.copy()
        return obj

def flip_y(idx, width, height):
    x,y = idx%width, idx//width
    y = (height-1)-y
    return y*width + x

def make_blank_grid(width, height):
    grid = []
    for i in range(height):
        grid.append([])
        for j in range(width):
            grid[-1].append(Node(0))
            # if (i-3)^2 + (j-3)^2 > 5:
            #     grid[-1].append(Node(0))
            # else:
            #     grid[-1].append(Node(random.randint(1, 5)))
    return grid

def set_ids(grid):
    count = 0
    for row in grid:
        for node in row:
            node.id = count
            count += 1

def set_old_ids(grid):
    for row in grid:
        for node in row:
            node.old_id = node.id

def pair_to_string(a, b):
    if a < b:
        return f'{a} {b}'
    return f'{b} {a}'

def make_thicker(lx, ly, hx, hy, factor):
    if abs(lx - hx) < abs(ly - hy):
        avg = (lx + hx)/2
        lx += (lx - avg)*(factor-1)
        hx += (hx - avg)*(factor-1)
    else:
        avg = (ly + hy)/2
        ly += (ly - avg)*(factor-1)
        hy += (hy - avg)*(factor-1)
    return lx, ly, hx, hy

def get_node_by_index(grid, index):
    grid_height = len(grid)
    grid_width = len(grid[0])
    x, y = index%grid_width, index//grid_width
    node = grid[y][x]
    assert node.id == index, 'Index mismatch, something has gone terribly wrong.'
    return node

def get_left(grid, index):
    grid_height = len(grid)
    grid_width = len(grid[0])
    x, y = index%grid_width, index//grid_width
    x -= 1
    if is_valid(grid, x, y):
        return grid[y][x]
    return None

def get_right(grid, index):
    grid_height = len(grid)
    grid_width = len(grid[0])
    x, y = index%grid_width, index//grid_width
    x += 1
    if is_valid(grid, x, y):
        return grid[y][x]
    return None    

def get_up(grid, index):
    grid_height = len(grid)
    grid_width = len(grid[0])
    x, y = index%grid_width, index//grid_width
    y -= 1
    if is_valid(grid, x, y):
        return grid[y][x]
    return None    

def get_down(grid, index):
    grid_height = len(grid)
    grid_width = len(grid[0])
    x, y = index%grid_width, index//grid_width
    y += 1
    if is_valid(grid, x, y):
        return grid[y][x]
    return None

def is_valid(grid, x, y):
    grid_height = len(grid)
    grid_width = len(grid[0])
    if x < 0 or x >= grid_width:
        return False
    if y < 0 or y >= grid_height:
        return False
    return True

def get_objects(grid):
    grid_height = len(grid)
    grid_width = len(grid[0])
    objects_grid = []
    discovered = {}
    
    for i in range(grid_height):
        objects_grid.append([])
        for j in range(grid_width):
            objects_grid[-1].append(-1)

    object_count = 0
    for i in range(grid_height):
        for j in range(grid_width):
            node = grid[i][j]
            if node.type == CELL_EMPTY or node.id in discovered:
                continue
            flood_fill_explore(node.id, grid, objects_grid, discovered, object_count)
            object_count += 1
    
    objects = {}
    for i in range(grid_height):
        for j in range(grid_width):
            object_id = objects_grid[i][j]
            if object_id == -1:
                continue
            if not object_id in objects:
                objects[object_id] = Object()
            objects[object_id].nodes[grid[i][j].id] = True
    return objects

def flood_fill_explore(index, grid, objects_grid, discovered, object_count):
    
    grid_height = len(grid)
    grid_width = len(grid[0])
    x, y = index%grid_width, index//grid_width

    discovered[index] = True
    objects_grid[y][x] = object_count

    nodes = [get_left(grid, index), get_right(grid, index), get_up(grid, index), get_down(grid, index)]
    for node in nodes:
        if node == None or node.type == CELL_EMPTY or node.id in discovered:
            continue
        if not index in node.neighbors:
            continue
        flood_fill_explore(node.id, grid, objects_grid, discovered, object_count)


    

