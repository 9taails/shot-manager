import json

from PySide6.QtCore import (
    QSize,
    Qt,
    QRegularExpression
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
    QLabel,
    QVBoxLayout
)

from CustomQTreeWidgetItem import CustomQTreeWidgetItem
from ui.Paths import Paths
import utilities as util


class Shot(CustomQTreeWidgetItem):
    """
    Custom widget representing a shot.

    Args:
        shot_name (str): The name of the shot.

    Attributes:
        data_file_directory (str): The path to the data file.
        shot_name (str): The name of the shot

    """

    def __init__(self, shot_name: str):
        super().__init__()

        self.data_file_directory = Paths.return_shot_data_full_filepath()

        self.shot_name = shot_name
        self.setup_ui()
        self.__class__ = Shot

        # Connect signals and slots
        self.render_button.clicked.connect(lambda: self.toggle_icon(self.render_button))
        self.visibility_button.clicked.connect(lambda: self.toggle_icon(self.visibility_button))
        self.frame_range_button.clicked.connect(lambda: self.toggle_icon(self.frame_range_button))
        self.change_aov_icon_from_layers_aov_status()

        self.name.textEdited.connect(lambda: self.update_field("name", self.name.text()))
        self.start.editingFinished.connect(lambda: self.update_field("start", self.start.text()))
        self.end.editingFinished.connect(lambda: self.update_field("end", self.end.text()))
        self.width_input.editingFinished.connect(lambda: self.update_field("width", self.width_input.text()))
        self.height_input.editingFinished.connect(lambda: self.update_field("height", self.height_input.text()))
        self.visibility_button.toggled.connect(lambda: self.toggle_style_frame())

    def setup_ui(self):
        """
       Sets up the user interface for the shot widget.
       """

        # Layouts

        master_layout = QHBoxLayout(self)
        master_layout.setSpacing(2)

        shot_layout = QHBoxLayout(self)
        shot_layout.setContentsMargins(-5, 5, 5, 5)
        shot_layout.setSpacing(1)
        shot_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        aov_layout = QHBoxLayout(self)
        aov_layout.setSpacing(1)
        aov_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        layer_layout = QHBoxLayout(self)
        layer_layout.setSpacing(3)
        layer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        info_layout = QVBoxLayout(self)
        info_layout.setSpacing(3)
        info_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        button_layout = QHBoxLayout(self)
        button_layout.setSpacing(5)
        button_layout.setContentsMargins(1, 0, 1, 0)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Size properties

        frame_size = QSize(550, 70)
        edit_size_str = QSize(60, 30)
        edit_size_int = QSize(40, 30)
        size_policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        icon_size = QSize(22, 30)
        aov_icon_size = QSize(20, 20)
        button_size = QSize(18, 30)

        # Frame

        self.frame = QFrame(self)
        self.frame.setMaximumSize(frame_size)
        self.frame.setSizePolicy(size_policy)

        # Shot name input

        shot_name_validator = QRegularExpressionValidator(QRegularExpression(r'(p\d\d-)?s\d\d\d$'))

        self.name = QLineEdit("name", self)
        self.name.setFixedSize(edit_size_str)
        self.name.setValidator(shot_name_validator)
        self.name.setEnabled(False)
        self.name.setToolTip("Shot name.")
        self.name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name.setFont(QFont("Open Sans ExtraBold", 10, 100))

        color = self.return_shot_color()

        self.line = QLabel()
        self.line.setObjectName("line")
        self.line.setFixedSize(2, 50)
        self.line.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.line.setStyleSheet(self.frame_styles["QLabel"][color])

        # Frame range inputs

        self.frame_range_button = QToolButton()
        self.frame_range_button.setChecked(False)
        self.frame_range_button.setObjectName("frame_range_button")
        self.frame_range_button.setIcon(QIcon(Paths.icon("icon_frame_range.png")))
        self.frame_range_button.setIconSize(icon_size)

        number_validator = QIntValidator(0, 20000)

        self.start = QLineEdit("start")
        self.start.setFixedSize(edit_size_int)
        self.start.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.start.setValidator(number_validator)
        self.start.setToolTip("Start frame.")
        self.start.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.separator_01 = QLabel("-")
        self.separator_01.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.end = QLineEdit("end")
        self.end.setFixedSize(edit_size_int)
        self.end.setToolTip("End frame.")
        self.end.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.line_02 = QLabel()
        self.line_02.setObjectName("line")
        self.line_02.setFixedSize(1, 30)
        self.line_02.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.line_02.setStyleSheet(self.frame_styles["QLabel"][color])

        self.spacer = QLabel("")

        # Resolution inputs

        self.resolution_button = QToolButton()
        self.resolution_button.setObjectName("resolution_button")
        self.resolution_button.setIcon(QIcon(Paths.icon("icon_resolution.png")))
        self.resolution_button.setIconSize(icon_size)

        self.width_input = QLineEdit("width_input")
        self.width_input.setFixedSize(edit_size_int)
        self.width_input.setValidator(number_validator)
        self.width_input.setToolTip("Resolution width.")
        self.width_input.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.separator_02 = QLabel("x")
        self.separator_02.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.height_input = QLineEdit("height_input")
        self.height_input.setFixedSize(edit_size_int)
        self.height_input.setValidator(number_validator)
        self.height_input.setToolTip("Resolution height.")
        self.height_input.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.line_03 = QLabel()
        self.line_03.setObjectName("line")
        self.line_03.setFixedSize(1, 30)
        self.line_03.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.line_03.setStyleSheet(self.frame_styles["QLabel"][color])

        # AOVs

        self.aov_button = QToolButton()
        self.aov_button.setObjectName("aov_button")
        self.aov_button.setCheckable(True)
        self.aov_button.setIcon(QIcon(Paths.icon("icon_aov_off.png")))

        self.aov_beauty_button = QToolButton()
        self.aov_beauty_button.setObjectName("aov_beauty_button")
        self.aov_beauty_button.setCheckable(True)
        self.aov_beauty_button.setIcon(QIcon(Paths.icon("icon_aov_beauty_off.png")))
        self.aov_beauty_button.setIconSize(aov_icon_size)
        self.aov_beauty_button.setToolTip("Beauty AOVs")

        self.aov_utility_button = QToolButton()
        self.aov_utility_button.setObjectName("aov_utility_button")
        self.aov_utility_button.setCheckable(True)
        self.aov_utility_button.setIcon(QIcon(Paths.icon("icon_aov_utility_off.png")))
        self.aov_utility_button.setIconSize(aov_icon_size)
        self.aov_utility_button.setToolTip("Utility AOVs")

        # Render layers info

        self.layers_icon = QToolButton()
        self.layers_icon.setObjectName("layers_icon")
        self.layers_icon.setIcon(QIcon(Paths.icon("icon_layers.png")))
        self.layers_icon.setIconSize(icon_size)

        self.layers_label = QLabel()
        self.layers_label.setMinimumSize(QSize(50, 20))
        self.layers_label.setToolTip("Number of existing layers for this shot.")
        self.layers_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.line_04 = QLabel()
        self.line_04.setObjectName("line")
        self.line_04.setFixedSize(1, 30)
        self.line_04.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.line_04.setStyleSheet(self.frame_styles["QLabel"][color])

        # Shot edit buttons

        self.visibility_button = QToolButton()
        self.visibility_button.setObjectName("visibility_button")
        self.visibility_button.setParent(self)
        self.visibility_button.setCheckable(True)
        self.visibility_button.setIcon(QIcon(Paths.icon("icon_visibility_off.png")))
        self.visibility_button.setIconSize(button_size)
        self.visibility_button.setToolTip("No active layers in this shot.")

        self.edit_button = QToolButton()
        self.edit_button.setObjectName("edit_button")
        self.edit_button.setIcon(QIcon(Paths.icon("icon_edit.png")))
        self.edit_button.setIconSize(button_size)
        self.edit_button.setToolTip("Edit shot.")
        self.edit_button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        self.render_button = QToolButton()
        self.render_button.setObjectName("render_button")
        self.render_button.setCheckable(True)
        self.render_button.setIconSize(button_size)
        self.render_button.setToolTip("Renderable status.")

        self.delete_button = QToolButton()
        self.delete_button.setObjectName("delete_button")
        self.delete_button.setIcon(QIcon(Paths.icon("icon_delete.png")))
        self.delete_button.setIconSize(button_size)
        self.delete_button.setToolTip("Delete shot.")

        # Layout widgets

        shot_layout.addWidget(self.name)
        shot_layout.addWidget(self.line)
        shot_layout.addWidget(self.spacer)
        shot_layout.addWidget(self.frame_range_button)
        shot_layout.addWidget(self.start)
        shot_layout.addWidget(self.separator_01)
        shot_layout.addWidget(self.end)
        shot_layout.addWidget(self.line_02)
        shot_layout.addWidget(self.spacer)
        shot_layout.addWidget(self.resolution_button)
        shot_layout.addWidget(self.width_input)
        shot_layout.addWidget(self.separator_02)
        shot_layout.addWidget(self.height_input)
        shot_layout.addWidget(self.line_03)
        shot_layout.addWidget(self.spacer)

        aov_layout.addWidget(self.aov_button)
        aov_layout.addWidget(self.aov_beauty_button)
        aov_layout.addWidget(self.aov_utility_button)

        layer_layout.addWidget(self.layers_icon)
        layer_layout.addWidget(self.layers_label)
        layer_layout.addWidget(self.spacer)
        layer_layout.addWidget(self.spacer)

        button_layout.addWidget(self.line_04)
        button_layout.addWidget(self.visibility_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.render_button)
        button_layout.addWidget(self.delete_button)

        master_layout.addLayout(shot_layout)
        master_layout.addLayout(info_layout)
        info_layout.addLayout(aov_layout)
        info_layout.addLayout(layer_layout)
        master_layout.addLayout(button_layout)

        self.frame.setLayout(master_layout)

        # ---> End layout

    def update_shot_widgets(self, data):
        """Sets the values of all fields from the data dictionary. Dictionary cannot be empty.

        Args:
            data (dict): A dictionary saved out in the JSON file.
        """
        if data:
            for key, value in data.items():

                if key == "name":
                    self.setObjectName(value)
                    self.frame.setObjectName(value)
                    self.name.setObjectName(value + "_shot")
                    self.start.setObjectName(value + "_start")
                    self.end.setObjectName(value + "_end")
                    self.width_input.setObjectName(value + "_width")
                    self.height_input.setObjectName(value + "_height")
                    self.layers_label.setObjectName(value + "_layers")
                    self.name.setText(value)

                elif key == "start":

                    self.start.setText(str(value))

                elif key == "end":
                    self.end.setText(str(value))

                elif key == "width":
                    self.width_input.setText(str(value))

                elif key == "height":
                    self.height_input.setText(str(value))

                elif key == "render_layers":
                    no_layers = len(value)

                    if no_layers == 1:
                        self.layers_label.setText(str(no_layers) + " layer")
                    else:
                        self.layers_label.setText(str(no_layers) + " layers")

    def update_field(self, field_name, field_value):
        """
       Updates the field value in the data dictionary and saves it to the data file.

       Args:
           field_name (str): The name of the field to update.
           field_value (str): The value of the field to update.
       """

        data_dict = util.shot_data_directory()

        try:
            data_dict[self.shot_name].update({
                field_name: int(field_value)
            })
        except ValueError:
            data_dict[self.shot_name].update({
                field_name: field_value
            })

        with open(self.data_file_directory, "w") as data_dump:
            json.dump(data_dict, data_dump, indent=4)

    @staticmethod
    def return_shot_name(widget):
        """
        Returns the name of the Shot object containing the widget.

        Args:
            widget (QWidget): The widget to find the parent Shot object for.

        Returns:
            shot_name (str): The name of the Shot object containing the widget.
        """

        frame_widget = widget.parentWidget()
        shot_widget = frame_widget.parentWidget()
        shot_name = shot_widget.objectName()

        return shot_name

    def return_shot_color(self):
        try:
            data = util.shot_data_directory()
            return data[self.shot_name]["color"]
        except KeyError:
            pass

    def change_aov_icon_from_layers_aov_status(self):
        """Toggles the icon and AOV render mode for the render layer."""

        data = util.shot_data_directory()
        status_set = set()

        b: QToolButton
        b = self.aov_button
        shot = self.shot_name

        # Get AOVs mode for the layer
        layers_list = data[shot]["render_layers"]
        layers_dict = data[shot]["layers"]

        for layer in layers_list:
            status = layers_dict[layer].get("AOV mode")
            status_set.add(status)

        status_list = [s for s in status_set]
        list_len = len(status_list)

        # Set checked state for each button based on the AOVs value
        if list_len == 1:

            if status_list[0] == 0:     # All AOV modes are off
                icon, tooltip = util.return_icon_and_tooltip("aov_button", "off")
                b.setChecked(False)

            else:    # All AOV modes are on
                icon, tooltip = util.return_icon_and_tooltip("aov_button", "on")
                b.setChecked(True)

        else:
            icon, tooltip = util.return_icon_and_tooltip("aov_button", "mid")
            b.setChecked(True)

        b.setIcon(icon)
        b.setToolTip(tooltip)
