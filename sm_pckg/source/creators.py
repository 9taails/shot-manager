"""
Module containing the building and functions for the
additional dialogs inside the Shot Manager.
"""
# pylint: disable=no-name-in-module,unnecessary-lambda,import-error
# type: ignore[reportPossiblyUnboundVariable]

import os
import json
import re
from PySide6.QtWidgets import QDialog

try:
    import maya.cmds as mc  # type: ignore
    import maya.app.renderSetup.model.renderSetup as render  # type: ignore
except ModuleNotFoundError:  # Local testing
    pass

from ui.ui_creators import LayerCreatorUI, ShotCreatorUI
from source import util
from source.util_paths import Path as path
from source.model import data_model


class LayerCreator(QDialog, LayerCreatorUI):
    """ Class providing interface for building render layers based on templates."""

    creator_instance = None  # maintain a single instance of the dialog in Production

    def __init__(self, parent):
        super().__init__(parent)

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

    def get_user_input(self, shot:str):
        """ Checks user selection and for checked items, appends the resulting layer name to
            a new_layers list (for filtering later on to prevent duplicates) and the corresponding
            template suffix to the templates list. Returns both lists.
            Args:
                shot (str): Name of the shot. """

        new_layers = []
        templates = []

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

    def add_layers_to_data(self, selection):
        """ Reads the user input for new layers, filters out layers which already exist for
            the given shot and creates DataModel entry and a physical render layer for each 
            new layer. Updates the shot entry in teh DataModel with new layers list.
            Args:
                selection (list): A list of shot names currently selected in the QTreeView. """

        for shot in selection:

            new_layers, templates = self.get_user_input(shot)
            current_layers = list(self.data[shot]["render_layers"])
            to_discard : list= [l for l in new_layers if l in current_layers]
            to_create : list = [l for l in new_layers if l not in current_layers]

            if len(to_discard) > 0:
                print(f"Layer(s) {to_discard} already exist(s). Skipping...")
                continue

            for layer in to_create:
                suffix = templates[to_create.index(layer)]

                # Update file via DataModel
                data_model.add_layer(shot, layer, self.data[shot]["start"], self.data[shot]["end"])
                # This must come after add_layer, since it reads the data file to edit the render
                # templates.
                if util.maya_is_loaded():
                    self.create_layer_from_template(shot, layer, suffix)

            data_model.update_shot_dict(shot, "render_layers", to_create)

            print(f"Following shot(s) have been created: {to_create}")

    def create_layer_from_template(self, shot, layer, suffix):
        """ Creates a render layer based on a JSON template.
            Args:
                shot (str): Name of the shot.
                layer (str): Name of the layer.
                suffix (str): Name of the template file (fg, bg, master, custom). """

        temp_dir = path.temp_dir()  # Temporary directory
        preset_dir = path.preset_files
        preset_path = "".join([preset_dir, "/", suffix, ".json"])  # Preset path

        # Read in JSON template file
        with open(preset_path, encoding="utf-8", mode="r") as read_file:
            template = json.load(read_file)

        # Loop over items in the template and rename the nodes
        # The template has been manually edited with keywords to use in the search pattern

        new_layer = self.update_layer_template(template, shot, layer, suffix)

        # There is no need to keep an edited template JSON permanently.
        # Save a temporary file for editing instead, create the render layer and
        # delete the temporary file.

        with open(temp_dir, encoding="utf-8", mode="w") as temp_write:
            json.dump(new_layer, temp_write, indent=4)

        if util.maya_is_loaded():
            with open(temp_dir, encoding="utf-8", mode="r") as temp_read:
                render.instance().decode(json.load(temp_read),  # type: ignore
                                            render.DECODE_AND_RENAME, None)  # type: ignore
        # Remove the temp file
        os.remove(temp_dir)

    def update_layer_template(self, template, shot, layer, suffix):
        """ Recursively edits the JSON template file defined by the suffix, renaming the values
            and setting correct attributes from the DataModel.
            Args:
                template (dict) : A JSON file with template names; uses the same 
                                format as when using Export render layer... option in Maya
                shot (str) : Name of the shot
                layer (str) : Name of the layer
                suffix (str) : Defines which template to open for editing. """
        # pylint: disable=too-many-branches

        layer_dict:dict = data_model.return_layer_dict(shot, layer)

        for k, v in self.data.copy().items():

            # Loops over the update function for each nested dictionary
            if isinstance(v, dict):  # For DICT
                template[k] = self.update_layer_template(v, shot, layer, suffix)

            # Loops over the function for each nested list
            elif isinstance(v, list):  # For LIST
                template[k] = [self.update_layer_template(i, shot, layer, suffix) for i in v]

            # Find keys and replace their value
            # Rename collections
            elif k == "name":
                if v == "RENDER_LAYER":
                    del template[k]
                    template[f"{k}"] = layer

                elif v in ["renderSetup","RenderSettingsCollection", "_BASE_GRP",
                           "startFrame", "endFrame"]:
                    del template[k]
                    template[f"{k}"] = f"{shot}{v}"

                elif "_COL" in v or "_OV" in v:
                    del template[k]
                    template[f"{k}"] = f"{shot}{v}"

            elif k == "labelColor":
                del template[k]
                template[f"{k}"] = self.data[shot].get("color", "blue")

            # Edit contents
            elif v == 250.0:  # Edit start frame
                del template[k]
                template[f"{k}"] = layer_dict.get("start", 1001) * 240 # Convert to 25FPS Maya units

            elif v == 30000.0:  # Edit end frame collections
                del template[k]
                template[f"{k}"] = layer_dict.get("end", 1200) * 240 # Convert to 25FPS Maya units

            # Set the layer pattern to include default sets and groups
            elif v == "shotForegroundSet":
                del template[k]
                if suffix == "master":
                    template[f"{k}"] = f"{shot}_foreground, global_foreground"
                else:
                    template[f"{k}"] = f"{shot}_foreground"

            elif v == "shotBackgroundSet":  # Add background set to collection
                del template[k]
                if suffix == "master":
                    template[f"{k}"] = f"{shot}_background, global_background"
                else:
                    template[f"{k}"] = f"{shot}_background"

            elif v == "shotCameraShape":  # Set correct camera
                del template[k]
                template[f"{k}"] = f"{shot}_camShape, *:*{shot}_camShape"

            elif v == "shotLights, generic":  # Add correct light group
                del template[k]
                template[f"{k}"] = f"{shot}_light, generic"

            elif v == "custom":  # Add empty fields for custom collections
                del template[k]
                template[f"{k}"] = ""

            elif v == "excludeSet":  # Add exclude set
                del template[k]
                template[f"{k}"] = f"{shot}_exclude"

        return template


class ShotCreator(QDialog, ShotCreatorUI):
    """ Class handling the creation of new shots. It's responsible for getting the user input
        and calling the Data Model to update the dictionary. It also creates the Maya scene
        structure for each shot. Shot widget creation is handled by the Shot Manager. """

    builder_instance = None  # maintain a single instance of the dialog in Production

    def __init__(self, parent):
        super().__init__(parent)

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
        self.add_shots_button.clicked.connect(lambda: self.add_shots_to_data())
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

    def add_shots_to_data(self):
        """ Creates a new entry in the dictionary for each new shot. """

        shot_list, length = self.return_new_shots()

        # Add new shots to the dictionary
        for shot in shot_list:
            data_model.add_shot(shot, length)

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
                LayerCreator(None).create_layer_from_template(shot, "master", "master")
                print(f"Master render layer for {shot} has been created.")
