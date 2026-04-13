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
    QHBoxLayout,
    QSizePolicy,
    QFrame,
    QLineEdit,
    QToolButton,
    QLabel,
    QVBoxLayout,
    QWidget,
    QStyledItemDelegate,
    QStyle
)

from source.util_paths import Paths
import source.util as util

class ShotManagerDelegate(QStyledItemDelegate):
    """Delegate to handle custom widgets (Shot/RenderLayer) in the TreeView."""
    
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        # Determine if we are creating a Shot or a RenderLayer based on model data
        item_type = index.data(Qt.ItemDataRole.UserRole + 1)
        name = index.data(Qt.ItemDataRole.DisplayRole)

        if item_type == "Shot":
            widget = Shot(name)
            widget.setParent(parent)
            # Sync with data
            data = util.shot_data_directory().get(name, {})
            widget.update_shot_widgets(data)
            return widget
        
        elif item_type == "RenderLayer":
            widget = RenderLayer(name)
            widget.setParent(parent)
            # Find parent shot name (stored in UserRole + 2 for layers)
            shot_name = index.data(Qt.ItemDataRole.UserRole + 2)
            widget.update_layer_widgets(shot_name, name)
            return widget

        return super().createEditor(parent, option, index)

    def paint(self, painter, option, index):
        """Override paint to prevent the default text from being drawn."""
        # Do not call super().paint() as it draws the DisplayRole text.
        # Instead, we only draw the selection/hover background if needed.
        painter.save()
        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
        elif option.state & QStyle.StateFlag.State_MouseOver:
            painter.fillRect(option.rect, option.palette.alternateBase())
        painter.restore()

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def sizeHint(self, option, index):
        item_type = index.data(Qt.ItemDataRole.UserRole + 1)
        if item_type == "Shot":
            return QSize(500, 85)
        return QSize(500, 65)
    
    def hasLayers(self, option, index):
        item_type = index.data(Qt.ItemDataRole.UserRole + 1)
        if item_type == "Shot":
            return True
        return False


class CustomWidgetBase(QWidget):
    """Base class for Shot and RenderLayer widgets to handle styling and common logic."""

    def __init__(self, name:str, parent=None):
        super().__init__(parent)

        self.data_file_directory = Paths.return_shot_data_full_filepath()  # Path to data file
        self.style_sheet = util.load_style_sheet()
        self.frame_styles = util.load_frame_style()
        self.name = name
        
        # Set initial styling based on current visibility state
        self.color = self.return_shot_color()
       
    def connect_slots(self):
        
        self.render_button.clicked.connect(lambda: self.toggle_icon(self.render_button))
        self.visibility_button.clicked.connect(lambda: self.toggle_icon(self.visibility_button))
        
    def setup_ui(self):
        """Creates UI elements."""
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        master_layout = QHBoxLayout()
        master_layout.setSpacing(2)
        master_layout.setContentsMargins(5, 2, 5, 2)

        shot_layout = QHBoxLayout()
        shot_layout.setContentsMargins(0, 5, 5, 5)
        shot_layout.setSpacing(1)
        shot_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        aov_layout = QHBoxLayout()
        aov_layout.setSpacing(1)
        aov_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        layer_layout = QHBoxLayout()
        layer_layout.setSpacing(3)
        layer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(3)
        info_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)
        button_layout.setContentsMargins(1, 0, 1, 0)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Size properties

        edit_size_str = QSize(60, 30)
        edit_size_int = QSize(40, 30)
        icon_size = QSize(22, 30)
        aov_icon_size = QSize(20, 20)
        button_size = QSize(18, 30)

        # Frame
       
        self.frame = QFrame(self)
        self.frame.setLayout(master_layout)
        self.main_layout.addWidget(self.frame)
        
         # Name input

        shot_name_validator = QRegularExpressionValidator(QRegularExpression(r'(p\d\d-)?s\d\d\d$'))
        
        shot_pattern = f"{self.name}"
        layer_pattern = shot_pattern + "\\w"
        layer_regex = QRegularExpression(layer_pattern)
        layer_validator = QRegularExpressionValidator(layer_regex)

        self.name_field = QLineEdit("name")
        self.name_field.setFixedSize(edit_size_str)
        self.name_field.setEnabled(False)
        self.name_field.setToolTip("Shot name.")
        self.name_field.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_field.setFont(QFont("Open Sans ExtraBold", 10, 100))
        self.name_field.setText(self.name)
        
        if isinstance(self, Shot):
            self.name_field.setValidator(shot_name_validator)
        elif isinstance(self, RenderLayer):
            self.name_field.setValidator(layer_validator)
            self.name_field.setReadOnly(True)
            self.name_field.setMouseTracking(True)
            self.name_field.installEventFilter(self.name_field)

        self.line = QLabel()
        self.line.setObjectName("line")
        self.line.setFixedSize(2, 50)
        self.line.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.line.setStyleSheet(self.frame_styles["QLabel"].get(self.color))

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
        self.line_02.setStyleSheet(self.frame_styles["QLabel"][self.color])

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
        self.line_03.setStyleSheet(self.frame_styles["QLabel"][self.color])

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

        # Shot only UI
        
        if isinstance(self, Shot):

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
            self.line_04.setStyleSheet(self.frame_styles["QLabel"][self.color])
            
            self.edit_button = QToolButton()
            self.edit_button.setObjectName("edit_button")
            self.edit_button.setIcon(QIcon(Paths.icon("icon_edit.png")))
            self.edit_button.setIconSize(button_size)
            self.edit_button.setToolTip("Edit shot.")
            self.edit_button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        # Shot edit buttons

        self.visibility_button = QToolButton()
        self.visibility_button.setObjectName("visibility_button")
        self.visibility_button.setParent(self.frame)
        self.visibility_button.setCheckable(True)
        self.visibility_button.setIcon(QIcon(Paths.icon("icon_visibility_off.png")))
        self.visibility_button.setIconSize(button_size)
        self.visibility_button.setToolTip("No active layers in this shot.")

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

        shot_layout.addWidget(self.name_field)
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

        if isinstance(self, Shot):
            layer_layout.addWidget(self.layers_icon)
            layer_layout.addWidget(self.layers_label)
            layer_layout.addWidget(self.spacer)
            layer_layout.addWidget(self.spacer)
            button_layout.addWidget(self.line_04)
            
        button_layout.addWidget(self.visibility_button)
        
        if isinstance(self, Shot):
            button_layout.addWidget(self.edit_button)
            
        button_layout.addWidget(self.render_button)
        button_layout.addWidget(self.delete_button)

        master_layout.addLayout(shot_layout)
        master_layout.addLayout(info_layout)
        info_layout.addLayout(aov_layout)
        info_layout.addLayout(layer_layout)
        master_layout.addLayout(button_layout)

    def update_field(self, field_name, field_value):
        """
       Updates the field value in the data dictionary and saves it to the data file.

       Args:
           field_name (str): The name of the field to update.
           field_value (str): The value of the field to update.
       """

        data_dict = util.shot_data_directory()
        
        if isinstance(self, Shot):
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
                
        elif isinstance(self, RenderLayer):
            try:
                self.data_model.update_layer(self.shot_name, self.layer_name, field_name, field_value)
            except Exception as e:
                # Handle the specific exception(s) that may occur during the update
                print(f"Error updating field: {e}")

    @staticmethod
    def toggle_icon(button: QToolButton):
        """
        Toggles the icon based on the checked state of the button.

        Args:
            button (QToolButton): The button to toggle the icon for.
        """

        if not button.isChecked():
            status = "off"
        else:
            status = "on"

        icon, tooltip = util.return_icon_and_tooltip(button.objectName(), status)

        button.setIcon(icon)
        button.setToolTip(tooltip)
    
    def apply_frame_style(self, color: str, frame: QFrame):
        """
        Applies the background stylesheet to the QFrame based on the color key.
        
        Args:
            color (str): The color key found in frame_styles.json
        """
        if hasattr(self, "frame"):
            style = self.frame_styles["QFrame"].get(color, "")
            frame.setStyleSheet(style)

    def toggle_style_frame(self, shot, button, frame):
        """ Reads in the style sheet and applies the correct frame style based on visibility of the shot."""

        data = util.shot_data_directory()
        shot_color = data[shot]["color"]
        active_color = shot_color + "_active"
        
        if button is not None:
            if button.isChecked():
                self.apply_frame_style(active_color, frame)

            else:
                self.apply_frame_style(shot_color, frame)

    def return_shot_color(self):
        """Returns the color assigned to the shot inside the data file.

        Returns:
            str: name of the color
        """
        try:
            color: str = util.shot_data_directory()[self.name].get("color")
            return color
        except KeyError as e:
            try:
                name = self.name[:4]
                color: str = util.shot_data_directory()[name].get("color")
                return color
            except KeyError as e:
                print(f"KeyError: {e}. Assigning default grey color.")
                return "default"


class Shot(CustomWidgetBase):
    """Custom widget representing a shot, subclassed from QWidget for Delegate use."""
    def __init__(self, shot_name, parent=None):
        super().__init__(shot_name, parent)
        
        self.shot_name = shot_name
        self.setObjectName(shot_name)
        
        self.setup_ui()
        self.apply_frame_style(self.color, self.frame)
        
        self.connect_slots()

    def connect_slots(self):
        """Connects signals and slots."""

        self.frame_range_button.clicked.connect(lambda: self.toggle_icon(self.frame_range_button))        
        self.name_field.textEdited.connect(lambda: self.update_field("name", self.name_field.text()))
        self.start.editingFinished.connect(lambda: self.update_field("start", self.start.text()))
        self.end.editingFinished.connect(lambda: self.update_field("end", self.end.text()))
        self.width_input.editingFinished.connect(lambda: self.update_field("width", self.width_input.text()))
        self.height_input.editingFinished.connect(lambda: self.update_field("height", self.height_input.text()))
        self.visibility_button.toggled.connect(lambda: self.toggle_style_frame(self.shot_name, self.visibility_button, self.frame))

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
                    self.start.setObjectName(value + "_start")
                    self.end.setObjectName(value + "_end")
                    self.width_input.setObjectName(value + "_width")
                    self.height_input.setObjectName(value + "_height")
                    self.layers_label.setObjectName(value + "_layers")
                    self.name_field.setText(value)

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

    def return_shot_name(self, widget: QWidget | None):
        """
        Returns the name of the Shot object containing the widget.

        Args:
            widget (QWidget): Widget instance from Shot or RenderLayer.
            None: Shot instance.
        Returns:
            str: Name of the shot.
        """
        if widget is not None:
            return widget.parent().objectName()  # type: ignore # pylance: ignore[reportOptionalMemberAccess]
        return self.shot_name

    def change_aov_icon_from_layers_aov_status(self):
        """Toggles the icon and AOV render mode for the render layer."""

        data = util.shot_data_directory()
        status_set = set()

        b : QToolButton = self.aov_button
        shot = self.shot_name

        # Get AOVs mode for the layer
        layers_list = data[shot].get("render_layers")
        layers_dict = data[shot].get("layers")

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
        """ Saves the data to the data file."""

        try:
            with open(self.data_file_directory, "w") as data_file:
                json.dump(self.data, data_file, indent=4)

        except IOError as e:
            # Handle the case when there is an error writing to the data file
            print(f"Error {e}. Cannot write to data file.")

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
                    shot_dict = self.data.get(shot)
                    render_layers = shot_dict.get("render_layers")
                    
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

    def get_layer_info(self, shot, layer):
        """
        Retrieves the information about the specified layer from the data.

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


class RenderLayer(CustomWidgetBase):
    """Represents a render layer widget, subclassed from QWidget for Delegate use."""
    def __init__(self, layer_name, parent=None):
        super().__init__(layer_name, parent)
        
        self.data_model = RenderLayerDataModel(self.data_file_directory)
        
        self.layer_name = layer_name
        self.shot_name = self.return_shot_name(self)
        print(self.shot_name)
        self.setObjectName(layer_name)
        
        self.setup_ui()
        self.apply_frame_style(self.color, self.frame)
        self.set_line_color()
        
        self.connect_slots()
    
    def connect_slots(self):
        """Connects signals and slots."""

        self.render_button.clicked.connect(lambda: self.render_button.toggle())
        self.render_button.clicked.connect(lambda: self.toggle_icon(self.render_button))
        self.visibility_button.clicked.connect(lambda: self.toggle_icon(self.visibility_button))
        self.visibility_button.toggled.connect(
            lambda: self.toggle_style_frame(self.shot_name, self.visibility_button, self.frame))
        self.aov_button.clicked.connect(lambda: self.aov_button.toggle())
        self.aov_button.toggled.connect(lambda: self.toggle_icon(self.aov_button))
        self.aov_button.clicked.connect(lambda: self.toggle_aov_mode_checked(self.aov_button))
        self.aov_beauty_button.clicked.connect(lambda: self.aov_beauty_button.toggle())
        self.aov_beauty_button.toggled.connect(lambda: self.toggle_icon(self.aov_beauty_button))
        self.aov_utility_button.clicked.connect(lambda: self.aov_utility_button.toggle())
        self.aov_utility_button.toggled.connect(lambda: self.toggle_icon(self.aov_utility_button))

        self.name_field.editingFinished.connect(lambda: self.update_field("name", self.name_field.text()))
        self.name_field.editingFinished.connect(lambda: util.rename_layers(self.layer_name, self.name_field.text()))
        self.start.editingFinished.connect(lambda: self.update_field("start", self.start.text()))
        """self.start.editingFinished.connect(
            lambda: util.edit_overrides(self.layer_name, "start", int(self.start.text()), "defaultRenderGlobals"))"""
        self.end.editingFinished.connect(lambda: self.update_field("end", self.end.text()))
        """self.end.editingFinished.connect(
            lambda: util.edit_overrides(self.layer_name, "end", int(self.end.text()), "defaultRenderGlobals"))"""
    
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
                    self.name_field.setObjectName(value + "_layer")
                    self.start.setObjectName(value + "_start")
                    self.end.setObjectName(value + "_end")
                    self.name_field.setText(value)

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

    def return_layer_name_by_widget(self, widget: QWidget):
        """
        Returns the name of the layer associated with the widget.

        Args:
            widget (QWidget): The widget.

        Returns:
            str: The name of the layer.
        """
        
        children = self.frame.children()
        
        if widget in children:
            return self.layer_name
        return ""

    def return_shot_name(self, widget: QWidget):
        """
        Returns the name of the shot associated with the widget.

        Args:
            widget (QWidget): The widget.

        Returns:
            str: The name of the shot.
        """
        

        parent = widget.parentWidget()
        layer_name = self.layer_name
        
        if parent is not None:
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

        shot_dict = data[self.name]

        shot_start = int(shot_dict["start"])
        shot_end = int(shot_dict["end"])

        layer_start = int(shot_dict["layers"][self.layer_name]["start"])
        layer_end = int(shot_dict["layers"][self.layer_name]["end"])

        if layer_start != shot_start or layer_end != shot_end:
            return False

        return True

    def eventFilter(self, obj, event):
        if obj == self.name_field and event.type() == QEvent.Type.MouseButtonDblClick:
            self.name_field.setReadOnly(False)
            return True
        return super().eventFilter(obj, event)

    def set_line_color(self):
        self.line.setStyleSheet(self.frame_styles["QLabel"][self.color])
        self.line_03.setStyleSheet(self.frame_styles["QLabel"][self.color])
