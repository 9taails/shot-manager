"""
Module containing class definitions for custom widgets
used as part of model-view architecture inside the Shot Manager.
- Custom base class (subclassed from QWidget), Shot and RenderLayer
widgets (subclassed from the custom base) and the StyledItemDelegate.
The module also holds the model logic class for the RenderLayer.
"""

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

from source.util_paths import Path as path
from source import util
from source.model import data_model
from ui.ui_widgets import UI


class ShotManagerDelegate(QStyledItemDelegate):
    """ Delegate to handle custom widgets (Shot/RenderLayer) in the TreeView. """
    # pylint: disable=invalid-name,unused-argument,useless-parent-delegation
    def __init__(self, parent=None):
        super().__init__(parent)

        self.data_file = path.return_data_filepath()
        self.data_model = data_model.data
        #print("ShotManagerDelegate", id(self.data_model))

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
            data = self.data_model.get(name, {})
            widget.update_widget_names_values(data)
            #print("Shot",id(self.data_model))
            return widget

        if item_type == "RenderLayer":
            widget = RenderLayer(name)
            widget.setParent(parent)
            # Find parent shot name (stored in UserRole + 2 for layers)
            shot_name = index.data(Qt.ItemDataRole.UserRole + 2)
            # Sync with data
            shot_data = self.data_model.get(shot_name, {})
            layer_data = shot_data.get("layers", {}).get(name, {})
            widget.update_widget_names_values(layer_data)
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
            return QSize(500, 55)
        return QSize(500, 40)


class CustomWidgetBase(QWidget):
    """ Base class for Shot and RenderLayer widgets to handle styling and common logic. """
    # pylint: disable=attribute-defined-outside-init
    def __init__(self, name:str, parent=None):
        super().__init__(parent)

        self.data_file = path.return_data_filepath()  # Path to data file
        self.data_model = data_model.data
        self.name = name
        self.color = self.return_shot_color()
        self.ui = UI(name, self.color, self)

    def connect_slots(self):
        """ Connects signals and slots. """

        # Connect QLineEdit fields
        for name in ["start", "end", "width", "height"]:
            widget = getattr(self.ui, name)
            widget.editingFinished.connect(lambda n=name, w=widget: self.update_field(n, w.text()))

        # Connect QToolButtons
        for btn_name in ["frame_range", "visibility", "render", "aov", "aov_beauty", "aov_utility"]:
            button = getattr(self.ui, f"{btn_name}_button")

            if btn_name == "visibility":
                button.toggled.connect(lambda checked, b=button:
                    self.toggle_style_frame(self.name, b, self.ui.frame))
            button.toggled.connect(lambda checked, b=button: self.toggle_icon(b))

    def update_field(self, field_name, field_value):
        """ Updates the field value in the data dictionary and saves it to the data file.
            Args:
                field_name (str): The name of the field to update.
                field_value (str): The value of the field to update. """

        if isinstance(self, Shot):
            try:
                self.data_model.update_shot_dict(
                    self.shot_name, field_name, field_value)
            except NameError, ValueError, KeyError:
                # Handle the specific exception(s) that may occur during the update
                print("Error updating field.")
        elif isinstance(self, RenderLayer):
            try:
                self.data_model.update_layer_dict(
                    self.shot_name, self.layer_name, field_name, field_value)
            except NameError, ValueError, KeyError:
                # Handle the specific exception(s) that may occur during the update
                print("Error updating field.")

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

        shot_color = self.data_model[shot]["color"]
        active_color = shot_color + "_active"

        if button is not None:
            if button.isChecked():
                self.apply_frame_style(active_color, frame)
            else:
                self.apply_frame_style(shot_color, frame)

    def return_shot_name(self, widget):
        """ Returns the name of the Shot object containing the widget.
            Args:
                widget (QWidget|Shot|RenderLayer): Instance of the widget.
            Returns:
                str: Name of the shot. """

        if isinstance(widget, Shot):
            return self.name
        if isinstance(widget, RenderLayer):
            return widget.return_parent_shot()
        return widget.parent().objectName() # type: ignore

    def return_shot_color(self):
        """ Returns the color assigned to the shot inside the data file. """

        try:
            color: str = self.data_model[self.name].get("color")
            return color
        except KeyError:
            try:
                name = self.name[:4]
                color: str = self.data_model[name].get("color")
                return color
            except KeyError as e:
                print(f"KeyError: {e}. Assigning default grey color.")
                return "default"


class Shot(CustomWidgetBase):
    """ Custom widget representing a shot, subclassed from QWidget for Delegate use. """
    def __init__(self, shot_name, parent=None):
        super().__init__(shot_name, parent)

        self.data_model = data_model
        self.shot_name = shot_name
        self.setObjectName(shot_name)

        self.ui.setup_shot_ui()
        self.apply_frame_style(self.color, self.ui.frame)
        self.connect_slots()
        #self.sync_shot_aovmode()

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

    def sync_shot_aovmode(self):
        """ Checks the AOV mode entry in the JSON dictionary, for all layers
        belonging to the Shot. Toggles the AOV render mode icon for the 
        Shot. """

        # Retrieve JSON data and create an empty set
        # AOV mode can only have 3 possible values; 0, 1, 2.
        # Since sets cannot have more than one same element,
        # the resulting set will have only 3 elements, regardless
        # of bhow many render layers there are.

        data_model.create_data_file()
        data = data_model.load_data()
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

        self.data_model = data_model
        self.layer_name = layer_name
        self.shot_name = self.return_shot_name(self)
        self.setObjectName(layer_name)

        # Sync UI
        self.ui.setup_layer_ui()
        self.apply_frame_style(self.color, self.ui.frame)
        self.set_line_color()
        #self.sync_buttons()
        self.connect_slots()

    def connect_slots(self):
        """ Connects signals and slots. """
        super().connect_slots()

        #self.ui.name_field.editingFinished.connect(
            #lambda: util.rename_layers(self.layer_name, self.ui.name_field.text()))
        self.ui.name_field.installEventFilter(self)
        self.ui.name_field.editingFinished.connect(
            lambda: self.update_field("name", self.ui.name_field.text()))
        self.ui.name_field.editingFinished.connect(
            lambda: self.data_model.rename_layer(
                self.shot_name, self.layer_name, self.ui.name_field.text()))

    def sync_buttons(self):
        """ Method collecting all button toggle methods. """

        self.update_aov_buttons(self.shot_name, self.layer_name)
        self.update_aovmode_button(self.shot_name, self.layer_name)
        self.update_render_button(self.shot_name, self.layer_name)
        self.toggle_range_icon(self.ui.frame_range_button)

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

    def return_parent_shot(self):
        """ Returns the name of the shot associated with the widget.
            Assumes the shot name is the first four characters of the layer name.
            Returns:
                str: The name of the shot. """

        layer_name = self.layer_name
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
        """ Toggles button's icon and tooltip based on its status 
            from the dictionary.
            Args:
                shot (str): Name of the shot.
                layer (str): Name of the layer. """

        # Retrieve layer values
        layer_dict = self.data_model.return_layer_dict(shot, layer)

        aovs = layer_dict.get("AOVs", [])

        for aov in ["beauty", "utility"]:
            for aov_tuple in aovs:
                if aov in aov_tuple:
                    status = aov_tuple[1]
                    button_name = f"aov_{aov}_button"
                    button = getattr(self.ui, button_name)
                    icon, tooltip = util.return_icon_tooltip(button_name, "on" if status else "off")
                    button.setChecked(status)
                    button.setIcon(icon)
                    button.setToolTip(tooltip)

    def update_aovmode_button(self, shot:str, layer:str):
        """ Toggles button's icon and tooltip based on its status 
            from the dictionary.
            Args:
                shot (str): Name of the shot.
                layer (str): Name of the layer. """

        # Retrieve layer values
        layer_dict = data_model.return_layer_dict(shot, layer)

        aovmode = layer_dict.get("AOV mode", 0)

        icon, tooltip = util.return_icon_tooltip("aov_button", "on" if aovmode else "off")
        self.ui.aov_button.setChecked(aovmode)
        self.ui.aov_button.setIcon(icon)
        self.ui.aov_button.setToolTip(tooltip)

    def update_render_button(self, shot:str, layer:str):
        """ Toggles button's icon and tooltip based on its status 
            from the dictionary.
            Args:
                shot (str): Name of the shot.
                layer (str): Name of the layer. """

        # Retrieve layer values
        layer_dict = data_model.return_layer_dict(shot, layer)

        status = layer_dict.get("renderable", 1)

        icon, tooltip = util.return_icon_tooltip("render_button", "on" if status else "off")
        self.ui.render_button.setChecked(status)
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
