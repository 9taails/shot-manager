import json

from PySide6.QtCore import (
    QSize,
    Qt,
    QRegularExpression,
    QEvent
)
from PySide6.QtGui import (
    QIcon,
    QRegularExpressionValidator,
    QIntValidator,
    QFont
)
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QSizePolicy,
    QFrame,
    QLineEdit,
    QToolButton,
    QLabel
)

from CustomQTreeWidgetItem import CustomQTreeWidgetItem
from ShotManager.ui.Paths import Paths
import utilities as util


class RenderLayerDataModel:
    def __init__(self, data_file_directory):
        """
        Initializes the RenderLayerDataModel.

        Args:
            data_file_directory (str): The path to the data file.
        """

        self.data_file_directory = data_file_directory
        self.data = self.load_data()

    def load_data(self):
        """
        Loads the data from the data file.

        Returns:
            dict: The loaded data.
        """

        with open(self.data_file_directory) as data_file:
            return json.load(data_file)

    def save_data(self):
        """
        Saves the data to the data file.
        """

        try:

            with open(self.data_file_directory, "w") as data_file:
                json.dump(self.data, data_file, indent=4)

        except IOError:
            # Handle the case when there is an error writing to the data file
            print("Error writing to data file.")

    def update_layer(self, shot, layer, field_name, field_value):
        """
        Updates a specific field value of a layer in the data.

        Args:
            shot (str): The name of the shot.
            layer (str): The name of the layer.
            field_name (str): The name of the field to update.
            field_value (str | int | layer): The new value of the field.
        """

        if shot in self.data and "layers" in self.data[shot] and layer in self.data[shot]["layers"]:

            layer_dict = self.data[shot]["layers"][layer]
            try:  # Changing start or end

                layer_dict.update({field_name: int(field_value)})
                self.save_data()

            except ValueError:  # Changing the name of the layer

                if field_name == "name":

                    layer_dict.update({field_name: field_value})

                    # Update the name in the render layers string
                    shot_dict = self.data[shot]
                    render_layers = shot_dict["render_layers"]
                    for i in render_layers:
                        if i == layer:
                            index = render_layers.index(i)
                            render_layers[index] = field_value
                            shot_dict["render_layers"] = render_layers

                    # Update the name in the layers dictionary
                    layers_dict = shot_dict["layers"]
                    layers_dict[field_value] = layers_dict.pop(layer)  # Replace the shot name in the .json

                elif field_name == "AOV mode":

                    layer_dict.update({field_name: field_value})

            except TypeError:  # For Active AOVs, field_value is a tuple

                value, status = field_value

                aov_list = layer_dict.get(field_name)

                # Any old files will have a wrong value type, so replace them with an empty list
                if isinstance(aov_list, str) or isinstance(aov_list, int) or aov_list is None:
                    aov_list = []
                    layer_dict.update({field_name: aov_list})

                # AOVs on and added to dictionary - do nothing
                if status and value in aov_list:
                    pass

                # AOVs on, but missing in dictionary - add to dictionary
                elif status and value not in aov_list:
                    aov_list.append(value)
                    layer_dict.update({field_name: aov_list})

                # AOVs off and missing in dictionary - do nothing
                elif status == 0 and value not in aov_list:
                    pass

                # AOVs off and value in dictionary - remove from dictionary
                elif status == 0 and value in aov_list:
                    aov_list.remove(value)
                    layer_dict.update({field_name: aov_list})

            self.save_data()

        else:
            # Handle the case when the layer does not exist in the data
            print("Layer or shot not found.")

    def get_layer_info(self, shot, layer):
        """
        Retrieves the information of a layer.

        Args:
            shot (str): The name of the shot.
            layer (str): The name of the layer.

        Returns:
            dict: The layer information.
        """

        data = self.load_data()

        if shot in data and "layers" in data[shot] and layer in data[shot]["layers"]:

            return data[shot]["layers"][layer]

        else:
            # Handle the case when the shot or layer does not exist in the data
            print("Shot or layer not found.")
            return {}


class RenderLayer(CustomQTreeWidgetItem):
    """
    Represents a render layer widget.

    Args:
        layer_name (str): The name of the render layer.
    """

    def __init__(self, layer_name):
        super().__init__()

        self.data_file_directory = Paths.return_shot_data_full_filepath()  # Path to data file
        self.layer_name = layer_name
        self.__class__ = RenderLayer
        self.shot_name = self.layer_name[:4]
        self.data_model = RenderLayerDataModel(self.data_file_directory)
        self.setup_ui()

        # Connect signals and slots
        self.render_button.clicked.connect(lambda: self.render_button.toggle())
        self.render_button.clicked.connect(lambda: self.toggle_icon(self.render_button))
        self.visibility_button.clicked.connect(lambda: self.toggle_icon(self.visibility_button))
        self.visibility_button.toggled.connect(lambda: self.toggle_style_frame())
        self.aov_button.clicked.connect(lambda: self.aov_button.toggle())
        self.aov_button.toggled.connect(lambda: self.toggle_icon(self.aov_button))
        self.aov_button.clicked.connect(lambda: self.toggle_aov_mode_checked(self.aov_button))
        self.aov_beauty_button.clicked.connect(lambda: self.aov_beauty_button.toggle())
        self.aov_beauty_button.toggled.connect(lambda: self.toggle_icon(self.aov_beauty_button))
        self.aov_utility_button.clicked.connect(lambda: self.aov_utility_button.toggle())
        self.aov_utility_button.toggled.connect(lambda: self.toggle_icon(self.aov_utility_button))

        self.name.editingFinished.connect(lambda: self.update_field("name", self.name.text()))
        self.name.editingFinished.connect(lambda: util.rename_layers(self.layer_name, self.name.text()))
        self.start.editingFinished.connect(
            lambda: util.edit_overrides(layer_name, "start", int(self.start.text()), "defaultRenderGlobals"))
        self.end.editingFinished.connect(
            lambda: util.edit_overrides(layer_name, "end", int(self.end.text()), "defaultRenderGlobals"))

    def setup_ui(self):
        """
        Sets up the user interface for the render layer widget.
        """
        # Layouts

        master_layout = QHBoxLayout(self)

        layer_layout = QHBoxLayout(self)
        layer_layout.setContentsMargins(-5, 5, 5, 5)
        layer_layout.setSpacing(2)
        layer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        aov_layout = QHBoxLayout(self)
        aov_layout.setSpacing(1)
        aov_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        button_layout = QHBoxLayout(self)
        button_layout.setContentsMargins(-5, 0, 5, 0)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Size properties

        frame_size = QSize(520, 55)
        edit_str_size = QSize(130, 20)
        edit_int_size = QSize(40, 20)
        size_policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        icon_size = QSize(15, 20)
        aov_icon_size = QSize(13, 13)
        button_size = QSize(18, 20)

        # Frame

        self.frame = QFrame(self)
        self.frame.setMaximumSize(frame_size)
        self.frame.setSizePolicy(size_policy)

        # Shot name input

        self.name = QLineEdit("name", self)
        self.name.setMinimumSize(edit_str_size)
        self.name.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.name.setReadOnly(True)
        self.name.setMouseTracking(True)
        self.name.installEventFilter(self)
        self.name.setFont(QFont("Open Sans Bold", 8, 100))
        self.name.setToolTip("Layer name")

        shot_pattern = f"{self.shot_name}"
        layer_pattern = shot_pattern + "\\w"
        layer_regex = QRegularExpression(layer_pattern)
        layer_validator = QRegularExpressionValidator(layer_regex)
        self.name.setValidator(layer_validator)

        self.line = QLabel()
        self.line.setObjectName("line")
        self.line.setFixedSize(2, 50)
        self.line.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # Frame range inputs

        self.frame_range_button = QToolButton(self)
        self.frame_range_button.setObjectName("frame_range_button")
        self.frame_range_button.setCheckable(True)
        self.frame_range_button.setIconSize(icon_size)
        self.frame_range_button.setIcon(QIcon(Paths.icon("icon_frame_range.png")))

        number_validator = QIntValidator(0, 20000)

        self.start = QLineEdit("start", self)
        self.start.setMinimumSize(edit_int_size)
        self.start.setSizePolicy(size_policy)
        self.start.setValidator(number_validator)
        self.start.setToolTip("Layer start frame")
        self.start.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.separator_01 = QLabel("-")
        self.separator_01.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.end = QLineEdit("end", self)
        self.end.setMinimumSize(edit_int_size)
        self.end.setSizePolicy(size_policy)
        # self.end.setValidator(number_validator)
        self.end.setToolTip("Layer end frame")
        self.end.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # AOVs

        self.aov_button = QToolButton(self)
        self.aov_button.setObjectName("aov_button")
        self.aov_button.setCheckable(True)
        icon, tooltip = util.return_icon_and_tooltip("aov_button", "off")
        self.aov_button.setIcon(icon)
        self.aov_button.setToolTip(tooltip)

        self.aov_beauty_button = QToolButton(self)
        self.aov_beauty_button.setObjectName("aov_beauty_button")
        self.aov_beauty_button.setCheckable(True)
        icon_1, tooltip_1 = util.return_icon_and_tooltip("aov_beauty_button", "on")
        self.aov_beauty_button.setIcon(icon_1)
        self.aov_beauty_button.setToolTip(tooltip_1)
        self.aov_beauty_button.setIconSize(aov_icon_size)

        self.aov_utility_button = QToolButton(self)
        self.aov_utility_button.setObjectName("aov_utility_button")
        self.aov_utility_button.setCheckable(True)
        icon_2, tooltip_2 = util.return_icon_and_tooltip("aov_utility_button", "on")
        self.aov_utility_button.setIcon(icon_2)
        self.aov_utility_button.setIconSize(aov_icon_size)
        self.aov_utility_button.setToolTip(tooltip_2)

        self.spacer = QLabel("")
        self.spacer.setFixedSize(10, 20)

        self.spacer_02 = QLabel("")
        self.spacer_02.setFixedSize(50, 20)

        self.line_03 = QLabel()
        self.line_03.setObjectName("line")
        self.line_03.setFixedSize(1, 30)
        self.line_03.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Shot edit buttons

        self.visibility_button = QToolButton(self)
        self.visibility_button.setObjectName("visibility_button")
        self.visibility_button.setCheckable(True)
        self.visibility_button.setIconSize(button_size)
        self.visibility_button.setIcon(QIcon(Paths.icon("icon_visibility_off.png")))
        self.visibility_button.setToolTip("Set " + f"{self.layer_name}" + " as active layer")

        self.render_button = QToolButton(self)
        self.render_button.setObjectName("render_button")
        self.render_button.setCheckable(True)
        self.render_button.setIcon(QIcon(Paths.icon("icon_renderable_green.png")))
        self.render_button.setIconSize(button_size)

        self.delete_button = QToolButton(self)
        self.delete_button.setObjectName("delete_button")
        self.delete_button.setIcon(QIcon(Paths.icon("icon_delete.png")))
        self.delete_button.setIconSize(button_size)

        # Layout widgets

        layer_layout.addWidget(self.name)
        layer_layout.addWidget(self.line)
        layer_layout.addWidget(self.spacer)
        layer_layout.addWidget(self.frame_range_button)
        layer_layout.addWidget(self.start)
        layer_layout.addWidget(self.separator_01)
        layer_layout.addWidget(self.end)
        layer_layout.addWidget(self.spacer)

        # aov_layout.addWidget(self.line_02)
        aov_layout.addWidget(self.aov_button)
        aov_layout.addWidget(self.aov_beauty_button)
        aov_layout.addWidget(self.aov_utility_button)
        aov_layout.addWidget(self.spacer)

        button_layout.addWidget(self.line_03)
        button_layout.addWidget(self.visibility_button)
        button_layout.addWidget(self.render_button)
        button_layout.addWidget(self.delete_button)

        master_layout.addLayout(layer_layout)
        master_layout.addLayout(aov_layout)
        master_layout.addLayout(button_layout)

        self.frame.setLayout(master_layout)

        # ---> End layout

    def update_layer_widgets(self, shot, layer):
        """
        Updates the render layer widget with the layer information from JSON file.

        Args:
            shot (str): The name of the shot.
            layer (str): The name of the layer.
        """

        data = util.shot_data_directory()

        try:
            layer_dict = data[shot]["layers"][layer]

        except KeyError:
            layer_dict = data[shot]

        if data and layer_dict:

            renderable = layer_dict.get("renderable")
            aov_mode = layer_dict.get("AOV mode")
            aovs = layer_dict.get("AOVs")

            for key, value in layer_dict.items():

                if key == "name":
                    self.setObjectName(value)
                    self.frame.setObjectName(value)
                    self.name.setObjectName(value + "_layer")
                    self.start.setObjectName(value + "_start")
                    self.end.setObjectName(value + "_end")
                    self.name.setText(value)

                if key == "start":

                    self.start.setText(str(value))
                    self.update_field("start", str(value))

                if key == "end":
                    self.end.setText(str(value))
                    self.update_field("end", str(value))

            # Check renderable status and set .isChecked for button and correct icon
            if renderable is not None:
                if renderable:
                    icon, tooltip = util.return_icon_and_tooltip("render_button", "on")
                    self.render_button.setChecked(True)

                else:
                    icon, tooltip = util.return_icon_and_tooltip("render_button", "off")
                    self.render_button.setChecked(False)

                self.render_button.setIcon(icon)
                self.render_button.setToolTip(tooltip)

            # Check for the AOV mode key and value. Set .isChecked for button and correct icon.
            if aov_mode is not None:
                if aov_mode == 1:
                    icon, tooltip = util.return_icon_and_tooltip("aov_button", "on")

                else:
                    icon, tooltip = util.return_icon_and_tooltip("aov_button", "off")

                self.aov_button.setToolTip(tooltip)
                self.aov_button.setIcon(icon)

            # Check for the AOV mode key and value. Set .isChecked for button and correct icon.

            if aovs is not None:
                if isinstance(aovs, int):
                    aov_list = ([], 0)
                    RenderLayerDataModel(self.data_file_directory).update_layer(shot, layer, "AOVs", aov_list)

                else:

                    if "beauty" in aovs:

                        icon_beauty, tooltip_beauty = util.return_icon_and_tooltip("aov_beauty_button", "on")
                        self.aov_beauty_button.setChecked(True)
                        self.aov_beauty_button.setIcon(icon_beauty)
                        self.aov_beauty_button.setToolTip(tooltip_beauty)

                    elif "utility" in aovs:

                        icon_utility, tooltip_utility = util.return_icon_and_tooltip("aov_utility_button", "on")
                        self.aov_utility_button.setChecked(True)
                        self.aov_utility_button.setIcon(icon_utility)
                        self.aov_utility_button.setToolTip(tooltip_utility)

    def update_field(self, field_name, field_value):
        try:
            self.data_model.update_layer(self.shot_name, self.layer_name, field_name, field_value)
        except Exception as e:
            # Handle the specific exception(s) that may occur during the update
            print(f"Error updating field: {e}")

    @staticmethod
    def return_layer_name(widget: QWidget):
        """
        Returns the name of the layer associated with the widget.

        Args:
            widget (QWidget): The widget.

        Returns:
            str: The name of the layer.
        """

        frame_widget = widget.parentWidget()
        parent = frame_widget.parentWidget()
        layer_name = parent.objectName()

        return layer_name

    def return_shot_name(self, widget: QWidget):
        """
        Returns the name of the shot associated with the widget.

        Args:
            widget (QWidget): The widget.

        Returns:
            str: The name of the shot.
        """

        parent = self.return_parent(widget)
        layer_name = parent.objectName()
        shot_name = layer_name[:4]

        return shot_name

    def toggle_range_icon(self, button: QToolButton):

        status = self.compare_range_values()

        if not status:
            icon, tooltip = util.return_icon_and_tooltip("frame_range_button", "on")
            button.setChecked(True)

        else:
            icon, tooltip = util.return_icon_and_tooltip("frame_range_button", "off")
            button.setChecked(False)

        button.setIcon(icon)
        button.setToolTip(tooltip)

    @staticmethod
    def toggle_aov_mode_checked(button: QToolButton):

        if button.isChecked():
            button.setChecked(False)

        else:
            button.setChecked(True)

    def compare_range_values(self):
        """ Checks start and end frame for the layer and compares them to the shot frame range. Toggles the icon based
            on the result of comparison.
        """

        data = self.data_model.load_data()

        shot_name = self.shot_name

        shot_dict = data[shot_name]

        shot_start = int(shot_dict["start"])
        shot_end = int(shot_dict["end"])

        layer_start = int(shot_dict["layers"][self.layer_name]["start"])
        layer_end = int(shot_dict["layers"][self.layer_name]["end"])

        if layer_start != shot_start or layer_end != shot_end:
            return False

        else:
            return True

    def eventFilter(self, obj, event):
        if obj == self.name and event.type() == QEvent.Type.MouseButtonDblClick:
            self.name.setReadOnly(False)
            return True
        return super().eventFilter(obj, event)

    def return_shot_color(self):
        try:
            data = util.shot_data_directory()
            return data[self.shot_name]["color"]
        except KeyError:
            pass

    def set_line_color(self):
        color = self.return_shot_color()
        self.line.setStyleSheet(self.frame_styles["QLabel"][color])
        self.line_03.setStyleSheet(self.frame_styles["QLabel"][color])
