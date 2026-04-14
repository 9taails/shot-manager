"""
Module containing class definitions for custom widgets
used as part of model-view architecture inside the Shot Manager.
- Custom base class (subclassed from QWidget), Shot and RenderLayer
widgets (subclassed from the custom base) and the StyledItemDelegate.
The module also holds the model logic class for the RenderLayer.
"""

import json

# pylint: disable=no-name-in-module,import-error
from PySide6.QtCore import (
    QSize,
    Qt,
    QEvent
)

from PySide6.QtWidgets import (
    QFrame,
    QToolButton,
    QWidget,
    QStyledItemDelegate,
    QStyle
)

from source.util_paths import Paths
from source import util
from sm_pckg.ui.ui_widgets import UI

class ShotManagerDelegate(QStyledItemDelegate):
    """ Delegate to handle custom widgets (Shot/RenderLayer) in the TreeView. """
    # pylint: disable=invalid-name,unused-argument,useless-parent-delegation
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        """ Creates the editor responsible for drawing the widget delegate.
            Determines the type to be created (Shot, RenderLayer) based 
            on model data.
            Args:
                parent (QWidget): Instance of parent widget.
                option (QStyleOptionViewItem): Defines the style to be drawn.
                index (QModelIndex): Index of the widget in the model view.
            Returns:
                QWidget: Instance of Shot or RenderLayer. """

        item_type = index.data(Qt.ItemDataRole.UserRole + 1)
        name = index.data(Qt.ItemDataRole.DisplayRole)

        if item_type == "Shot":
            widget = Shot(name)
            widget.setParent(parent)
            # Sync with data
            data = util.shot_data_directory().get(name, {})
            widget.update_shot_widgets(data)
            return widget

        if item_type == "RenderLayer":
            widget = RenderLayer(name)
            widget.setParent(parent)
            # Find parent shot name (stored in UserRole + 2 for layers)
            shot_name = index.data(Qt.ItemDataRole.UserRole + 2)
            widget.update_layer_widgets(shot_name, name)
            return widget

        return super().createEditor(parent, option, index)

    def paint(self, painter, option, index):
        """ Override paint to prevent the default text from being drawn.
            Args:
                painter (QPainter): Instance of QPainter.
                option (QStyleOptionViewItem): Defines the style to be drawn.
                index (QModelIndex): Index of the widget in the model view. """

        # Draws the selection/hover background if needed.
        painter.save()
        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
        elif option.state & QStyle.StateFlag.State_MouseOver:
            painter.fillRect(option.rect, option.palette.alternateBase())
        painter.restore()

    def updateEditorGeometry(self, editor, option, index):
        """ Updates the editor geometry.
            Args:
                editor (QEditor): Instance of the editor.
                option (QStyleOptionViewItem): Defines the style to be drawn.
                index (QModelIndex): Index of the widget in the model view. """

        editor.setGeometry(option.rect)

    def sizeHint(self, option, index):  # pylint: disable=invalid-name,unused-argument
        """ Returns the size for Shot and RenderLayer widgets.
            Args:
                option (QStyleOptionViewItem): Defines the style to be drawn.
                index (QModelIndex): Index of the widget in the model view.
            Returns:
                QSize: Tuple (width, height). """

        item_type = index.data(Qt.ItemDataRole.UserRole + 1)
        if item_type == "Shot":
            return QSize(500, 85)
        return QSize(500, 65)


class CustomWidgetBase(QWidget):
    """ Base class for Shot and RenderLayer widgets to handle styling and common logic. """
    # pylint: disable=attribute-defined-outside-init
    def __init__(self, name:str, parent=None):
        super().__init__(parent)

        self.data_file_directory = Paths.return_shot_data_full_filepath()  # Path to data file
        self.name = name
        self.color = self.return_shot_color()
        self.ui = UI(name, self.color, self)


    def connect_slots(self):
        """ Connects signals and slots. """

        self.ui.render_button.clicked.connect(lambda: self.toggle_icon(self.ui.render_button))
        self.ui.visibility_button.clicked.connect(
            lambda: self.toggle_icon(self.ui.visibility_button))

    def update_field(self, field_name, field_value):
        """ Updates the field value in the data dictionary and saves it to the data file.
            Args:
                field_name (str): The name of the field to update.
                field_value (str): The value of the field to update. """

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

            with open(self.data_file_directory, encoding="UTF-8", mode="w") as data_dump:
                json.dump(data_dict, data_dump, indent=4)

        elif isinstance(self, RenderLayer):
            try:
                self.data_model.update_layer(
                    self.shot_name, self.layer_name, field_name, field_value)
            except Exception as e:
                # Handle the specific exception(s) that may occur during the update
                print(f"Error updating field: {e}")

    def toggle_icon(self, button: QToolButton):
        """ Toggles the icon based on the checked state of the button.
            Args:
                button (QToolButton): The button to toggle the icon for. """
        if isinstance(button, QToolButton):
            if not button.isChecked():
                status = "off"
            else:
                status = "on"

            icon, tooltip = util.return_icon_tooltip(button.objectName(), status)

            button.setIcon(icon)
            button.setToolTip(tooltip)

    def apply_frame_style(self, color: str, frame: QFrame):
        """ Applies the background stylesheet to the QFrame based on the color key.
            Args:
                color (str): The color key found in frame_styles.json.
                frame (QFrame): The frame to apply the style to. """

        style = self.ui.frame_styles["QFrame"].get(color, "")
        frame.setStyleSheet(style)

    def toggle_style_frame(self, shot:str, button:QToolButton, frame:QFrame):
        """ Reads in the style sheet and applies the correct frame style based
            on visibility of the shot. """

        data = util.shot_data_directory()
        shot_color = data[shot]["color"]
        active_color = shot_color + "_active"

        if button is not None:
            if button.isChecked():
                self.apply_frame_style(active_color, frame)
            else:
                self.apply_frame_style(shot_color, frame)

    def return_shot_color(self):
        """ Returns the color assigned to the shot inside the data file. """

        try:
            color: str = util.shot_data_directory()[self.name].get("color")
            return color
        except KeyError:
            try:
                name = self.name[:4]
                color: str = util.shot_data_directory()[name].get("color")
                return color
            except KeyError as e:
                print(f"KeyError: {e}. Assigning default grey color.")
                return "default"


class Shot(CustomWidgetBase):
    """ Custom widget representing a shot, subclassed from QWidget for Delegate use. """
    def __init__(self, shot_name, parent=None):
        super().__init__(shot_name, parent)

        self.shot_name = shot_name
        self.setObjectName(shot_name)

        self.ui.setup_shot_ui()
        self.apply_frame_style(self.color, self.ui.frame)

        self.connect_slots()

    def connect_slots(self):
        """ Connects signals and slots. """
        super().connect_slots()

        self.ui.frame_range_button.clicked.connect(
            lambda: self.toggle_icon(self.ui.frame_range_button))
        self.ui.name_field.textEdited.connect(
            lambda: self.update_field("name", self.ui.name_field.text()))
        self.ui.start.editingFinished.connect(
            lambda: self.update_field("start", self.ui.start.text()))
        self.ui.end.editingFinished.connect(
            lambda: self.update_field("end", self.ui.end.text()))
        self.ui.width_input.editingFinished.connect(
            lambda: self.update_field("width", self.ui.width_input.text()))
        self.ui.height_input.editingFinished.connect(
            lambda: self.update_field("height", self.ui.height_input.text()))
        self.ui.visibility_button.toggled.connect(
            lambda: self.toggle_style_frame(self.shot_name,
                                            self.ui.visibility_button,
                                            self.ui.frame))

    def update_shot_widgets(self, data):
        """ Sets the values of all fields from the data dictionary. Dictionary cannot be empty.
            Args:
                data (dict): A dictionary saved out in the JSON file. """

        if data:
            for key, value in data.items():

                if key == "name":
                    self.setObjectName(value)
                    self.ui.frame.setObjectName(value)
                    self.ui.start.setObjectName(value + "_start")
                    self.ui.end.setObjectName(value + "_end")
                    self.ui.width_input.setObjectName(value + "_width")
                    self.ui.height_input.setObjectName(value + "_height")
                    self.ui.layers_label.setObjectName(value + "_layers")
                    self.ui.name_field.setText(value)

                elif key == "start":

                    self.ui.start.setText(str(value))

                elif key == "end":
                    self.ui.end.setText(str(value))

                elif key == "width":
                    self.ui.width_input.setText(str(value))

                elif key == "height":
                    self.ui.height_input.setText(str(value))

                elif key == "render_layers":
                    no_layers = len(value)

                    if no_layers == 1:
                        self.ui.layers_label.setText(str(no_layers) + " layer")
                    else:
                        self.ui.layers_label.setText(str(no_layers) + " layers")

    def return_shot_name(self, widget: QWidget | None):
        """ Returns the name of the Shot object containing the widget.
            Args:
                widget (QWidget): Widget instance from Shot or RenderLayer.
                None: Shot instance.
            Returns:
                str: Name of the shot. """

        if widget is not None:
            return widget.parent().objectName() # type: ignore
        return self.shot_name

    def sync_shot_aovmode(self):
        """ Checks the AOV mode entry in the JSON dictionary, for all layers
        belonging to the Shot. Toggles the AOV render mode icon for the 
        Shot. """

        # Retrieve JSON data and create an empty set
        # AOV mode can only have 3 possible values; 0, 1, 2.
        # Since sets cannot have more than one same element,
        # the resulting set will have only 3 elements, regardless
        # of bhow many render layers there are.

        data = util.shot_data_directory()
        status_set = set()

        # Get the correct Shot button instance
        b : QToolButton = self.ui.aov_button

        # Get AOVs mode for the layer
        layers_list = data[self.shot_name].get("render_layers")
        layers_dict = data[self.shot_name].get("layers")

        for layer in layers_list:
            status = layers_dict[layer].get("AOV mode")
            status_set.add(status)

        list_len = len(list(status_set))

        # Set checked state for each button based on the AOVs value
        if list_len == 1:

            if list(status_set)[0] == 0:     # All AOV modes are off
                icon, tooltip = util.return_icon_tooltip("aov_button", "off")
                b.setChecked(False)

            else:    # All AOV modes are on
                icon, tooltip = util.return_icon_tooltip("aov_button", "on")
                b.setChecked(True)

        else:
            icon, tooltip = util.return_icon_tooltip("aov_button", "mid")
            b.setChecked(True)

        b.setIcon(icon)
        b.setToolTip(tooltip)


class RenderLayerDataModel:
    """ Class handling the data model for RenderLayer. """

    def __init__(self, data_file_directory):
        """ Initializes the RenderLayerDataModel.
            Args:
                data_file_directory (str): The path to the data file. """

        self.data_file_directory = data_file_directory
        self.data = self.load_data()

    def load_data(self):
        """ Loads the data from the data file.
            Returns:
                dict: The loaded data. """

        with open(self.data_file_directory, encoding="UTF-8", mode="r") as data_file:
            return json.load(data_file)

    def save_data(self):
        """ Saves the data to the data file. """

        try:
            with open(self.data_file_directory, encoding="UTF-8", mode="w") as data_file:
                json.dump(self.data, data_file, indent=4)

        except IOError as e:
            # Handle the case when there is an error writing to the data file
            print(f"Error {e}. Cannot write to data file.")

    def layer_dict_exists(self, shot:str, layer:str):
        """ Checks if a dictionary entry for the given shot and render
            layer exists.
            Args:
                shot (str): name of the shot
                layer (str): name of the layer
            Returns:
                bool: True if the dictionary entry exists, False otherwise. """

        if self.data_file_directory and self.data and shot in self.data:
            layers = self.data[shot].get("render_layers")
            if layers and layer in layers:
                return True
        return False

    def update_layer(self, shot:str, layer:str, field_name:str, field_value):
        """ Updates a specific field value of a layer in the data.
            Args:
                shot (str): The name of the shot.
                layer (str): The name of the layer.
                field_name (str): The name of the field to update.
                field_value (str | int | layer): The new value of the field. """

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
                    # Replace the shot name in the .json
                    layers_dict[field_value] = layers_dict.pop(layer)

                elif field_name == "AOV mode":

                    layer_dict.update({field_name: field_value})

            except TypeError:  # For Active AOVs, field_value is a tuple

                value, status = field_value

                aov_list = layer_dict.get(field_name)

                # Any old files will have a wrong value type, so replace them with an empty list
                if isinstance(aov_list, (str, int)) or aov_list is None:
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
        """ Retrieves the information about the specified layer from the data.
            Args:
                shot (str): The name of the shot.
                layer (str): The name of the layer.
            Returns:
                dict: The layer information. """

        data = self.load_data()

        if shot in data and "layers" in data[shot] and layer in data[shot]["layers"]:

            return data[shot]["layers"][layer]

        print("Shot or layer not found.")
        return {}


class RenderLayer(CustomWidgetBase):
    """ Represents a render layer widget, subclassed from QWidget for Delegate use. """
    # pylint: disable=unnecessary-lambda
    def __init__(self, layer_name, parent=None):
        super().__init__(layer_name, parent)

        self.data_model = RenderLayerDataModel(self.data_file_directory)

        self.layer_name = layer_name
        self.shot_name = self.return_shot_name(self)
        self.setObjectName(layer_name)

        self.ui.setup_layer_ui()
        self.apply_frame_style(self.color, self.ui.frame)
        self.set_line_color()

        self.connect_slots()

    def connect_slots(self):
        """ Connects signals and slots. """
        super().connect_slots()

        self.ui.render_button.clicked.connect(lambda: self.ui.render_button.toggle())
        self.ui.render_button.clicked.connect(
            lambda: self.toggle_icon(self.ui.render_button))
        self.ui.visibility_button.clicked.connect(
            lambda: self.toggle_icon(self.ui.visibility_button))
        self.ui.visibility_button.toggled.connect(
            lambda: self.toggle_style_frame(
                self.shot_name, self.ui.visibility_button, self.ui.frame))
        self.ui.aov_button.clicked.connect(lambda: self.ui.aov_button.toggle())
        self.ui.aov_button.toggled.connect(lambda: self.toggle_icon(self.ui.aov_button))
        self.ui.aov_button.clicked.connect(lambda: self.toggle_button(self.ui.aov_button))
        self.ui.aov_beauty_button.clicked.connect(lambda: self.ui.aov_beauty_button.toggle())
        self.ui.aov_beauty_button.toggled.connect(
            lambda: self.toggle_icon(self.ui.aov_beauty_button))
        self.ui.aov_utility_button.clicked.connect(lambda: self.ui.aov_utility_button.toggle())
        self.ui.aov_utility_button.toggled.connect(
            lambda: self.toggle_icon(self.ui.aov_utility_button))

        self.ui.name_field.editingFinished.connect(
            lambda: self.update_field("name", self.ui.name_field.text()))
        self.ui.name_field.editingFinished.connect(
            lambda: util.rename_layers(self.layer_name, self.ui.name_field.text()))
        self.ui.start.editingFinished.connect(
            lambda: self.update_field("start", self.ui.start.text()))
        self.ui.start.editingFinished.connect(lambda: util.edit_overrides(
                self.layer_name, "start", int(self.ui.start.text()), "defaultRenderGlobals"))
        self.ui.end.editingFinished.connect(lambda: self.update_field("end", self.ui.end.text()))
        self.ui.end.editingFinished.connect(lambda: util.edit_overrides(
            self.layer_name, "end", int(self.ui.end.text()), "defaultRenderGlobals"))

    def update_layer_widgets(self, shot:str, layer:str):
        """ Updates the render layer widget with the layer information from JSON file.
            Args:
                shot (str): The name of the shot.
                layer (str): The name of the layer. """

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
                    self.ui.frame.setObjectName(value)
                    self.ui.name_field.setObjectName(value + "_layer")
                    self.ui.start.setObjectName(value + "_start")
                    self.ui.end.setObjectName(value + "_end")
                    self.ui.name_field.setText(value)

                elif key == "start":

                    self.ui.start.setText(str(value))
                    self.update_field("start", str(value))

                elif key == "end":
                    self.ui.end.setText(str(value))
                    self.update_field("end", str(value))

            # Check renderable status and set .isChecked for button and correct icon
            if renderable is not None and renderable is True:
                icon, tooltip = util.return_icon_tooltip("render_button", "on")
                self.ui.render_button.setChecked(True)
            else:
                icon, tooltip = util.return_icon_tooltip("render_button", "off")
                self.ui.render_button.setChecked(False)

            self.ui.render_button.setIcon(icon)
            self.ui.render_button.setToolTip(tooltip)

            # Check for the AOV mode key and value. Set .isChecked for button and correct icon.
            if aov_mode is not None and aov_mode == 1:
                icon, tooltip = util.return_icon_tooltip("aov_button", "on")
            else:
                icon, tooltip = util.return_icon_tooltip("aov_button", "off")

            self.ui.aov_button.setToolTip(tooltip)
            self.ui.aov_button.setIcon(icon)

            # Check for the AOV mode key and value. Set .isChecked for button and correct icon.

            if aovs is not None and isinstance(aovs, int):

                aov_list = ([], 0)
                RenderLayerDataModel(self.data_file_directory).update_layer(
                    shot, layer, "AOVs", aov_list)

            else:

                if "beauty" in aovs:

                    icon_beauty, tooltip_beauty = util.return_icon_tooltip(
                        "aov_beauty_button", "on")
                    self.ui.aov_beauty_button.setChecked(True)
                    self.ui.aov_beauty_button.setIcon(icon_beauty)
                    self.ui.aov_beauty_button.setToolTip(tooltip_beauty)

                elif "utility" in aovs:

                    icon_utility, tooltip_utility = util.return_icon_tooltip(
                        "aov_utility_button", "on")
                    self.ui.aov_utility_button.setChecked(True)
                    self.ui.aov_utility_button.setIcon(icon_utility)
                    self.ui.aov_utility_button.setToolTip(tooltip_utility)

    def return_layer_name_by_widget(self, widget: QWidget):
        """ Returns the name of the layer associated with the widget.
            Args:
                widget (QWidget): The widget.
            Returns:
                str: The name of the layer. """

        children = self.ui.frame.children()

        if widget in children:
            return self.layer_name
        return ""

    def return_shot_name(self, widget: QWidget):
        """ Returns the name of the shot associated with the widget.
            Args:
                widget (QWidget): The widget.
            Returns:
                str: The name of the shot. """

        parent = widget.parentWidget()
        layer_name = self.layer_name

        if parent is not None:
            layer_name = parent.objectName()

        shot_name = layer_name[:4]

        return shot_name

    def toggle_range_icon(self, button: QToolButton):
        """ Method toggles the frame range icon based on its start and end
            frame values relative to its parent shot ranges. Used to notify the user
            when a render layer has a different frame range set, and therefore, is
            not inheriting Shot's frame range values.
            Args:
                button (QToolButton): Instance of the RenderLayer frame range button. """

        status = self.compare_range_values()

        if not status:
            icon, tooltip = util.return_icon_tooltip("frame_range_button", "on")
            button.setChecked(True)

        else:
            icon, tooltip = util.return_icon_tooltip("frame_range_button", "off")
            button.setChecked(False)

        button.setIcon(icon)
        button.setToolTip(tooltip)

    def toggle_button(self, button: QToolButton):
        """ Toggles .checked state for the button.
            Args:
                button (QToolButton): Instance of the button. """

        if isinstance(button, QToolButton):
            if button.isChecked():
                button.setChecked(False)

            else:
                button.setChecked(True)

    def compare_range_values(self):
        """ Checks start and end frame for the layer and compares
        them to the shot frame range. Toggles the icon based on the 
        result of comparison. """

        data = self.data_model.load_data()

        shot_dict = data[self.shot_name]

        shot_start = int(shot_dict["start"])
        shot_end = int(shot_dict["end"])

        layer_start = int(shot_dict["layers"][self.layer_name]["start"])
        layer_end = int(shot_dict["layers"][self.layer_name]["end"])

        if layer_start != shot_start or layer_end != shot_end:
            return False

        return True

    def eventFilter(self, obj, event):  # pylint: disable=invalid-name
        """ Overrides default click event for QLineEdit field in the 
            RenderLayer. Enables the field to be editable, otherwise it's ReadOnly.
            Args:
                obj (QWidget): instance of the QLineEdit widget
                event (QEvent): Type of the event
            Returns:
                bool: True if event happened, False otherwise. """

        if obj == self.ui.name_field and event.type() == QEvent.Type.MouseButtonDblClick:
            self.ui.name_field.setReadOnly(False)
            return True
        return super().eventFilter(obj, event)

    def set_line_color(self):
        """ Apply style sheet to QLabel items in the RenderLayer. """

        self.ui.line.setStyleSheet(self.ui.frame_styles["QLabel"][self.color])
        self.ui.line_03.setStyleSheet(self.ui.frame_styles["QLabel"][self.color])
