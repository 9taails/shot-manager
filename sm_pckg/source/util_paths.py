"""
Module with a class containing reference to
resource path used in Shot Manager.
"""
import os
try:
    import maya.cmds as mc
except ModuleNotFoundError:
    pass
import tempfile


class Path:
    """Class containing reference to resource path used in Shot Manager."""

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

    @classmethod
    def return_data_filepath(cls):
        """Returns the full path to the current scene's shot_data file.
        Example: C:/maya/projects/default/scenes/.shot_manager/barney_shot_data.json
        """

        try:
            maya_filepath = mc.file(q=True, sn=True)  # C:/maya/projects/default/scenes/barney.ma
            maya_filename_only = (maya_filepath.split("/")[-1:])[-1]  # barney.ma
            strip_extension = (maya_filename_only.split(".")[:-1])[0]  # barney
            file_name = f"{strip_extension}_shot_data.json"

        except NameError:  # Maya is not loaded
            file_name = "shot_data.json"

        data_filepath = os.path.join(cls.base, file_name)

        if cls.return_sm_dir():
            data_filepath = os.path.join(cls.return_sm_dir(), file_name)

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
