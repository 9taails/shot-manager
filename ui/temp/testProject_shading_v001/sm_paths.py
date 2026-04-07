import os
try:
	import maya.cmds as mc
except ModuleNotFoundError:
	pass
from datetime import datetime
import tempfile


class Paths:
	"""Class containing reference to resource paths used in Shot Manager."""

	base = os.path.dirname(__file__)		# Path to this folder
	sm_folder = os.path.abspath(os.path.join(base, ".."))  	# Path to .shot_manager directory
	temp_files = os.path.join(base, "temp")		# Path to temp folder
	preset_files = os.path.join(sm_folder, "layer_presets")		# Path to preset folder
	icons = os.path.join(base, "icons")		# Path to icons folder

	@classmethod
	def get_data_folder(cls):
		"""Returns the path to .shot_manager folder for the current Maya scene."""

		data_folder = os.path.join(cls.sm_folder, ".shot_manager")

		return data_folder

	# File loaders.

	@classmethod
	def ui_file(cls, filename):
		"""Returns the full file path to files contained in the ui folder.
		Example: "C:/Users/test/Projects/shotManager_latest/ui/style_sheet.css"

		Args:
			filename = name of the file	with extension, ex. style_sheet.css
		"""
		return os.path.join(cls.base, filename)

	@classmethod
	def icon(cls, filename):
		return os.path.join(cls.icons, filename)

	@classmethod
	def data_dir(cls, filename):
		"""
		"""
		if cls.get_data_folder():

			data_folder = cls.get_data_folder()

			return os.path.join(data_folder, filename)

		return None

	@classmethod
	def current_file_name(cls):
		"""Returns the name of the shot data file for the current scene."""
		try:
			maya_filepath = mc.file(q=True, sn=True)  # C:/maya/projects/default/scenes/barney.ma
			maya_filename_only = (maya_filepath.split("/")[-1:])[-1]  # barney.ma
			strip_extension = (maya_filename_only.split(".")[:-1])[0]  # barney
			file_name = f"{strip_extension}_shot_data.json"

		except NameError:		# Maya is not loaded
			file_name = "shot_data.json"

		return file_name

	@classmethod
	def temp_dir(cls):
		return os.path.join(tempfile.gettempdir(), "renderLayerTemp.json")

