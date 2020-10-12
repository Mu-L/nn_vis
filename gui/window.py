import ntpath
from tkinter import *
from tkinter import filedialog
from typing import List, Dict

from definitions import DATA_PATH
from data.data_handler import ImportanceDataHandler, ProcessedNNHandler
from gui.general_setting import SettingField, SettingEntry, RadioButtons
from gui.neural_network_setting import LayerSettings
from gui.render_setting import RenderSettings


class OptionGui:
    def __init__(self):
        self.test: bool = False

        self.gui_root: Tk = Tk()
        self.layer_settings: List[LayerSettings] = []
        self.settings: Dict[str, any] = {"Closed": False, "current_layer_data": []}

        self.gui_root.title("NNVIS Options")

        # - Stats shown in the GUI ----------------------------------------------------------------------------------- #
        self.stats_frame: LabelFrame = LabelFrame(self.gui_root, text="Statistics", width=60, padx=5, pady=5)
        self.stats_frame.grid(row=0, column=0, padx=5, pady=5)
        self.field_text: dict = {"edge_count": "Edges", "sample_count": "Samples", "cell_count": "Grid Cells",
                                 "pruned_edges": "Pruned Edges", "fps": "FPS"}
        stats_rows: int = 0
        for field in self.field_text.keys():
            self.settings[field] = SettingField(self.stats_frame, self.field_text[field] + ":", row=stats_rows,
                                                column=0)
            stats_rows += 1
        # ------------------------------------------------------------------------------------------------------------ #

        # - Architecture section of the GUI -------------------------------------------------------------------------- #
        self.architecture_frame: LabelFrame = LabelFrame(self.gui_root, text="Neural Network Architecture", width=60,
                                                         padx=5, pady=5)
        self.architecture_frame.grid(row=1, column=0, rowspan=2, padx=5, pady=5)
        self.architecture_buttons: List[Button] = []
        self.save_processed_button: Button = Button(self.architecture_frame, text="Save Processed Network", width=20,
                                                    command=self.save_processed_nn_file)
        self.save_processed_button.grid(row=0, column=0, columnspan=3)
        self.load_processed_button: Button = Button(self.architecture_frame, text="Load Processed Network", width=20,
                                                    command=self.open_processed_nn_file)
        self.load_processed_button.grid(row=1, column=0, columnspan=3)
        self.load_button: Button = Button(self.architecture_frame, text="Load Network", width=20,
                                          command=self.open_importance_file)
        self.load_button.grid(row=2, column=0, columnspan=3)
        self.generate_button: Button = Button(self.architecture_frame, text="Generate Network", width=20,
                                              command=self.generate)
        self.generate_button.grid(row=3, column=0, columnspan=3)
        self.layer_label: Label = Label(self.architecture_frame, text="Modify:")
        self.add_layer_button: Button = Button(self.architecture_frame, text="Add Layer", command=self.add_layer)
        self.clear_layer_button: Button = Button(self.architecture_frame, text="Clear Layer", command=self.clear_layer)
        self.layer_label.grid(row=4, column=0)
        self.add_layer_button.grid(row=4, column=1)
        self.clear_layer_button.grid(row=4, column=2)
        # ------------------------------------------------------------------------------------------------------------ #

        # - Render settings section of the GUI ----------------------------------------------------------------------- #
        self.render_frame: LabelFrame = LabelFrame(self.gui_root, text="Render Settings", width=60,
                                                   padx=5, pady=5)
        self.render_frame.grid(row=0, column=3, columnspan=2, rowspan=3, padx=5, pady=5)

        self.grid_render_settings: RenderSettings = RenderSettings(self.render_frame, "Grid", self.change_setting,
                                                                   ["None", "Cube", "Point"], 0, row=0, column=0)
        edge_shader_settings: Dict[str, any] = {"Size": 0.2, "Base Opacity": 0.0, "Importance Opacity": 1.1,
                                                "Depth Opacity": 0.5, "Density Exponent": 0.5,
                                                "Importance Threshold": 0.01}
        self.edge_render_settings: RenderSettings = RenderSettings(self.render_frame, "Edge", self.change_setting,
                                                                   ["None", "Sphere", "Sphere_Transparent",
                                                                    "Ellipsoid_Transparent", "Line", "Point"],
                                                                   3, edge_shader_settings, row=1, column=0)
        node_shader_settings: Dict[str, any] = {"Size": 0.05, "Base Opacity": 0.0, "Importance Opacity": 1.0,
                                                "Depth Opacity": 0.5, "Density Exponent": 0.5,
                                                "Importance Threshold": 0.01}
        self.node_render_settings: RenderSettings = RenderSettings(self.render_frame, "Node", self.change_setting,
                                                                   ["None", "Sphere", "Sphere_Transparent", "Point"], 2,
                                                                   node_shader_settings, row=2, column=0)
        self.class_setting_frame: LabelFrame = LabelFrame(self.render_frame, text="Class Visibility", width=60,
                                                          padx=5, pady=5)
        self.class_setting_frame.grid(row=0, column=1, rowspan=3, padx=5, pady=5)
        self.class_show: IntVar = IntVar(value=0)
        self.class_show_options: RadioButtons = RadioButtons(self.class_setting_frame,
                                                             ["Independent", "All", "Class 0", "Class 1", "Class 2",
                                                              "Class 3", "Class 4", "Class 5", "Class 6", "Class 7",
                                                              "Class 8", "Class 9"], self.class_show,
                                                             command=self.change_setting, option="show",
                                                             sub_option="class", row=0, column=0, width=10, height=2)
        # ------------------------------------------------------------------------------------------------------------ #

        # - Processing section of the GUI --------------------------------------------------------------------- #
        self.processing_frame: LabelFrame = LabelFrame(self.gui_root, text="Processing", width=60, padx=5, pady=5)
        self.processing_frame.grid(row=0, column=1, columnspan=2, rowspan=3, padx=5, pady=5)

        self.action_frame: LabelFrame = LabelFrame(self.processing_frame, text="Actions", width=60,
                                                   padx=5, pady=5)
        self.action_frame.grid(row=1, column=0, rowspan=2, padx=5, pady=5)
        self.sample_button: Button = Button(self.action_frame, text="Resample Edges", width=15,
                                            command=lambda: self.change_setting("trigger_network", "sample", 1, True))
        self.sample_button.grid(row=0, column=0)
        self.action_state: IntVar = IntVar(value=0)
        self.action_buttons: RadioButtons = RadioButtons(self.action_frame,
                                                         ["Stop Everything", "Node Advect", "Node Diverge",
                                                          "Node Noise", "Edge Advect", "Edge Diverge", "Edge Noise"],
                                                         self.action_state, command=self.change_setting,
                                                         option="action", sub_option="state", row=2, column=0)

        self.smoothing_status: IntVar = IntVar(value=1)
        self.smoothing_checkbox: Checkbutton = Checkbutton(self.action_frame, text="Smoothing",
                                                           variable=self.smoothing_status,
                                                           command=lambda: self.change_setting("edge",
                                                                                               "smoothing",
                                                                                               self.smoothing_status.get()))
        self.change_setting("edge", "smoothing", self.smoothing_status.get())
        self.smoothing_checkbox.grid(row=1, column=0)

        self.setting_frame: LabelFrame = LabelFrame(self.processing_frame, text="Settings", width=60,
                                                    padx=5, pady=5)
        self.setting_frame.grid(row=0, column=0, padx=5, pady=5)
        self.layer_distance: SettingEntry = SettingEntry(self.setting_frame, "Layer distance:", row=0, column=0,
                                                         variable_type="float")
        self.layer_width: SettingEntry = SettingEntry(self.setting_frame, "Layer width:", row=1, column=0,
                                                      variable_type="float")
        self.sampling_rate: SettingEntry = SettingEntry(self.setting_frame, "Sampling rate:", row=2, column=0,
                                                        variable_type="float")
        self.prune_percentage: SettingEntry = SettingEntry(self.setting_frame, "Prune percentage:", row=3,
                                                           column=0, variable_type="float")
        self.node_bandwidth_reduction: SettingEntry = SettingEntry(self.setting_frame, "Node Bandwidth reduction:",
                                                                   row=4, column=0, variable_type="float")
        self.edge_bandwidth_reduction: SettingEntry = SettingEntry(self.setting_frame, "Edge Bandwidth reduction:",
                                                                   row=5, column=0, variable_type="float")
        self.edge_importance_type: SettingEntry = SettingEntry(self.setting_frame, "Edge Importance Type:",
                                                               row=6, column=0, variable_type="int")
        # ------------------------------------------------------------------------------------------------------------ #

    def start(self, layer_data: List[int] = None, layer_distance: float = 1.0, node_size: float = 1.0,
              sampling_rate: float = 10.0, prune_percentage: float = 0.0, node_bandwidth_reduction: float = 0.95,
              edge_bandwidth_reduction: float = 0.9, edge_importance_type: int = 1):
        if layer_data is None:
            default_layer_data = [4, 9, 4]
            for nodes in default_layer_data:
                self.add_layer(nodes)
        else:
            for nodes in layer_data:
                self.add_layer(nodes)

        self.layer_distance.set(layer_distance)
        self.layer_width.set(node_size)
        self.sampling_rate.set(sampling_rate)
        self.prune_percentage.set(prune_percentage)
        self.node_bandwidth_reduction.set(node_bandwidth_reduction)
        self.edge_bandwidth_reduction.set(edge_bandwidth_reduction)
        self.edge_importance_type.set(edge_importance_type)
        self.generate()

        self.gui_root.mainloop()
        self.settings["Closed"] = True

    def save_processed_nn_file(self):
        filename = filedialog.asksaveasfilename()
        if not filename:
            return
        self.settings["save_processed_nn_path"] = filename
        self.settings["save_file"] = True

    def open_processed_nn_file(self):
        filename = filedialog.askopenfilename(initialdir=DATA_PATH, title="Select A File",
                                              filetypes=(("processed nn files", "*.npz"),))
        data_loader: ProcessedNNHandler = ProcessedNNHandler(filename)
        self.settings['network_name'] = ntpath.basename(filename) + "_processed"
        self.update_layer(data_loader.layer_data, processed_nn=data_loader)

    def open_importance_file(self):
        filename = filedialog.askopenfilename(initialdir=DATA_PATH, title="Select A File",
                                              filetypes=(("importance files", "*.npz"),))
        data_loader: ImportanceDataHandler = ImportanceDataHandler(filename)
        self.settings['network_name'] = ntpath.basename(filename) + "_raw"
        self.update_layer(data_loader.layer_data, importance_data=data_loader)

    def update_layer(self, layer_data: List[int], importance_data: ImportanceDataHandler = None,
                     processed_nn: ProcessedNNHandler = None):
        self.clear_layer()

        for nodes in layer_data:
            self.add_layer(nodes)
        self.generate(importance_data, processed_nn)

    def add_layer(self, nodes: int = 9):
        layer_id: int = len(self.layer_settings)
        self.layer_settings.append(LayerSettings(self.architecture_frame, layer_id, 5, 0, self.remove_layer))
        self.layer_settings[layer_id].set_neurons(nodes)

    def clear_layer(self):
        for ls in self.layer_settings:
            ls.remove()
        self.layer_settings = []

    def remove_layer(self, layer_id: int):
        self.layer_settings[layer_id].remove()
        self.layer_settings.remove(self.layer_settings[layer_id])

        for i, ls in enumerate(self.layer_settings):
            ls.layer_id = i
            ls.grid()
        self.layer_label.grid(row=0, column=0)

    def generate(self, importance_data: ImportanceDataHandler = None, processed_nn: ProcessedNNHandler = None):
        self.action_buttons.press(0)
        layer_data: List[int] = []
        for ls in self.layer_settings:
            layer_data.append(ls.get_neurons())
        self.settings["current_layer_data"] = layer_data
        self.settings["importance_data"] = importance_data
        self.settings["processed_nn"] = processed_nn
        self.settings["layer_distance"] = self.layer_distance.get()
        self.settings["layer_width"] = self.layer_width.get()
        self.settings["sampling_rate"] = self.sampling_rate.get()
        self.settings["prune_percentage"] = self.prune_percentage.get()
        self.settings["node_bandwidth_reduction"] = self.node_bandwidth_reduction.get()
        self.settings["edge_bandwidth_reduction"] = self.edge_bandwidth_reduction.get()
        self.settings["edge_importance_type"] = self.edge_importance_type.get()
        self.settings["update_model"] = True

    def change_setting(self, setting_type: str, sub_type: str, value: int, stop_action: bool = False):
        if stop_action:
            self.action_buttons.press(0)
        self.settings[setting_type + "_" + sub_type] = value
