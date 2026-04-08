from __future__ import annotations

import json
import os
from random import randrange

from PySide6.QtWidgets import (
    QDialog
)

try:
    import maya.cmds as mc
    import maya.app.renderSetup.model.renderSetup as render
    import maya.app.renderSetup.model.renderLayer as renderLayer
    import maya.app.renderSetup.model.override as override
    import maya.app.renderSetup.model.container as container
    import pymel.core as pm

except ModuleNotFoundError:  # Local testing
    pass

import utilities as util
from LayerCreator import LayerCreator
from ui.Paths import Paths
from ui.ShotBuilderUI import ShotBuilderUI


class ShotBuilder(QDialog, ShotBuilderUI):
    """A class for the shot building UI dialog.

    This dialog is used to create single or multiple shots in the scene and all the scene elements associated with a
    shot i.e. set, sequence and master render layer. A corresponding camera and light group is created for each shot
    and a color is assigned	to all eligible elements, ie outliner names or render layers, in order to easily
    identify each shot. The class contains all the functions related to creating these elements.
    """
    # pw = ShotManager(parent = None)

    builder_instance = None  # maintain a single instance of the dialog in Production

    def __init__(self, parent):
        super(ShotBuilder, self).__init__(parent)

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
            cls.builder_instance = ShotBuilder(parent)

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

        data_dict = {}

        try:

            with open(self.data_filepath, "r") as data_read:  # Try to open an existing JSON file
                data_dict = json.load(data_read)

        except FileNotFoundError:  # File and/or folder does not exist

            try:

                os.mkdir(self.data_file_directory)  # Try to create a .shot_manager folder

            except FileExistsError:  # Folder exists, but the file is missing

                data_dict = dict()  # Create an empty dictionary

            else:

                data_dict = dict()  # Create an empty dictionary

        except TypeError:  # Scene outside project structure

            print("Create the file inside the pipeline structure.")
            pass

        finally:

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
            layer_list = mc.ls(type="renderSetupLayer")

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
