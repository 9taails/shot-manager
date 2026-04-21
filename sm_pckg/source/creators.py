"""
Module containing the building and functions for the
additional dialogs inside the Shot Manager.
"""
# pylint: disable=no-name-in-module,unnecessary-lambda
# type: ignore[reportPossiblyUnboundVariable]

import os, json, re

from PySide6.QtWidgets import (
    QDialog,
    QMessageBox
)

try:
    import maya.cmds as mc  # type: ignore
    import maya.app.renderSetup.model.renderSetup as render  # type: ignore
except ModuleNotFoundError:  # Local testing
    pass

from ui.ui_creators import LayerCreatorUI, ShotCreatorUI
import source.util as util
from source.util_paths import Path as path
from source.model import data_model


class LayerCreator(QDialog, LayerCreatorUI):
    """ Class providing interface for building render layers based on templates."""

    creator_instance = None  # maintain a single instance of the dialog in Production

    def __init__(self, parent):
        super(LayerCreator, self).__init__(parent)

        self.data = data_model.data
        self.style_sheet = util.load_frame_style()
        self.setup_ui(self)
        self.connect_signals()

    @classmethod
    def show_creator_ui(cls, parent):
        """ Displays the UI for Layer Creator. Maintains a single
            instance of the Class.
            Args:
                parent (ShotManager): Instance of the main window. """
        
        if not cls.creator_instance:
            cls.creator_instance = LayerCreator(parent)
            
        if cls.creator_instance.isHidden():
            cls.creator_instance.show()
            
        else:
            cls.creator_instance.raise_()
            cls.creator_instance.activateWindow()

    def connect_signals(self):
        """ Connect signals to relevant functions. """
        
        self.custom_layer_checkbox.clicked.connect(lambda: self.toggle_custom_input())

    def toggle_custom_input(self):
        """ Enables the QLineEdit widget for inputting user's own render layer name/s.
            Input accepts both a single name or a comma-separated list of names. """
        
        if self.custom_layer_checkbox.isChecked():
            self.custom_beauty_input.setEnabled(True)

        else:
            self.custom_beauty_input.setEnabled(False)

    def create_layers(self, selection):
        
        for shot in selection:
            
            new_layers, templates = self.get_user_input(shot)
            current_layers = list(self.data[shot]["render_layers"])
            print("Layer Creator create layers ", id(self.data))
            to_discard : list= [l for l in new_layers if l in current_layers]
            to_create : list = [l for l in new_layers if l not in current_layers]

            if len(to_discard) > 0:
                print(f"Layer(s) {to_discard} already exist(s). Skipping...")
                continue

            for layer in to_create:
                suffix = templates[to_create.index(layer)]
                if util.maya_is_loaded():
                    self.create_layer_from_template(shot, suffix)
                print("Layer Creator create layers ", id(self.data))
                # Update file via DataModel
                data_model.add_layer(shot, layer, self.data[shot]["start"], self.data[shot]["end"])
            print("Layer Creator create layers ", id(self.data))
            data_model.update_shot_dict(shot, "render_layers", to_create)
            print(to_create)

    def get_user_input(self, shot:str):
        """ Retrieves the list of selected Shots (QStyledItemDelegate) and builds render layers
            for each of those shots, based on user choices.
            Args:
                selection (list): A list of currently selected QModelIndex objects. """

        new_layers = []
        templates = []
        print(shot)
        # MASTER RENDER LAYER
        if self.master_layer_checkbox.isChecked():
            suffix = "master"
            layer_name = "".join([shot, suffix])
            new_layers.append(layer_name)
            templates.append(suffix)

        # FOREGROUND RENDER LAYER
        if self.global_foreground_checkbox.isChecked() or self.shot_foreground_checkbox.isChecked():
            suffix = "fg"
            layer_name = "".join([shot, suffix])
            new_layers.append(layer_name)
            templates.append(suffix)

        # BACKGROUND RENDER LAYER
        if self.global_background_checkbox.isChecked() or self.shot_background_checkbox.isChecked():
            suffix = "bg"
            layer_name = "".join([shot, suffix])
            new_layers.append(layer_name)
            templates.append(suffix)

        # CUSTOM RENDER LAYER/s
        if self.custom_layer_checkbox.isChecked():
            suffix = "custom"
            raw_input = self.custom_beauty_input.text()  # Get user input

            # This finds all alphanumeric sequences (plus underscores) 
            # and ignores everything else (commas, spaces, etc.)
            custom_names = re.findall(r'[\w]+', raw_input)
            
            for name in custom_names:
                layer_name = "".join([shot, name])
                new_layers.append(layer_name)
                templates.append(suffix)
                
        return new_layers, templates
            
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
        self.data.save_data()


    def create_layer_from_template(self, shot_input, suffix):

        """Creates a render layer based on a JSON template

            Args:
                shot_input (string): Format s010preset or s010
                suffix (string): One of the available presets names in the resource folder, ex. fg, bg, master
        """
        #template_dir = util.find_latest("resources/presets/maya/renderLayerPresets", "main")  # Preset directory
        temp_dir = path.temp_dir()  # Temporary directory
        #preset_path = "".join([template_dir, "/", suffix, ".json"])  # Preset path
        # TODO: hardcoded path
        local_path = "E:/Projects/maya/layer_presets"
        preset_path = "".join([local_path, "/", suffix, ".json"])  # Preset path
        print(preset_path)

        if suffix == "custom":
            shot = shot_input[:4]
        else:
            shot = shot_input
        shot_data = self.data[shot]
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
    """ Class handling the creation of new shots. It's responsible for getting the user input
        and calling the Data Model to update the dictionary. It also creates the Maya scene
        structure for each shot. Shot widget creation is handled by the Shot Manager. """

    builder_instance = None  # maintain a single instance of the dialog in Production

    def __init__(self, parent):
        super(ShotCreator, self).__init__(parent)

        self.data = data_model.data
        self.setup_ui(self)
        self.connect_signals()

    @classmethod
    def show_shot_creator(cls, parent):
        """Show and maintain one instance of the Shot Builder UI."""

        if not cls.builder_instance:
            cls.builder_instance = ShotCreator(parent)

        if cls.builder_instance.isHidden():
            cls.builder_instance.show()

        else:
            cls.builder_instance.raise_()
            cls.builder_instance.activateWindow()

    def connect_signals(self):
        """ Connect signals to relevant functions. """
        self.add_shots_button.clicked.connect(lambda: self.add_new_shots())
        self.add_shots_button.clicked.connect(lambda: print("ShotCreator.buttonClick ", id(self.data)))
        if util.maya_is_loaded():
            self.add_shots_button.clicked.connect(lambda: self.populate_scene())
        self.add_shots_button.clicked.connect(lambda: self.accept())

    def get_user_input(self):
        """ Retrieve user input for creating new shots.
            Returns:
                user_input (list): Shot count, initial shot number and shot length. """

        shot_count: int = self.shot_count.value()
        start_shot: int = self.start_shot.value()
        length: int = int(self.shot_length.text())
        user_input: list = [shot_count, start_shot, length]

        return user_input

    def return_new_shots(self):
        """ Checks if there is a file containing shot data or creates it if 
            it doesn't exist. Retrieves user input from the UI and checks which 
            shots already exist in the model. Returns a list of shots to create
            and the length of the shots. """

        # Get input from user
        count, start_shot, length = self.get_user_input()
        end_shot = start_shot + count * 10

        # Create an empty set for new shots
        new_shots = []

        # Add items to the dictionary based on user input
        for num in range(start_shot, end_shot, 10):
            shot_name = "".join(["s", f"{num}".zfill(3)])
            new_shots.append(shot_name)

        # Do not add shots with same names to the dictionary
        # The renaming template uses s000, so filter that out
        existing_shots = list(self.data.keys())
        shots_to_create = [s for s in new_shots if s not in existing_shots and s != "s000"]

        return (shots_to_create, length)

    def add_new_shots(self):
        """ Creates a new entry in the dictionary for each new shot. """

        shot_list, length = self.return_new_shots()

        # Add new shots to the dictionary
        for shot in shot_list:
            data_model.add_shot(shot, length)

    def add_layer(self):
        pass
        """layer_info = master_layer, 1001, int(end_frame), 1, 0

        LayerCreator(None).add_layer_info(data_dict, shot, layer_info)
        
        self.data.save_data()"""

    def populate_scene(self):
        """ Creates all the Maya nodes for the shots in the model. Checks if any of the 
            objects  already exist in the scene and if not, creates shot camera, sets, 
            sequence, light groups and a master render layer. """
       
        layer_list = mc.ls(type="renderSetupLayer")  # type: ignore
        new_shots = self.return_new_shots()[0]

        for shot in new_shots:

            if not util.set_exists(shot):
                util.create_sets(shot)
                print(f"Sets for shot {shot} have been created.")

            if not util.camera_exists(shot):
                util.create_camera(shot)
                print(f"Camera for shot {shot} has been created.")

            if not util.sequence_exists(shot):
                util.create_sequence(shot)
                print(f"Sequence {shot} has been created.")

            if not util.light_exists(shot):
                util.create_light_group(shot)
                print(f"Light group for shot {shot} has been created.")

            if f"{shot}master" not in layer_list:
                LayerCreator(None).create_layer_from_template(shot, "master")
                print(f"Master render layer for {shot} has been created.")
