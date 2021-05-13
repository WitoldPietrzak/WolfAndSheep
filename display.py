from tkinter import *
from tkinter import messagebox as msg
from tkinter import colorchooser
from tkinter import filedialog
import tkinter.ttk as ttk
import matplotlib
import matplotlib.backend_bases as bb
import os
import pickle
import json
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import logic as chase
import time
import _thread

matplotlib.use("TkAgg")


class ChaseDisplay:
    def __init__(self):
        self.window_title = "Wolf and Sheep"
        self.window_resolution = '720x640'
        self.sim_field_width = 300
        self.sim_field_height = 300
        self.zoom = 1.5
        self.sheep_color = 'blue'
        self.wolf_color = 'red'
        self.background_color = 'green'
        self.line_color = 'yellow'
        self.line = False
        self.line_choice = None
        self.idle_time = 1.0
        self.idle_choice = None
        self.simulation = chase.Simulation(0, 0, 10.0, 0.5, 1.0, False, "", None)
        self.window = Tk(className=self.window_title)
        self.window.geometry(self.window_resolution)
        self.window.resizable(False, False)
        self.isStarted = False

        self.start_button = Button(self.window, text="Start", command=self.start)
        self.start_button.grid(column=0, row=1)

        self.step_button = Button(self.window, text="Step", command=self.step)
        self.step_button.grid(column=0, row=2)

        self.reset_button = Button(self.window, text="Reset", command=self.reset)
        self.reset_button.grid(column=0, row=3)

        self.zoom_slider = Scale(self.window, from_=3.0, to=0.1, orient=HORIZONTAL, resolution=0.1, width=10,
                                 length=500,
                                 command=self.change_zoom)
        self.zoom_slider.set(self.zoom)
        self.zoom_slider.grid(column=1, row=11, columnspan=10)
        self.update_display()

        self.menu_bar = Menu(self.window)
        self.window.configure(menu=self.menu_bar)
        self.menu_file = Menu(self.menu_bar, tearoff=0)
        self.menu_file.add_command(label="Open", command=self.open)
        self.menu_file.add_command(label="Save", command=self.save)
        self.menu_file.add_command(label="Quit", command=self.quit)

        self.menu_bar.add_cascade(label="File", menu=self.menu_file)
        self.menu_bar.add_command(label="Settings", command=self.settings_display)
        self.window.mainloop()

    def detect_click(self, event):
        if event.button == bb.MouseButton.LEFT:
            self.spawn_sheep(event)
        if event.button == bb.MouseButton.RIGHT:
            self.move_wolf(event)
        self.update_display()

    def move_wolf(self, event):
        if self.isStarted:
            return
        x, y = event.inaxes.transData.inverted().transform((event.x, event.y))
        self.simulation.move_wolf_manual([x, y].copy())

    def spawn_sheep(self, event):
        if self.isStarted:
            return
        x, y = event.inaxes.transData.inverted().transform((event.x, event.y))
        self.simulation.add_sheep(len(self.simulation.sheep), [x, y].copy())

    def change_zoom(self, val):
        self.zoom = float(val)
        self.update_display()

    def settings_display(self):
        settings_window = Toplevel(self.window)
        settings_window.grab_set()
        settings_window.resizable(False, False)
        settings_window.wm_title("Settings")
        title_label = Label(settings_window, text="Configure Settings")
        self.line_choice = BooleanVar(value=self.line)
        title_label.grid(column=0, row=0)

        color_frame = LabelFrame(settings_window, text="Display Settings")
        sheep_color_button = Button(color_frame, text="Change Sheep Color",
                                    command=lambda: [self.change_sheep_color(), self.update_display(),
                                                     update_settings_display()])
        wolf_color_button = Button(color_frame, text="Change Wolf Color",
                                   command=lambda: [self.change_wolf_color(), self.update_display(),
                                                    update_settings_display()])
        field_color_button = Button(color_frame, text="Change Field Color",
                                    command=lambda: [self.change_field_color(), self.update_display(),
                                                     update_settings_display()])
        line_checkbox = Checkbutton(color_frame, text="Show line", variable=self.line_choice, onvalue=True,
                                    offvalue=False,
                                    command=lambda: [update_settings_display(), self.update_display()])
        line_color_button = Button(color_frame, text="Change Line Color",
                                   command=lambda: [self.change_line_color(), self.update_display(),
                                                    update_settings_display()], state=DISABLED)

        sheep_color_example = Canvas(color_frame, bg=self.sheep_color, height=20, width=20)
        wolf_color_example = Canvas(color_frame, bg=self.wolf_color, height=20, width=20)
        field_color_example = Canvas(color_frame, bg=self.background_color, height=20, width=20)
        line_color_example = Canvas(color_frame, bg=self.line_color, height=20, width=20)
        if self.line_choice.get() is True:
            line_color_button.configure(state=NORMAL)

        timer_frame = LabelFrame(settings_window, text="Timer Settings")
        self.idle_choice = DoubleVar(value=self.idle_time)
        save_button = Button(settings_window, text="Save Config",
                             command=self.save_config)
        load_button = Button(settings_window, text="Load Config",
                             command=lambda: [self.load_config(), update_settings_display()])
        close_button = Button(settings_window, text="Ok",
                              command=settings_window.destroy)

        color_frame.grid(column=0, row=1, padx=10, pady=10)
        sheep_color_button.grid(column=0, row=1, padx=10, pady=10)
        sheep_color_example.grid(column=1, row=1, padx=10, pady=10)
        wolf_color_button.grid(column=0, row=2, padx=10, pady=10)
        wolf_color_example.grid(column=1, row=2, padx=10, pady=10)
        field_color_button.grid(column=0, row=3, padx=10, pady=10)
        field_color_example.grid(column=1, row=3, padx=10, pady=10)
        line_checkbox.grid(column=0, row=4, padx=10, pady=10)
        line_color_button.grid(column=0, row=5, padx=10, pady=10)
        line_color_example.grid(column=1, row=5, padx=10, pady=10)
        timer_frame.grid(column=0, row=2, padx=10, pady=10)

        #  for i in range(1, 5):
        #     timer_radio = Radiobutton(timer_frame, text=0.5 * i, variable=self.idle_choice, value=0.5 * i,command=lambda: [update_settings_display()])
        #     timer_radio.grid(row=i // 3, column=((i - 1) % 2) + 1, padx=10, pady=10
        timer_combobox = ttk.Combobox(timer_frame, textvariable=self.idle_choice, values=(0.5, 1.0, 1.5, 2.0),
                                      state="readonly", width=5)
        timer_button = Button(timer_frame, text="Update Timer", command=lambda: [update_settings_display()])

        timer_combobox.grid(row=0, column=0, padx=10, pady=10)
        timer_button.grid(row=0, column=1, padx=10, pady=10)
        save_button.grid(column=0, row=3, padx=10, pady=10)
        load_button.grid(column=0, row=4, padx=10, pady=10)
        close_button.grid(column=0, row=5, ipadx=5, ipady=5)

        def update_settings_display():

            sheep_color_example.configure(bg=self.sheep_color)
            wolf_color_example.configure(bg=self.wolf_color)
            field_color_example.configure(bg=self.background_color)
            line_color_example.configure(bg=self.line_color)
            self.idle_time = self.idle_choice.get()
            self.line = self.line_choice.get()
            if self.line_choice.get() is True:
                line_color_button.configure(state=NORMAL)
            else:
                line_color_button.configure(state=DISABLED)

    def start(self):
        self.start_button.configure(text="Stop", command=self.stop)
        self.step_button.configure(state=DISABLED)
        self.reset_button.configure(state=DISABLED)
        self.menu_bar.entryconfigure("File", state=DISABLED)
        self.menu_bar.entryconfigure("Settings", state=DISABLED)
        self.isStarted = True
        _thread.start_new_thread(self.loop, ())

    def loop(self):
        while self.isStarted:
            self.step()
            time.sleep(self.idle_time)

    def stop(self):
        self.isStarted = False
        self.start_button.configure(text="Start", command=self.start)
        self.step_button.configure(state=NORMAL)
        self.reset_button.configure(state=NORMAL)
        self.menu_bar.entryconfigure("File", state=NORMAL)
        self.menu_bar.entryconfigure("Settings", state=NORMAL)

    @staticmethod
    def quit():
        answer = msg.askyesno("Exit", "Are you sure you want to leave?")
        if answer:
            raise SystemExit

    def open(self):
        my_filetypes = [('save file', '.chase')]
        open_file = filedialog.askopenfile(mode="rb", parent=self.window, initialdir=os.getcwd(),
                                           title="Select a file name", filetypes=my_filetypes)
        if open_file is None:
            return
        save_data = pickle.load(open_file)
        open_file.close()
        self.simulation = pickle.loads(save_data["simulation"])
        self.update_display()

    def load_config(self):
        my_filetypes = [('settings file', '.conf')]
        open_file = filedialog.askopenfile(mode="r", parent=self.window, initialdir=os.getcwd(),
                                           title="Select a file name", filetypes=my_filetypes)
        if open_file is None:
            return
        save_data = json.load(open_file)
        open_file.close()
        self.zoom = save_data["zoom"]
        self.sheep_color = save_data["sheep_color"]
        self.wolf_color = save_data["wolf_color"]
        self.background_color = save_data["field_color"]
        self.line_color = save_data["line_color"]
        self.line = save_data["line"]
        self.idle_time = save_data["idle_timer"]
        self.zoom_slider.set(self.zoom)
        self.update_display()

    def save(self):
        my_filetypes = [('save file', '.chase')]
        save_file = filedialog.asksaveasfile(mode="wb", parent=self.window, initialdir=os.getcwd(),
                                             title="Select a file name", filetypes=my_filetypes,
                                             defaultextension=".chase")
        if save_file is None:
            return
        save_data = {
            "simulation": pickle.dumps(self.simulation),
        }
        pickle.dump(save_data, save_file)
        save_file.close()

    def save_config(self):
        my_filetypes = [('settings file', '.conf')]
        save_file = filedialog.asksaveasfile(mode="w", parent=self.window, initialdir=os.getcwd(),
                                             title="Select a file name", filetypes=my_filetypes,
                                             defaultextension=".conf")
        if save_file is None:
            return
        save_data = {
            "zoom": self.zoom,
            "sheep_color": self.sheep_color,
            "wolf_color": self.wolf_color,
            "field_color": self.background_color,
            "line_color": self.line_color,
            "idle_timer": self.idle_time,
            "line": self.line
        }
        json.dump(save_data, save_file)

        save_file.close()

    def change_wolf_color(self):
        buff = colorchooser.askcolor(self.wolf_color)[1]
        if buff:
            self.wolf_color = buff

    def change_sheep_color(self):
        buff = colorchooser.askcolor(self.sheep_color)[1]
        if buff:
            self.sheep_color = buff

    def change_field_color(self):
        buff = colorchooser.askcolor(self.background_color)[1]
        if buff:
            self.background_color = buff

    def change_line_color(self):
        buff = colorchooser.askcolor(self.line_color)[1]
        if buff:
            self.line_color = buff

    def step(self):
        if not self.simulation.alive_sheep:
            msg.showinfo("Brak owiec", "Nie można wykonać żądanej operacji")
            if self.isStarted:
                self.stop()
            return
        self.simulation.simulate_turn()
        self.update_display()
        if not self.simulation.alive_sheep:
            msg.showinfo("Brak owiec", "Wszystkie owce zostały zjedzone")
            if self.isStarted:
                self.stop()

    def reset(self):
        self.simulation.reset()
        self.update_display()

    def update_display(self):
        sheep_label = Label(self.window, text="Sheep Alive: " + str(len(self.simulation.alive_sheep)))
        sheep_label.grid(column=0, row=0)
        turn_label = Label(self.window, text="Turn Number: " + str(self.simulation.turn_number))
        turn_label.grid(column=1, row=0)

        self.draw_field()

    def draw_field(self):
        limit = self.simulation.init_pos_limit * self.zoom
        x, y = self.simulation.wolf.position

        figure = Figure(figsize=(5, 5))
        figure.patch.set_facecolor(self.background_color)
        figure.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
        sp = figure.add_subplot(1, 1, 1)
        sp.axis('off')
        axes = figure.gca()
        axes.set_xlim([-limit, limit])
        axes.set_ylim([-limit, limit])
        if self.line is True and self.simulation.alive_sheep:
            nearest_sheep_pos = self.simulation.wolf.find_nearest_sheep(self.simulation.alive_sheep).position
            line_x = [self.simulation.wolf.position[0]]
            line_y = [self.simulation.wolf.position[1]]
            line_x.append(nearest_sheep_pos[0])
            line_y.append(nearest_sheep_pos[1])
            sp.plot(line_x, line_y, '--', color=self.line_color, linewidth=1)
        sp.plot(x, y, 'o', color=self.wolf_color, markersize=6 / (self.zoom / 1.5))
        x = []
        y = []
        for sheep in self.simulation.alive_sheep:
            x.append(sheep.position[0])
            y.append(sheep.position[1])
        sp.plot(x, y, 'o', color=self.sheep_color, markersize=6 / (self.zoom / 1.5))

        canvas = FigureCanvasTkAgg(figure, self.window)
        canvas.get_tk_widget().configure(background=self.background_color)
        canvas.get_tk_widget().grid(row=1, column=1, rowspan=10, columnspan=10)
        canvas.mpl_connect("button_press_event", self.detect_click)


chase_display = ChaseDisplay()
chase_display.window.mainloop()
