from colors import ACT_H_VOXEL, ACT_V_VOXEL, EMPTY_VOXEL, FIXED_VOXEL, RIGID_VOXEL, SOFT_VOXEL
import utils
import data_manager

class Env:
    def __init__(self):
        self.grid_width = 10
        self.grid_height = 10

        self.grid = utils.make_blank_grid(self.grid_width, self.grid_height)
        utils.set_ids(self.grid)

        self.mode = utils.VOXELS
        self.selector = utils.CELL_SOFT

        self.objects = {}
        self.node_to_object = {}
        self.unnamed_obj_count = 1

        self.hovered_object_id = None
        self.selected_object_id = None

        self.just_altered = None
        self.need_to_update_objects = False

        self.dm = data_manager.DataManager()

    def update(self, hovered, selected, mouse_pressed, mouse_held, key_presses, mode_data):
        
        self.need_to_update_objects = False
        self.just_altered = None

        if mouse_pressed:
            self.handle_mouse_press(hovered)
        if mouse_held:
            self.handle_mouse_held(hovered)

        # self.handle_key_presses(key_presses)
        self.update_mode(mode_data)

        if self.need_to_update_objects:
            self.update_objects()

        self.update_active_objects(hovered, selected)

    def load(self, file_name):
        self.grid_width, self.grid_height, self.grid, self.objects, self.node_to_object, self.unnamed_obj_count = self.dm.load(file_name)
        self.hovered_object_id = None
        self.selected_object_id = None

    def save(self, file_name):
        self.dm.save(file_name, self.grid, self.objects)

    def update_mode(self, mode_data):
        self.mode = mode_data['mode']
        self.selector = mode_data['selector']

    def update_active_objects(self, hovered, selected):

        self.hovered_object_id = None
        if hovered != None and hovered[0] == 'node' and utils.get_node_by_index(self.grid, hovered[2]).type != utils.CELL_EMPTY:
            self.hovered_object_id = self.node_to_object[hovered[2]]
        if hovered != None and hovered[0] == 'edge':
            a, b = tuple(hovered[1].split())
            a, b = int(a), int(b)
            self.hovered_object_id = self.node_to_object[a]

        self.selected_object_id = None
        if selected != None and selected[0] == 'node' and utils.get_node_by_index(self.grid, selected[2]).type != utils.CELL_EMPTY:
            self.selected_object_id = self.node_to_object[selected[2]]
        if selected != None and selected[0] == 'edge':
            a, b = tuple(selected[1].split())
            a, b = int(a), int(b)
            self.selected_object_id = self.node_to_object[a]

    def update_objects(self,):

        new_objects = utils.get_objects(self.grid)

        for object_id, obj in new_objects.items():
            for node_id in obj.nodes:
                if obj.name != None:
                    break
                for curr_obj_id, curr_obj in self.objects.items():
                    if node_id in curr_obj.nodes:
                        obj.name = curr_obj.name
                        break
            if obj.name == None:
                obj.name = f'new_object_{self.unnamed_obj_count}'
                self.unnamed_obj_count += 1

        self.objects = {}
        for object_id, obj in new_objects.items():
            self.objects[object_id] = obj.copy()

        self.node_to_object = {}
        for object_id, obj in self.objects.items():
            for node_id in obj.nodes:
                self.node_to_object[node_id] = object_id

        
    # def handle_key_presses(self, key_presses):
    #     if key_presses['z']:
    #         self.selector = utils.CELL_EMPTY
    #     if key_presses['x']:
    #         self.selector = utils.CELL_RIGID
    #     if key_presses['c']:
    #         self.selector = utils.CELL_SOFT
    #     if key_presses['v']:
    #         self.selector = utils.CELL_ACT_H
    #     if key_presses['b']:
    #         self.mode = utils.VOXELS
    #     if key_presses['n']:
    #         self.mode = utils.EDGES

    def handle_mouse_press(self, hovered):

        if hovered == None:
            return

        if self.mode == utils.EDGES and hovered[0] == 'edge':
            a, b = tuple(hovered[1].split())
            a, b = int(a), int(b)
            self.toggle_connection(a, b)
            self.just_altered = hovered

    def handle_mouse_held(self, hovered):
        
        if hovered == None:
            return

        if self.mode == utils.VOXELS and hovered[0] == 'node':
            node = self.get_node_by_index(hovered[2])

            if self.selector == utils.CELL_EMPTY:
                if node.type != utils.CELL_EMPTY:
                    self.remove_node(hovered[2])
            else:
                if node.type == utils.CELL_EMPTY:
                    self.add_node(hovered[2], self.selector)
                    self.just_altered = hovered
                else:
                    if node.type != self.selector:
                        self.edit_node(hovered[2], self.selector)
                        self.just_altered = hovered

    def toggle_connection(self, a_id, b_id):
        a_node = self.get_node_by_index(a_id)
        b_node = self.get_node_by_index(b_id)

        if a_id in b_node.neighbors:
            del b_node.neighbors[a_id]
            del a_node.neighbors[b_id]
        else:
            b_node.neighbors[a_id] = True
            a_node.neighbors[b_id] = True

        self.need_to_update_objects = True

    def remove_node(self, index):
        self.get_node_by_index(index).type = utils.CELL_EMPTY
        neighbors = [self.get_left(index), self.get_right(index), self.get_up(index), self.get_down(index)]

        for node in neighbors:
            if node == None:
                continue
            if index in node.neighbors:
                del node.neighbors[index]
            if node.id in self.get_node_by_index(index).neighbors:
                del self.get_node_by_index(index).neighbors[node.id]

        self.need_to_update_objects = True

    def add_node(self, index, value):
        self.get_node_by_index(index).type = value
        neighbors = [self.get_left(index), self.get_right(index), self.get_up(index), self.get_down(index)]

        for node in neighbors:
            if node == None:
                continue
            node.neighbors[index] = True
            self.get_node_by_index(index).neighbors[node.id] = True

        self.need_to_update_objects = True

    def edit_node(self, index, value):
        self.get_node_by_index(index).type = value

    def get_node_by_index(self, index):
        x, y = index%self.grid_width, index//self.grid_width
        node = self.grid[y][x]
        assert node.id == index, 'Index mismatch, something has gone terribly wrong.'
        return node

    def get_left(self, index):
        x, y = index%self.grid_width, index//self.grid_width
        x -= 1
        if self.is_valid(x, y):
            return self.grid[y][x]
        return None

    def get_right(self, index):
        x, y = index%self.grid_width, index//self.grid_width
        x += 1
        if self.is_valid(x, y):
            return self.grid[y][x]
        return None    

    def get_up(self, index):
        x, y = index%self.grid_width, index//self.grid_width
        y -= 1
        if self.is_valid(x, y):
            return self.grid[y][x]
        return None    

    def get_down(self, index):
        x, y = index%self.grid_width, index//self.grid_width
        y += 1
        if self.is_valid(x, y):
            return self.grid[y][x]
        return None

    def is_valid(self, x, y):
        if x < 0 or x >= self.grid_width:
            return False
        if y < 0 or y >= self.grid_height:
            return False
        return True