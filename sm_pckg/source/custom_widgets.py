"""
Module containing class definitions for custom widgets
used as part of model-view architecture inside the Shot Manager.
- Custom base class (subclassed from QWidget), Shot and RenderLayer
widgets (subclassed from the custom base) and the StyledItemDelegate.
The module also holds the model logic class for the RenderLayer.
"""
from PySide6.QtWidgets import (
    QToolButton
)

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
from ui.ui_widgets import UI


class ShotManagerDelegate(QStyledItemDelegate):
    """ Delegate to handle custom widgets (Shot/RenderLayer) in the TreeView. """
    # pylint: disable=invalid-name,unused-argument,useless-parent-delegation
    def __init__(self, parent=None):
        super().__init__(parent)

        self.data_file = Paths.return_shot_data_full_filepath()

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
            data = DataModel(self.data_file).return_shot_dict(name)
            widget.update_widget_names_values(data)
            return widget

        if item_type == "RenderLayer":
            widget = RenderLayer(name)
            widget.setParent(parent)
            # Find parent shot name (stored in UserRole + 2 for layers)
            shot_name = index.data(Qt.ItemDataRole.UserRole + 2)
            # Sync with data
            data = DataModel(self.data_file).return_layer_dict(shot_name, name)
            widget.update_widget_names_values(data)
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

        self.data_file = Paths.return_shot_data_full_filepath()  # Path to data file
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

        if isinstance(self, Shot):
            print(field_name, field_value)
            try:
                self.data_model.update_shot_dict(
                    self.shot_name, field_name, field_value)
            except Exception as e:
                # Handle the specific exception(s) that may occur during the update
                print(f"Error updating field: {e}")
        elif isinstance(self, RenderLayer):
            try:
                self.data_model.update_layer_dict(
                    self.shot_name, self.layer_name, field_name, field_value)
            except Exception as e:
                # Handle the specific exception(s) that may occur during the update
                print(f"Error updating field: {e}")

    def update_widget_names_values(self, data:dict):
        """ Updates the render layer widget with the layer information from JSON file.
            Args:
                data (dict): Data dictionary."""
            
        if data != {}:
            for key, value in data.items():

                if key == "name":
                    self.setObjectName(value)
                    self.ui.frame.setObjectName(value)
                    self.ui.start.setObjectName(value + "_start")
                    self.ui.end.setObjectName(value + "_end")
                    self.ui.name_field.setText(value)
                    self.ui.name_field.setObjectName(value)
                    if isinstance(self, RenderLayer):
                        self.ui.name_field.setObjectName(value + "_layer")

                elif key == "start":
                    self.ui.start.setText(str(value))

                elif key == "end":
                    self.ui.end.setText(str(value))
                
                elif key == "width":
                    self.ui.width.setText(str(value))

                elif key == "height":
                    self.ui.height.setText(str(value))

                elif key == "render_layers" and isinstance(self, Shot):
                    if len(value) == 1:
                        self.ui.layers_label.setText(str(len(value)) + " layer")
                    else:
                        self.ui.layers_label.setText(str(len(value)) + " layers")
    
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
                self.rename_layer(shot, layer, field_value)
                self.save_data()

            elif field_name in ["start", "end", "width", "height", "renderable", "AOV mode"]:
                layer_dict.update({field_name: int(field_value)})
                self.save_data()

            elif field_name == "AOVs":
                self.update_aovs(layer_dict, field_value)
                self.save_data()

    def rename_layer(self, shot:str, layer:str, field_value:str):
        """ Method updates all relevant entries for the layer
            with a new name.
            Args:
                shot (str): Name of the shot.
                layer (str): Old name of the layer.
                field_value (str): New name of the layer. """

        # Update the name in the render layers string
        shot_dict:dict = self.data.get(shot)
        render_layers:list = shot_dict.get("render_layers", [])

        for i in render_layers:
            if i == layer:
                index = render_layers.index(i)
                render_layers[index] = field_value
                shot_dict.update({"render_layers": render_layers})

        # Update the name in the layers dictionary
        layers_dict:dict = shot_dict.get("layers", {})
        
        try:
            # Replace the shot name in JSON
            layers_dict[field_value] = layers_dict.pop(layer)
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


class Shot(CustomWidgetBase):
    """ Custom widget representing a shot, subclassed from QWidget for Delegate use. """
    def __init__(self, shot_name, parent=None):
        super().__init__(shot_name, parent)
        
        self.data_model = DataModel(self.data_file)
        
        self.shot_name = shot_name
        self.setObjectName(shot_name)

        self.ui.setup_shot_ui()
        self.apply_frame_style(self.color, self.ui.frame)

        self.connect_slots()

    def connect_slots(self):
        """ Connects signals and slots. """
        super().connect_slots()

        # Connect QLineEdit fields
        for name in ["start", "end", "width", "height"]:
            widget = getattr(self.ui, name)
            widget.editingFinished.connect(lambda n=name, w=widget: self.update_field(n, w.text()))

        # Connect QToolButtons
        for btn_name in ["frame_range", "visibility", "render", "aov", "aov_beauty", "aov_utility"]:
            button = getattr(self.ui, f"{btn_name}_button")

            if btn_name == "visibility":
                button.toggled.connect(lambda checked, b=button: self.toggle_style_frame(self.shot_name, b, self.ui.frame))
            button.toggled.connect(lambda checked, b=button: self.toggle_icon(b))

        self.ui.name_field.textEdited.connect(lambda text: self.update_field("name", text))

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
                    self.ui.width.setObjectName(value + "_width")
                    self.ui.height.setObjectName(value + "_height")
                    self.ui.layers_label.setObjectName(value + "_layers")
                    self.ui.name_field.setText(value)

                elif key == "start":

                    self.ui.start.setText(str(value))

                elif key == "end":
                    self.ui.end.setText(str(value))

                elif key == "width":
                    self.ui.width.setText(str(value))

                elif key == "height":
                    self.ui.height.setText(str(value))

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


class RenderLayer(CustomWidgetBase):
    """ Represents a render layer widget, subclassed from QWidget for Delegate use. """
    # pylint: disable=unnecessary-lambda
    def __init__(self, layer_name, parent=None):
        super().__init__(layer_name, parent)

        self.data_model = DataModel(self.data_file)

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

        # Connect QLineEdit fields
        for name in ["start", "end"]:
            widget = getattr(self.ui, name)
            widget.editingFinished.connect(lambda n=name, w=widget: self.update_field(n, w.text()))

        # Connect QToolButtons
        for btn_name in ["render", "visibility", "aov", "aov_beauty", "aov_utility"]:
            button = getattr(self.ui, f"{btn_name}_button")
            button.toggled.connect(lambda checked, b=button: self.toggle_icon(b))

            if btn_name == "visibility":
                button.toggled.connect(lambda checked, b=button: self.toggle_style_frame(self.shot_name, b, self.ui.frame))

        self.ui.name_field.editingFinished.connect(
            lambda: self.update_field("name", self.ui.name_field.text()))
        self.ui.name_field.editingFinished.connect(
            lambda: util.rename_layers(self.layer_name, self.ui.name_field.text()))

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

    def update_aov_buttons(self, shot:str, layer:str):

        # Retrieve layer values
        layer_dict = DataModel(self.data_file).return_layer_dict(shot, layer)
        
        aovs = layer_dict.get("AOVs", [])

        for aov in ["beauty", "utility"]:
            for aov_tuple in aovs:
                if aov in aov_tuple:
                    status = aov_tuple[1]
                    button_name = f"aov_{aov}_button"
                    button = self.ui.__getattribute__(button_name)
                    icon, tooltip = util.return_icon_tooltip(button_name, status)
                    button.setIcon(icon)
                    button.setToolTip(tooltip)

    def update_aovmode_button(self, shot:str, layer:str):

        # Retrieve layer values
        layer_dict = DataModel(self.data_file).return_layer_dict(shot, layer)
        
        aovmode = layer_dict.get("AOV mode", 0)

        icon, tooltip = util.return_icon_tooltip("aov_button", aovmode)
        self.ui.aov_button.setIcon(icon)
        self.ui.aov_button.setToolTip(tooltip)

    def update_render_button(self, shot:str, layer:str):

        # Retrieve layer values
        layer_dict = DataModel(self.data_file).return_layer_dict(shot, layer)

        status = layer_dict.get("renderable", 1)

        icon, tooltip = util.return_icon_tooltip("render_button", status)
        self.ui.render_button.setIcon(icon)
        self.ui.render_button.setToolTip(tooltip)

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
