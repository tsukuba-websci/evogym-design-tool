from tkinter import * 
from tkinter.ttk import *
from ttkbootstrap import Style
import tkinter.messagebox as mb

import os

import utils

#https://github.com/israel-dryer/ttkbootstrap
#https://github.com/israel-dryer/ttkbootstrap/blob/master/src/ttkcreator/__init__.py

class GUI:
    def __init__(self, name, window_data):

        self.master = Tk()
        self.master.title(name)
        

        mx, my, fy = window_data
        self.width = mx//4
        self.height = my


        self.master.geometry(f'{self.width}x{self.height}+{0}+{0}')
        self.update_small()

        dx, dy = self.master.winfo_rootx(), self.master.winfo_rooty()
        self.master.geometry(f'{self.width}x{self.height}+{mx-self.width-dx}+{-dy+fy-my}')

        # frame1 = Frame(master=self.master, height=100)
        # frame1.pack(fill=X)\

        style = Style(theme='cosmo')
        #style.configure("BW.TLabel", foreground="black", background="white")
        style.configure("debug.TFrame", background="white", padding=60)
        
        self.vpad = 10
        self.hpad = 15

        ### Project Information ###
        self.pi_frame = Labelframe(self.master, text='Project Information', padding=15)

        self.pi_name = Entry(self.pi_frame)
        self.pi_name.insert('end', 'my_evironment.json')
        self.pi_name.pack(side='left', fill='x', expand='yes')

        self.pi_save = Button(self.pi_frame, text="Save", command=self.save_click)
        self.pi_save.pack(side='left', fill='x', expand='yes', padx=2)

        self.pi_load = Button(self.pi_frame, text="Load", command=self.load_click)
        self.pi_load.pack(side='left', fill='x', expand='yes', padx=2)

        self.pi_frame.pack(side='top', fill='x', pady=self.vpad, padx=self.hpad)

        ### Mode ###
        self.mode_frame = Labelframe(self.master, text='Edit Mode', padding=15)

        self.mode_var = IntVar()
        self.mode_voxel = Radiobutton(self.mode_frame, value=1, text='Voxel Mode', variable=self.mode_var)
        self.mode_voxel.pack(side='left', fill='x', expand='yes')
        self.mode_voxel.invoke()
        
        self.mode_edge = Radiobutton(self.mode_frame, value=2, text='Edge Mode', variable=self.mode_var)
        self.mode_edge.pack(side='left', fill='x', expand='yes')

        self.mode_edge = Radiobutton(self.mode_frame, value=3, text='Select Mode', variable=self.mode_var)
        self.mode_edge.pack(side='left', fill='x', expand='yes')

        self.mode_frame.pack(side='top', fill='x', pady=self.vpad, padx=self.hpad)

        ### Voxel Selector ###
        self.vs_frame = Labelframe(self.master, text='Voxel Selector', padding=15)
        
        self.vs_options = ['Empty Voxel', 'Rigid Voxel', 'Soft Voxel', 'Horizontal Actuator', 'Vertical Actuator', 'Fixed Voxel']
        self.vs_text = StringVar()
        self.vs_menu = OptionMenu(self.vs_frame, self.vs_text, self.vs_options[2], *tuple(self.vs_options))
        self.vs_menu.pack(side='left', fill='x', padx=(5, 0), pady=5)

        self.vs_frame.pack(side='top', fill='x', pady=self.vpad, padx=self.hpad)

        ### Object Name ###
        self.o_frame = Labelframe(self.master, text='Object Name', padding=15)

        self.o_name = Entry(self.o_frame)
        self.o_name.insert('end', 'object_name')
        self.o_name.pack(side='left', fill='x', expand='yes')

        self.o_frame.pack(side='top', fill='x', pady=self.vpad, padx=self.hpad)

        ### Variables ###
        self.last_object_viewed = None
        self.mode_data = {'mode': utils.VOXELS, 'selector': utils.CELL_SOFT}
        self.old_mode = utils.VOXELS
        self.objects = {}

        self.save_path = 'exported_data'
        self.default_type = '.json'

        self.save_env_func = None
        self.load_env_func = None
        self.load_viewer_func = None

        # self.pi_frame2 = Labelframe(self.master, text='Project Information', padding=15)
        # #self.pi_frame.pack(fill=X, anchor='n', expand=True)

        # test_button = Button(self.pi_frame2, text="Red")
        # test_button.pack(side='left', fill='x', expand='yes', padx=2)

        # test_button = Button(self.pi_frame2, text="Red")
        # test_button.pack(side='left', fill='x', expand='yes', padx=2)

        # test_button = Button(self.pi_frame2, text="Red")
        # test_button.pack(side='left', fill='x', expand='yes', padx=2)

        # self.pi_frame2.pack(side='top', fill='x', pady=10, padx=10)

        # self.pi_separator = Separator(self.st_frame, orient='horizontal')
        # self.pi_separator.pack(fill='x', side='top', anchor='n')

        # self.gs_frame = Frame(self.st_frame, style="debug.TFrame")
        # self.gs_frame.pack(fill=X, anchor='n', expand=True)

        # test_button1 = Button(self.gs_frame, text="Red")
        # test_button1.pack()

    def set_funcs(self, save_env_func, load_env_func, load_viewer_func):
        self.save_env_func = save_env_func
        self.load_env_func = load_env_func
        self.load_viewer_func = load_viewer_func

    def update_object_info(self, objects, recently_updated_objects, hovered_object_id, selected_object_id):

        curr_object_id = None
        if selected_object_id != None:
            curr_object_id = selected_object_id
        if hovered_object_id != None:
            curr_object_id = hovered_object_id

        if curr_object_id == None:
            self.o_frame.pack_forget()
        elif self.last_object_viewed != curr_object_id:
            self.o_name.delete(0, 'end')
            self.o_name.insert('end', objects[curr_object_id].name)
            self.o_frame.pack(side='top', fill='x', pady=self.vpad, padx=self.hpad)
        else:
            if recently_updated_objects:
                self.o_name.delete(0, 'end')
                self.o_name.insert('end', objects[curr_object_id].name)
            else:
                objects[curr_object_id].name = self.o_name.get()

        self.last_object_viewed = curr_object_id

    def update_mode(self, key_presses):
        
        options = {
            1: utils.VOXELS,
            2: utils.EDGES,
            3: utils.SELECT
        }
        self.mode_data['mode'] = options[self.mode_var.get()]

        options = {
            'Empty Voxel': utils.CELL_EMPTY,
            'Rigid Voxel': utils.CELL_RIGID, 
            'Soft Voxel': utils.CELL_SOFT, 
            'Horizontal Actuator': utils.CELL_ACT_H, 
            'Vertical Actuator': utils.CELL_ACT_V,
            'Fixed Voxel': utils.CELL_FIXED}

        if self.mode_data['mode'] == utils.VOXELS:
            self.mode_data['selector'] = options[self.vs_text.get()]

            if self.mode_data['mode'] != self.old_mode:
                self.o_frame.pack_forget()
                self.vs_frame.pack(side='top', fill='x', pady=self.vpad, padx=self.hpad)
                self.o_frame.pack(side='top', fill='x', pady=self.vpad, padx=self.hpad)
        else:
            self.mode_data['selector'] = None
            if self.mode_data['mode'] != self.old_mode:
                self.vs_frame.pack_forget()  
        
        self.old_mode = self.mode_data['mode']

    def load(self, file_name):
        
        if self.load_env_func == None or self.load_viewer_func == None:
            return
        self.load_env_func(file_name)
        self.load_viewer_func(file_name)

        self.last_object_viewed = None
        self.objects = {}

    def save(self, file_name):
        if self.save_env_func == None:
            return
        self.save_env_func(file_name)


    def load_click(self,):
        file_name = self.clean_name(self.pi_name.get())
        if len(self.objects.items()) > 0:
            if mb.askokcancel(title='Overwrite Warning', message=f'Are you sure you want to overwrite editor contents with data from {file_name}?'):
                self.load(file_name)
        else:
            self.load(file_name)

    def save_click(self):

        taken_names = {}
        for key, obj in self.objects.items():
            if not obj.name in taken_names:
                taken_names[obj.name] = 0
            taken_names[obj.name] += 1

        is_fail = False
        for name, count in taken_names.items():
            if count > 1:
                is_fail = True
                break

        if is_fail:
            disp_list = "\n\n"
            for name, count in taken_names.items():
                if count <= 1:
                    continue
                disp_list += f'{name} ({count})\n'
            disp_list = disp_list[:-1]

            mb.showerror(title='Error: Duplicate Names', message=f'All object names must be unique. The following names have been used multiple times: {disp_list}')
            return 

        file_name = self.clean_name(self.pi_name.get())
        save_path = os.path.join(self.save_path, file_name)
        if os.path.exists(save_path):
            if mb.askokcancel(title='Overwrite Warning', message=f'Are you sure you want to overwrite {file_name} with contents from the editor?'):
                self.save(file_name)
        else:
            self.save(file_name)

    def clean_name(self, file_name):
        if not '.' in file_name:
            return file_name + self.default_type
        return file_name

    def update(self, grid, objects, recently_updated_objects, hovered_object_id, selected_object_id, key_presses):

        self.objects = {}
        for object_id, obj in objects.items():
            self.objects[object_id] = obj.copy()

        self.update_object_info(objects, recently_updated_objects, hovered_object_id, selected_object_id)
        self.update_mode(key_presses)

        self.master.update_idletasks()
        self.master.update()

    def update_small(self):
        self.master.update_idletasks()
        self.master.update()