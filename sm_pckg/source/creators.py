from __future__ import annotations
import os
import json
from random import randrange

from PySide6.QtWidgets import (
    QDialog,
    QMessageBox
)

try:
    import maya.cmds as mc  # type: ignore
    import maya.app.renderSetup.model.renderSetup as render  # type: ignore
    import pymel.core as pm  # type: ignore

except ModuleNotFoundError:  # Local testing
    pass

import source.util as util
from source.util_paths import Paths
from ui.ui_creators import LayerCreatorUI, ShotCreatorUI


class LayerCreator(QDialog, LayerCreatorUI):
    """A dialog providing interface for building render layers based on templates."""

    creator_instance = None  # maintain a single instance of the dialog in Production

    def __init__(self, parent):
        super(LayerCreator, self).__init__(parent)

        self.data_file_directory = Paths.return_shot_data_full_filepath() # Path to data file
        self.data_directory = Paths.return_shot_data_directory()  # Path to data folder
        self.style_sheet = util.load_frame_style()

        self.setup_ui(self)
        self.custom_layer_checkbox.clicked.connect(lambda: self.toggle_custom_input())

    @classmethod
    def show_creator_ui(cls, parent):
        if not cls.creator_instance:
            cls.creator_instance = LayerCreator(parent)

        if cls.creator_instance.isHidden():
            cls.creator_instance.show()
        else:
            cls.creator_instance.raise_()
            cls.creator_instance.activateWindow()

    def update_data(self, data: dict):
        """ Writes the data to JSON file."""

        if self.data_file_directory is not None:
            with open(self.data_file_directory, "w") as data_dump:
                json.dump(data, data_dump, indent=4)

    def toggle_custom_input(self):

        if self.custom_layer_checkbox.isChecked():

            self.custom_beauty_input.setEnabled(True)

        else:

            self.custom_beauty_input.setEnabled(False)

    def add_new_layers(self, shot_data, selection):
        # Get the current shot info dictionary and create render layers based on the shot data.

        for i in selection:

            shot = i[0]
            layers_in_shot = list(shot_data[shot]["render_layers"])
            new_layers = []

            # MASTER RENDER LAYER
            if self.master_layer_checkbox.isChecked():
                suffix = "master"
                self.create_layer_from_template(shot, suffix)
                layer_name = "".join([shot, suffix])
                new_layers.append(layer_name)

            # FOREGROUND RENDER LAYER
            if self.global_foreground_checkbox.isChecked():
                suffix = "fg"
                self.create_layer_from_template(shot, suffix)
                layer_name = "".join([shot, suffix])
                new_layers.append(layer_name)

            # SHOT-SPECIFIC FOREGROUND RENDER LAYER
            if self.shot_foreground_checkbox.isChecked():
                suffix = "shot_fg"
                self.create_layer_from_template(shot, suffix)
                new_suffix = suffix[5:]
                layer_name = "".join([shot, new_suffix])
                new_layers.append(layer_name)

            # BACKGROUND RENDER LAYER
            if self.global_background_checkbox.isChecked():
                suffix = "bg"
                self.create_layer_from_template(shot, suffix)
                layer_name = "".join([shot, suffix])
                new_layers.append(layer_name)

            # SHOT-SPECIFIC BACKGROUND RENDER LAYER
            if self.shot_background_checkbox.isChecked():
                suffix = "shot_bg"
                self.create_layer_from_template(shot, suffix)
                new_suffix = suffix[5:]
                layer_name = "".join([shot, new_suffix])
                new_layers.append(layer_name)

            # CUSTOM RENDER LAYER
            if self.custom_layer_checkbox.isChecked():
                suffix = "custom"
                custom_input = self.custom_beauty_input.text()  # Get user input

                if ", " in custom_input:

                    custom_output = custom_input.split(", ")

                else:

                    custom_output = [custom_input]

                for co in custom_output:
                    shot_name = shot + co

                    self.create_layer_from_template(shot_name, suffix)
                    layer_name = "".join([shot, co])
                    new_layers.append(layer_name)

            existing_layers = [layer for layer in new_layers if layer in layers_in_shot]
            layers_to_create = [layer for layer in new_layers if layer not in existing_layers]
            length = len(existing_layers)
            warning_shots = ", ".join(existing_layers)

            if length > 0:

                if length == 1:

                    QMessageBox.warning(self, "Warning", "Layer " + warning_shots + " already exists.")

                else:

                    QMessageBox.warning(self, "Warning", "Layers " + warning_shots + " already exist.")

            for layer in layers_to_create:
                layers_in_shot.append(layer)

                # Update view
                shot_data[shot]["render_layers"] = layers_in_shot

                self.update_data(shot_data)

                layer_info = layer, shot_data[shot]["start"], shot_data[shot]["end"], 1, 1

                self.add_layer_info(shot_data, shot, layer_info)

    def add_layer_info(self, data: dict, shot: str, info: tuple):
        """Updates dictionary entry for shot layers with layer specific information.

            Args:
                data : JSON file dictionary
                shot : name of the shot that layers belong to
                info : layer name (str), start frame (int), end frame (int), renderable status (bool) and AOV enabled
                       status (bool)

        """

        name, start, end, renderable, aov = info

        layer_info = {
            "name": name,
            "start": int(start),
            "end": int(end),
            "renderable": renderable,
            "AOV mode": aov,
            "AOVs": []
        }

        info_dict = {
            name: layer_info
        }

        layer_update = LayerCreator(None).layer_dict_exists(data, shot)
        layer_update.update(info_dict)
        self.update_data(data)

    def create_layer_from_template(self, shot_input, suffix):

        """Creates a render layer based on a JSON template

            Args:
                shot_input (string): Format s010preset or s010
                suffix (string): One of the available presets names in the resource folder, ex. fg, bg, master
        """
        #template_dir = util.find_latest("resources/presets/maya/renderLayerPresets", "main")  # Preset directory
        temp_dir = Paths.temp_dir()  # Temporary directory
        #preset_path = "".join([template_dir, "/", suffix, ".json"])  # Preset path
        # TODO: hardcoded path
        local_path = "E:/Projects/maya/layer_presets"
        preset_path = "".join([local_path, "/", suffix, ".json"])  # Preset path
        print(preset_path)

        shot_data: dict = util.shot_data_directory()

        if suffix == "custom":
            shot = shot_input[:4]
        else:
            shot = shot_input
        
        if shot_data:
            start = shot_data[shot]["start"]
            end = shot_data[shot]["end"]
            color = shot_data[shot]["color"]

            # Convert units to Maya units at 25 fps

            start_maya_units = int(start) * 240.0
            end_maya_units = int(end) * 240.0

            # Render layer color per shot
            layer_color = self.get_layer_color(color)

            # Read in JSON template file
            with open(preset_path, "r") as read_file:
                layer_preset = json.load(read_file)

            # Apply edits to the template based on the shot

            shot_info = shot_input, suffix, layer_color, start_maya_units, end_maya_units
            print(shot_info)

            new_layer = self.update_layer_template(layer_preset, shot_info)

            # Save a temporary file for editing
            with open(temp_dir, "w") as temp_file:
                json.dump(new_layer, temp_file, indent=4)

            # Create render layer from the edited JSON file
            if util.maya_is_loaded():
                
                with open(temp_dir, "r") as temp_read:
                    render.instance().decode(json.load(temp_read),  # type: ignore
                                             render.DECODE_AND_RENAME, None)  # type: ignore

            # Remove the temp file
            os.remove(temp_dir)

    def update_layer_template(self, data: dict, shot_info: tuple):
        """ Function goes over existing .json templates and replaces the collection names and include patterns for
            every new shot.

            Args:
                data : shot_data dictionary from JSON
                shot_info : a tuple containing name, layer suffix, assigned color and frame range
        """

        shot_name, suffix, color, start, end = shot_info
        global_fg_set = "global_foreground, *:global_foreground, *:*:global_foreground"
        global_bg_set = "global_background, *:global_background, *:*:global_background"

        if suffix == "custom":  # For custom layer

            shot = shot_name[:4]
            custom_name = shot_name[4:]

            layer = "".join([shot, custom_name])

        elif "shot_" in suffix:  # For shot-specific fg and bg layer

            new_suffix = suffix[5:]
            layer = "".join([shot_name, new_suffix])
            shot = shot_name

        else:

            layer = "".join([shot_name, suffix])
            shot = shot_name

        for k, v in data.copy().items():

            # Loops over the update function for each nested dictionary
            if isinstance(v, dict):  # For DICT
                data[k] = self.update_layer_template(v, shot_info)

            # Loops over the function for each nested list
            elif isinstance(v, list):  # For LIST
                data[k] = [self.update_layer_template(i, shot_info) for i in v]

            # Find keys and replace their value

            elif k == "name":  # Rename collections
                if v == "RENDER_LAYER":  # Edit render layer name
                    del data[k]
                    data[f"{k}"] = layer

                elif v == "renderSetup":  # Edit render setup layer name
                    del data[k]
                    data[f"{k}"] = "".join([shot, v])

                elif v == "RenderSettingsCollection":  # Edit render settings collection name
                    del data[k]
                    data[f"{k}"] = "_".join([shot, v])

                elif v == "_BASE_GRP":  # Edit render layer name
                    del data[k]
                    data[f"{k}"] = "".join([shot, v])

                elif "_COL" in v:  # Rename collections
                    del data[k]
                    data[f"{k}"] = "".join([shot, v])

                elif "_OV" in v:  # Rename overrides
                    del data[k]
                    data[f"{k}"] = "".join([shot, v])

                elif v == "startFrame":  # Edit render layer name
                    del data[k]
                    data[f"{k}"] = "_".join([shot, v])

                elif v == "endFrame":  # Edit render layer name
                    del data[k]
                    data[f"{k}"] = "_".join([shot, v])

            elif k == "labelColor":  # Rename collections
                del data[k]
                data[f"{k}"] = color

            # Find and replace values

            elif v == 250.0:  # Edit start frame
                del data[k]
                data[f"{k}"] = start

            elif v == 30000.0:  # Edit end frame collections
                del data[k]
                data[f"{k}"] = end

            elif v == "shotForegroundSet":  # Add foreground set to collection
                if suffix == "master":
                    del data[k]
                    fg_set = "_".join([shot, "foreground, "])
                    fg_set_ns_1 = "".join(["*:*", shot, "_foreground, "])
                    fg_set_ns_2 = "".join(["*:*:*", shot, "_foreground, "])
                    data[f"{k}"] = fg_set + fg_set_ns_1 + fg_set_ns_2 + global_fg_set
                else:
                    del data[k]
                    fg_set = "_".join([shot, "foreground, "])
                    fg_set_ns_1 = "".join(["*:*", shot, "_foreground, "])
                    fg_set_ns_2 = "".join(["*:*:*", shot, "_foreground, "])
                    data[f"{k}"] = fg_set + fg_set_ns_1 + fg_set_ns_2

            elif v == "shotBackgroundSet":  # Add background set to collection
                if suffix == "master":
                    del data[k]
                    bg_set = "_".join([shot, "background, "])
                    bg_set_ns_1 = "".join(["*:*", shot, "_background, "])
                    bg_set_ns_2 = "".join(["*:*:*", shot, "_background, "])
                    data[f"{k}"] = bg_set + bg_set_ns_1 + bg_set_ns_2 + global_bg_set

                else:
                    del data[k]
                    bg_set = "_".join([shot, "background, "])
                    bg_set_ns_1 = "".join(["*:*", shot, "_background, "])
                    bg_set_ns_2 = "".join(["*:*:*", shot, "_background, "])
                    data[f"{k}"] = bg_set + bg_set_ns_1 + bg_set_ns_2

            elif v == "shotCameraShape":  # Set correct camera
                del data[k]
                cam = "_".join([shot, "camShape, "])
                cam_ns_1 = "".join(["*:*", shot, "_camShape, "])
                cam_ns_2 = "".join(["*:*:*", shot, "_camShape"])
                data[f"{k}"] = cam + cam_ns_1 + cam_ns_2

            elif v == "shotLights, generic":  # Add correct light group
                del data[k]
                s_lights = "_".join([shot, "light, "])
                s_lights_ns_1 = "".join(["*:*", shot, "_light, "])
                s_lights_ns_2 = "".join(["*:*:*", shot, "_light, "])
                g_lights = "generic, "
                g_lights_ns_1 = "*:*generic, "
                g_lights_ns_2 = "*:*:*generic"
                data[f"{k}"] = s_lights + s_lights_ns_1 + s_lights_ns_2 + g_lights + g_lights_ns_1 + g_lights_ns_2

            elif v == "custom":  # Add empty fields for custom collections
                del data[k]
                data[f"{k}"] = ""

            elif v == "excludeSet":  # Add exclude set
                del data[k]
                shot_set = "_".join([shot, "exclude, "])
                shot_set_ns_1 = "".join(["*:*", shot, "_exclude, "])
                shot_set_ns_2 = "".join(["*:*:*", shot, "_exclude, "])
                data[f"{k}"] = shot_set + shot_set_ns_1 + shot_set_ns_2

        return data

    @staticmethod
    def layer_dict_exists(data: dict, shot: str):
        """Backward compatibility function which adds an empty dictionary and "layers" key to the shot dictionary, if
            the layer dictionary doesn't exist.

            Args:
                data: JSON data file
                shot: name of the shot

            Returns:
                layer_dict (dict): an empty dictionary or value of the "layers" key

        """

        try:

            layer_dict = data[shot]["layers"]

        except KeyError:

            layer_dict = dict()
            data[shot]["layers"] = layer_dict

        return layer_dict

    @staticmethod
    def get_layer_color(color):
        """This function contains color dictionaries for render layers and outliner elements, based on the colors
        available in render setup.

        Args:
            color (string): Name of the color, which is assigned to the shot

        Returns:
            color (string): A string with the name of the color, for use in render layers.
        """

        RENDER_COLORS = {
            "red": "Red",
            "green": "Green",
            "blue": "Blue",
            "yellow": "Yellow",
            "purple": "Violet",
            "orange": "Orange"
        }

        layer_color = RENDER_COLORS[color]

        return layer_color


class ShotCreator(QDialog, ShotCreatorUI):
    """A class for the shot building UI dialog.

    This dialog is used to create single or multiple shots in the scene and all the scene elements associated with a
    shot i.e. set, sequence and master render layer. A corresponding camera and light group is created for each shot
    and a color is assigned	to all eligible elements, ie outliner names or render layers, in order to easily
    identify each shot. The class contains all the functions related to creating these elements.
    """

    builder_instance = None  # maintain a single instance of the dialog in Production

    def __init__(self, parent):
        super(ShotCreator, self).__init__(parent)

        self.data_filepath = Paths.return_shot_data_full_filepath()  # Path to data file
        self.data_file_directory = Paths.return_shot_data_directory()  # Path to data folder

        self.setup_ui(self)
        self.add_shots_button.clicked.connect(lambda: self.write_data())
        try:
            self.add_shots_button.clicked.connect(lambda: self.add_shot_elements_to_scene())
        except NameError:
            print("Maya hasn't been loaded yet.")
            pass
        self.add_shots_button.clicked.connect(lambda: self.accept())

    @classmethod
    def show_shot_builder(cls, parent):
        """Show and maintain one instance of the Shot Builder UI."""

        if not cls.builder_instance:
            cls.builder_instance = ShotCreator(parent)

        if cls.builder_instance.isHidden():
            cls.builder_instance.show()

        else:
            cls.builder_instance.raise_()
            cls.builder_instance.activateWindow()

    def update_data(self, data: dict):
        """ Writes the data to JSON file."""

        if self.data_filepath is not None:
            with open(self.data_filepath, "w") as data_dump:
                json.dump(data, data_dump, indent=4)

    def get_user_input(self):
        """This function gets user input for:
        1) The amount of shots to be built.
        2) The shot number to be built, alternatively the starting shot to be used when building multiple shots
        3) The length of the shots.

        Returns:
            number_of_shots (int): An integer.
            shot_number (int): An integer with a default interval of 10.
            shot_length (int): An integer specifying shot duration in frames.
            light_group (bool): False by default, True otherwise.
        """

        number_of_shots = self.shot_count_value.value()
        shot_number = self.start_shot_value.value()
        shot_length = int(self.shot_length_value.text())

        return number_of_shots, shot_number, shot_length

    def write_data(self):
        """Checks if there is a file containing shot data or creates it if it doesn't exist. Retrieves user input from
        the UI and then either updates or writes the model."""

        # Check if data directory exists, if not, create it.

        data_dict = util.shot_data_directory()

        # Get input from user

        number_of_shots, shot_number, shot_length = self.get_user_input()
        end_shot = (shot_number + number_of_shots * 10)

        # Set shot color
        color_list = ("red", "green", "blue", "yellow", "purple", "orange")
        new_shots = []

        # Add items to the dictionary based on user input

        for num in range(shot_number, end_shot, 10):
            shot_name = "".join(["s", f"{num}".zfill(3)])
            new_shots.append(shot_name)

        if data_dict:

            shots = list(data_dict.keys())
            shots_to_create = [sh for sh in new_shots if sh not in shots]

        else:

            shots_to_create = new_shots

            # Add new shots to the dictionary

        for shot in shots_to_create:

            if shot != "s000":

                shot_info_dict = dict()

                if data_dict:

                    data_dict[shot] = shot_info_dict

                else:
                    data_dict = dict()
                    data_dict[shot] = shot_info_dict

                random_index = randrange(0, len(color_list))
                color = color_list[random_index]
                end_frame = 1001 + shot_length - 1
                master_layer = shot + "master"

                shot_info_dict["name"] = shot
                shot_info_dict["color"] = color
                shot_info_dict["start"] = 1001
                shot_info_dict["end"] = int(end_frame)
                shot_info_dict["width"] = 1920
                shot_info_dict["height"] = 1080
                shot_info_dict["render_layers"] = [master_layer]

                self.update_data(data_dict)

                layer_info = master_layer, 1001, int(end_frame), 1, 0

                LayerCreator(None).add_layer_info(data_dict, shot, layer_info)

        self.update_data(data_dict)

    @staticmethod
    def add_shot_elements_to_scene():
        """ Creates all the Maya nodes for the shots in the model. Checks if any of the objects to be created already
            exist in the scene and if not, creates the following for each shot:
            - camera
            - sets
            - Sequencer sequence
            - light groups
            - master render layer
        """

        shot_data = util.shot_data_directory()
        
        try:
            layer_list = mc.ls(type="renderSetupLayer")  # type: ignore

        except NameError:  # Maya module not imported
            pass

        else:

            if shot_data and shot_data is not None:

                new_shots = list(shot_data.keys())

                for shot in new_shots:
                    if shot != "s000":
                        if not util.set_exists(shot):
                            util.create_sets(shot)
                            print("Sets for shot " + f'{shot}' + " have been created.")

                        if not util.camera_exists(shot):
                            util.create_camera(shot)
                            # TODO: change camera rig template scene
                            print("Camera for shot " + f'{shot}' + " has been created.")

                        if not util.sequence_exists(shot):
                            util.create_sequence(shot)
                            print("Sequence " + f'{shot}' + " has been created.")

                        if not util.light_exists(shot):
                            util.create_light_group(shot)
                            print("Light group for shot " + f'{shot}' + " has been created.")

                        master_layer_name = "".join([shot, "master"])

                        if master_layer_name not in layer_list:
                            LayerCreator(None).create_layer_from_template(shot, "master")
                            print("Master render layer for " + f'{shot}' + " has been created.")
