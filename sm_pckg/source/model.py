"""
Module with DataModel class, which handles all logic
for the data model, like creating, updating or reading 
data from the JSON file. Central source of the data file.
"""
import json
from source import util # pylint: disable=import-error

class DataModel:
    """ Class handling the data model Shot Manager. """

    def __init__(self, data_file_directory):
        """ Initializes the DataModel.
            Args:
                data_file_directory (str): The path to the data file. """

        self.data_file = data_file_directory
        self.data = self.load_data()

    def load_data(self):
        """ Loads the data from the data file.
            Returns:
                dict: The loaded data. """

        with open(self.data_file, encoding="UTF-8", mode="r") as data_file:
            return json.load(data_file)

    def save_data(self):
        """ Saves the data to the data file. """

        try:
            with open(self.data_file, encoding="UTF-8", mode="w") as data_file:
                json.dump(self.data, data_file, indent=4)

        except IOError as e:
            # Handle the case when there is an error writing to the data file
            print(f"Error {e}. Cannot write to data file.")

    def shot_dict_exists(self, shot:str):
        """ Checks if a dictionary entry for the given shot exists.
            Args:
                shot (str): name of the shot
            Returns:
                bool: True if the dictionary entry exists, False otherwise. """

        if self.data_file and self.data and shot in self.data:
            return True
        return False

    def return_shot_dict(self, shot:str):
        """ Checks if a dictionary entry for the given shot exists and 
            returns the dictionary entry.
            Args:
                shot (str): name of the shot
            Returns:
                shot_dict (dict): Shot dictionary."""

        if self.shot_dict_exists(shot):
            return self.data[shot]

        print("Dictionary is empty.")
        return {}

    def update_shot_dict(self, shot:str, field_name:str, field_value):
        """ Updates a specific field value of a shot in the data.
            Args:
                shot (str): The name of the shot.
                field_name (str): The name of the field to update.
                field_value (str | int | layer): The new value of the field. """
        self.data = self.load_data()

        shot_dict = self.return_shot_dict(shot)

        if shot_dict:
            if field_name in ["name", "color"]:
                shot_dict.update({field_name: field_value})
                self.save_data()

            elif field_name in ["start", "end", "width", "height"]:
                shot_dict.update({field_name: int(field_value)})
                self.save_data()

    def add_shot(self, shot_name, length):
        """ Adds a new shot entry to the data. """

        self.data = self.load_data()

        if shot_name in self.data:
            return

        end_frame = 1001 + length - 1
        color = util.get_random_color()

        self.data[shot_name] = {
            "name": shot_name,
            "color": color,
            "start": 1001,
            "end": end_frame,
            "width": 1920,
            "height": 1080,
            "render_layers": [f"{shot_name}master"],
            "layers": {}
        }

        self.save_data()

    def layer_dict_exists(self, shot:str, layer:str):
        """ Checks if a dictionary entry for the given shot and render
            layer exists.
            Args:
                shot (str): name of the shot
                layer (str): name of the layer
            Returns:
                bool: True if the dictionary entry exists, False otherwise. """

        if self.data_file and self.data and shot in self.data:
            layers = self.data[shot].get("render_layers")
            if layers and layer in layers:
                return True
        return False

    def return_layer_dict(self, shot:str, layer:str):
        """ Checks if a dictionary entry for the given shot and render
            layer exists and returns the dictionary entry.
            Args:
                shot (str): name of the shot
                layer (str): name of the layer
            Returns:
                layer_dict (dict): Layer dictionary."""

        if self.layer_dict_exists(shot, layer):
            return self.data[shot]["layers"][layer]

        print("Layer dictionary is empty.")
        return {}

    def update_layer_dict(self, shot:str, layer:str, field_name:str, field_value):
        """ Updates a specific field value of a layer in the data.
            Args:
                shot (str): The name of the shot.
                layer (str): The name of the layer.
                field_name (str): The name of the field to update.
                field_value (str | int | layer): The new value of the field. """

        self.data = self.load_data()
        layer_dict = self.return_layer_dict(shot, layer)

        if layer_dict:

            if field_name == "name":
                layer_dict.update({field_name: field_value})
                self.save_data()

            elif field_name in ["start", "end", "width", "height", "renderable", "AOV mode"]:
                layer_dict.update({field_name: int(field_value)})
                self.save_data()

            elif field_name == "AOVs":
                self.update_aovs(layer_dict, field_value)
                self.save_data()

    def add_layer(self, shot_name, layer_name, start, end):
        """ Adds a new layer entry to a specific shot. """

        self.data = self.load_data()

        if shot_name not in self.data:
            return

        if layer_name not in self.data[shot_name]["render_layers"]:
            self.data[shot_name]["render_layers"].append(layer_name)

        if "layers" not in self.data[shot_name]:
            self.data[shot_name]["layers"] = {}

        self.data[shot_name]["layers"][layer_name] = {
            "name": layer_name,
            "start": int(start),
            "end": int(end),
            "renderable": 1,
            "AOV mode": 0,
            "AOVs": []
        }

        self.save_data()

    def rename_layer(self, shot:str, old_name:str, new_name:str):
        """ Method updates all relevant entries for the layer
            with a new name.
            Args:
                shot (str): Name of the shot.
                old_name (str): Current name of the layer.
                new_name (str): New name of the layer. """

        self.data = self.load_data()
        # Update shot and replace layer name for "render_layers" key
        shot_dict:dict = self.return_shot_dict(shot)
        render_layers:list = shot_dict.get("render_layers", [])

        for i in render_layers:
            if i == old_name:
                index = render_layers.index(i)
                render_layers[index] = f"{new_name}"
                shot_dict.update({"render_layers": render_layers})

        # Update the name in the "layers" dictionary
        layers_dict:dict = shot_dict.get("layers", {})

        try:
            layers_dict[new_name] = layers_dict.pop(old_name)
        except KeyError:
            print("Entry not found.")

        self.save_data()

    def update_aovs(self, layer_dict:dict, field_value:tuple):
        """ Method checks for current AOVs entry.
            Args:
                layer_dict (dict): Dictionary for the layer.
                field_value (tuple): A tuple of AOV and status (on/off). """

        aov, status = field_value

        # Get a list of tuples for [aov, status]
        aov_list: list[tuple] = layer_dict.get("AOVs", [])

        # AOVs on, but missing in dictionary - add to dictionary
        if status and aov not in aov_list:
            aov_list.append(aov)
            layer_dict.update({"AOVs": aov_list})

        # AOVs off and value in dictionary - remove from dictionary
        elif status == 0 and aov in aov_list:
            aov_list.remove(aov)
            layer_dict.update({"AOVs": aov_list})
        # A: AOVs off and missing in dictionary - do nothing
        # B: AOVs on and added to dictionary - do nothing
        else:
            pass
