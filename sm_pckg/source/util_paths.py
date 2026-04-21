"""
Module with a class containing reference to
resource path used in Shot Manager.
"""
import os
import json
import tempfile

class Path:
    """Class containing reference to resource paths used in Shot Manager."""

    base = os.path.dirname(__file__)		# Path to this folder
    sm_folder = os.path.abspath(os.path.join(base, "..")) # Path to dir with .shot_manager
    temp_files = os.path.join(base, "temp")		# Path to temp folder
    preset_files = os.path.join(sm_folder, "layer_presets")		# Path to preset folder
    icons = os.path.join(sm_folder, "ui", "icons")		# Path to icons folder

    @classmethod
    def return_sm_dir(cls):
        """Returns the path to .shot_manager folder for the current Maya scene.
        Example: C:/maya/projects/default/scenes/.shot_manager
        """

        data_folder = os.path.join(cls.sm_folder, ".shot_manager")
        return data_folder

    @staticmethod
    def get_maya_filename():
        """ Method queries the scene name to find the work folder,
        where .shot_manager will be created. Returns filepath or empty string. """
        # pylint: disable=import-error
        try:
            maya_filepath = mc.file(q=True, sn=True)  # C:/maya/projects/default/scenes/barney.ma
            maya_filename_only = (maya_filepath.split("/")[-1:])[-1]  # barney.ma
            strip_extension = (maya_filename_only.split(".")[:-1])[0]  # barney
            #filename: str = f"{strip_extension}_shot_data.json"
            extension: str = f"{strip_extension}_"
            return extension
        except NameError:
            return ""

    @classmethod
    def return_data_filepath(cls):
        """Returns the full path to the current scene's shot_data file.
        Example: C:/maya/projects/default/scenes/.shot_manager/barney_shot_data.json
        """

        extension = cls.get_maya_filename()

        filename = extension + "shot_data.json"
        data_filepath = os.path.join(cls.base, filename)

        if cls.return_sm_dir():
            data_filepath = os.path.join(cls.return_sm_dir(), filename)

        return data_filepath

    @classmethod
    def ui_file(cls, filename):
        """Returns the full file path to files contained in the ui folder.
        Example: "C:/Users/test/Projects/shotManager_latest/ui/ui_manager.py"

        Args:
            filename = name of the file	with extension, ex. style_sheet.css
        """
        return os.path.join(cls.sm_folder, "ui", filename)

    @classmethod
    def resource_file(cls, filename):
        """Returns the full file path to files contained in the resources folder.
        Example: "C:/Users/test/Projects/shotManager_latest/resources/style_sheet.css"

        Args:
            filename = name of the file	with extension, ex. style_sheet.css
        """
        return os.path.join(cls.sm_folder, "resources", filename)

    @classmethod
    def icon(cls, filename):
        """ Return icon filepath with the given icon name.
        Args:
            filename: name of the icon, ex. renderable_on.png
        """
        return os.path.join(cls.icons, filename)

    @classmethod
    def temp_dir(cls): # pylint: disable=unused-argument
        """ Creates a temporary render layer in the temp folder, before renaming
            and saving the proper render layer file in the correct location.
        """
        return os.path.join(tempfile.gettempdir(), "renderLayerTemp.json")

    @classmethod
    def make_dir(cls):
        """ Checks if the directory exists at a given path.
            Creates the directory if it doesn't. Changes permissions
            on PermissionError for the directory and parent directory.
            Returns:
                bool: True if the directory exists, False otherwise. """

        path = cls.return_sm_dir()

        # Check if directory exists
        if not os.path.exists(path):
            # Directory doesn't exist
            print("Directory doesn't exist.")
            try:
                # Try to create the folder
                os.mkdir(path)
                print("Directory has been created.")

            except PermissionError:
                print("Permission denied.")
                os.chmod(cls.sm_folder, 777)
                os.mkdir(path)
                os.chmod(path, 777)

    @classmethod
    def make_file(cls):
        """ Checks if the file exists at a given path.
            Returns:
                bool: True if the file exists, False otherwise. """

        path = cls.return_data_filepath()
        # Directory exists
        try:
            # Open existing JSON file
            with open(path, encoding="UTF-8", mode="r") as data_read:
                json.load(data_read)
                print(f"Data file exists at {path}")

        # File doesn't exist, create an empty dictionary
        except FileNotFoundError:
            print("Data file is missing. Creating a new one...")
            empty_file = {}
            # Create a new file from the empty dictionary
            with open(path, encoding="UTF-8", mode="w") as data_write:
                json.dump(empty_file, data_write, indent=4)
                print(f"Data file created at {path}")

    @classmethod
    def remove_file(cls):
        """ Method for removing the file in case of wrong
            file formatting or decoding error. """

        path = cls.return_data_filepath()

        try:
            os.remove(path)
            print("File deleted successfully.")

        except OSError as e:
            print(f"Error deleting the file: {e}. "\
                "Defaulting to root directory.")

        else:
            # Create an empty dictionary
            empty_file = {}

            # Create a new file from the empty dictionary
            with open(cls.base, encoding="UTF-8", mode="w") as data_write:
                json.dump(empty_file, data_write, indent=4)
                print("File with an empty dictionary has been "
                  f"created in {cls.base}.")

    @classmethod
    def default_path(cls):
        """ Returns default path in the Documents folder. """

        doc_path = os.path.expanduser("~\\OneDrive\\Documents\\shot_data.json")

        with open(doc_path, encoding="UTF-8", mode="w") as data_write:
            json.dump({}, data_write, indent=4)
            print(f"Data file created at {doc_path}")
        return doc_path
