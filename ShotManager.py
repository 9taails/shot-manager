from __future__ import annotations

import sys
from functools import partial
import re
import json

from PySide6 import QtWidgets
from PySide6.QtCore import (
    QSize,
    Qt
)

from PySide6.QtWidgets import (
    QDialog,
    QTreeWidgetItem,
    QFrame,
    QLineEdit,
    QToolButton,
    QLabel,
    QMessageBox,
    QInputDialog,
    QMenu,
    QGridLayout,

)

from PySide6.QtGui import (
    QAction,
    QIcon,
    QStandardItem
)

try:
    import maya.cmds as mc
    import maya.mel as mel
    import maya.app.renderSetup.model.renderSetup as render
    import maya.app.renderSetup.model.renderLayer as renderLayer
    import maya.app.renderSetup.model.override as override
    import maya.app.renderSetup.model.container as container
    import maya.app.renderSetup.views.overrideUtils as renderUtils
    import maya.app.renderSetup.model.collection as collection
    import pymel.core as pm

except ModuleNotFoundError:  # Local testing
    pass

from source import utilities as util
from ui.Paths import Paths
from ui.ShotManagerUI import ShotManagerWindow
from RenderLayer import RenderLayer
from Shot import Shot
from ShotBuilder import ShotBuilder
from LayerCreator import LayerCreator


class ShotManager(ShotManagerWindow):
    """A class for the shot-oriented UI.

    This tool improves Maya's default functionality by creating a set of elements for a single or multiple
    shots defined by the user. Each created set contains basic shot information in the form of attributes, like
    frame range and resolution. The UI allows for easily switching between the various shots and/or render layers.
    """

    # CLASS VARIABLES
    try:
        pw = util.get_maya_window()
    except NameError:
        pw = None

    manager_instance = None         # maintain a single instance of the dialog in Production

    def __init__(self, parent=pw):
        super(ShotManager, self).__init__(parent)

        self.data_file_directory = Paths.return_shot_data_full_filepath()  # Path to data file
        self.data_directory = Paths.return_shot_data_directory()  # Path to data folder
        self.data = util.shot_data_directory()      # Path to the JSON file
        self.style_sheet = util.load_frame_style()
        self.setup_ui(self)

        self.root = self.shotList_treeWidget.invisibleRootItem()
        self.root_index = self.shotList_treeWidget.indexFromItem(self.root)
        self.tree_object = self.shotList_treeWidget

        self.set_up_model(self.data)

        self.newShot_button.clicked.connect(lambda: self.show_shot_builder())
        self.newLayer_button.clicked.connect(lambda: self.get_selection())
        self.newLayer_button.clicked.connect(lambda: self.show_layer_creator())

        # Runs in Maya only

        if "maya" in sys.modules:

            util.set_redshift_renderer()
            util.set_correct_fps()
            util.create_default_groups()
            util.create_global_sets()
            util.create_global_rs_sets()
        else:
            print("Maya hasn't been loaded yet.")

        self.set_shot_visibility()
        self.set_layer_visibility()

        self.connect_shot_button("render_button")
        self.set_layer_renderable()

        self.connect_shot_button("frame_range_button")
        self.on_shot_frame_editing_finished()
        self.connect_layer_frame_range_edit_fields("start")
        self.connect_layer_frame_range_edit_fields("end")
        self.toggle_layer_range_icons()

        self.aov_init_layer_buttons("aov_beauty_button")
        self.aov_init_layer_buttons("aov_utility_button")

        self.connect_shot_button("aov_button")
        self.aov_mode_init_layer_button("aov_button")
        self.aov_mode_connect_layer_button()
        self.connect_shot_button("aov_beauty_button")
        self.aov_connect_layer_button("aov_beauty_button")
        self.connect_shot_button("aov_utility_button")
        self.aov_connect_layer_button("aov_utility_button")

        self.set_shot_buttons_indicator_color()

        self.delete_shot()
        self.delete_layer()

        self.show_edit_menu()

    # Windows display

    @classmethod
    def show_ui(cls):
        """Show Shot Manager Window."""

        if cls.manager_instance:
            cls.manager_instance.close()
            cls.manager_instance.deleteLater()

        cls.manager_instance = ShotManager()
        cls.manager_instance.show()

    def show_shot_builder(self):
        """Shows the Shot Builder Dialog."""

        sb_window = ShotBuilder(self)
        sb_window.add_shots_button.clicked.connect(lambda: sb_window.write_data())
        sb_window.add_shots_button.clicked.connect(lambda: self.set_up_model(ShotManager().data))
        # sb_window.addShots_button.clicked.connect(lambda: sb_window.accept())
        sb_window.add_shots_button.clicked.connect(lambda: self.deleteLater())
        sb_window.add_shots_button.clicked.connect(lambda: self.show_ui())
        sb_window.show()

    def show_layer_creator(self):
        """Shows the Layer Creator Dialog."""

        lc_window = LayerCreator(self)
        lc_window.createLayers_button.clicked.connect(lambda: lc_window.add_new_layers(self.data,
                                                                                       self.get_selection()))
        lc_window.createLayers_button.clicked.connect(lambda: self.set_up_model(self.data))
        lc_window.createLayers_button.clicked.connect(lambda: self.add_render_layer_widget())
        lc_window.createLayers_button.clicked.connect(lambda: lc_window.accept())
        lc_window.show()

    #############################################
    # ---------> DATA MANAGEMENT <----------
    #############################################

    def write_data(self, data: dict):
        """ Writes the data to JSON file."""

        if self.data_file_directory is not None:
            with open(self.data_file_directory, "w") as data_dump:
                json.dump(data, data_dump, indent=4)

    def set_up_model(self, shot_data):
        """Reads in the JSON file and applies the view to the model.

        Args:
            shot_data (dict) : A JSON file containing shot information.
        """

        tree_widget = self.shotList_treeWidget
        root = self.root
        widget_list = []

        # Check for existing widgets in the tree
        widget_count = root.childCount()

        for number in range(0, widget_count):
            widget_item = root.child(number)
            name = tree_widget.itemWidget(widget_item, 0).objectName()
            widget_list.append(name)

        if shot_data:

            shot_list = sorted(list(shot_data.keys()))

            if len(shot_list) > 0:
                # Create shot items from data model

                for shot in shot_list:

                    # Don't add shots if they're already in the list
                    if shot not in widget_list:

                        widget_item = QTreeWidgetItem(shot)
                        root.addChild(widget_item)

                        shot_name_dict = shot_data[shot]  # Name of the new shot
                        shot_color = shot_data[shot]["color"]  # Assigned color

                        new_shot_instance = Shot(shot)  # Class Shot
                        new_shot_instance.update_shot_widgets(shot_name_dict)
                        new_shot_instance.setObjectName(shot)
                        new_shot_instance.setParent(self)

                        tree_widget.setItemWidget(widget_item, 0, new_shot_instance)  # Class QTreeWidgetItem

                        widget_item.setSizeHint(0, QSize(550, 75))

                        try:

                            Shot.apply_frame_style(new_shot_instance, shot_color)

                        except TypeError:  # Old json file

                            pass

                        finally:

                            new_entry = root.child(root.childCount() - 1)
                            layer_list = sorted(shot_data[shot]["render_layers"])

                            # Create layers per shot

                            for layer in layer_list:

                                new_parent = new_entry
                                child_item = QTreeWidgetItem(layer)
                                new_parent.addChild(child_item)

                                new_layer_instance = RenderLayer(layer)
                                new_layer_instance.update_layer_widgets(shot, layer)
                                new_layer_instance.setObjectName(layer)
                                new_layer_instance.setParent(new_shot_instance)
                                child_item.setSizeHint(0, QSize(550, 60))

                                tree_widget.setItemWidget(child_item, 0, new_layer_instance)

                                try:

                                    Shot.apply_frame_style(new_layer_instance, shot_color)

                                except TypeError:  # Old json file

                                    pass

    def update_data(self, shot: str, layer: str | None, key: str, value: str | int):
        """ Updates key - value pair in the dictionary and saves out the JSON file.

            Args:
                shot - name of the shot
                layer - name of the layer, if None only shot gets updated
                key - name of the key
                value - value of the key
        """

        data = util.shot_data_directory()

        if not layer:

            data[shot].update({
                key: value
            })

        else:

            data[shot]["layers"][layer].update({
                key: value
            })

        self.write_data(data)

    #############################################
    # ---------> BUTTON FUNCTIONALITY <----------
    #############################################

    @staticmethod
    def return_status(button):
        """Returns True if button is checked, else returns False.

            Args:
            button (object) = A QtObject
        """

        return button.isChecked()

    def connect_shot_button(self, button_name):

        # Get a list of all shots class Shot
        shot_widgets = self.return_child_widgets(self.root, "Shot")

        for shot in shot_widgets:

            # Get a respective QTreeWidgetItem for each shot
            shot_widget = self.return_respective_type(shot, self.root, "QTreeWidgetItem")

            # Get shot button widget
            button = shot.return_child_widget(button_name)

            # Add reset function
            button.clicked.connect(partial(self.reset_layers, shot_widget, button, button_name))

            # Toggle shot's icon
            button.clicked.connect(partial(Shot.toggle_icon, button))

    def set_shot_buttons_indicator_color(self):
        """ On init, checks the status of all child layers and changes shot's icon color
            to reflect the status of its layers.
        """

        shot_widgets = self.return_child_widgets(self.root, "Shot")

        for shot in shot_widgets:
            buttons = shot.findChildren(QToolButton)
            shot_widget = self.return_respective_type(shot, self.root, "QTreeWidgetItem")

            for button in buttons:
                button_name = button.objectName()
                try:
                    self.toggle_shot_icon_and_tooltip(shot_widget, button, button_name)
                except AttributeError:      # Sometimes, it can't find the button on init
                    pass
                except KeyError:        # For non-toggable buttons
                    pass

    def reset_layers(self, shot_widget: QTreeWidgetItem, parent_button: QToolButton, button_name: str):
        """ Loops over all shot's layers icons and toggles the checked status of all those icons to the same status
            the shot icon has. Used in resetting all frame range overrides on layers and setting renderable status on
            all shot layers at once.

            Args:
                shot_widget: QTreeWidgetItem, container of Shot
                parent_button: QToolButton attrib of Shot
                button_name: name of the button
        """

        shot = self.return_respective_type(shot_widget, self.root, "Shot")
        shot_name = shot.shot_name

        layer_buttons = self.return_shot_children_by_name(button_name, shot_name)
        status = self.return_status(parent_button)

        for b in layer_buttons:

            layer_name = RenderLayer.return_layer_name(b)

            if isinstance(b, QToolButton):

                # Set check state on all layers' buttons to parent button check state
                b.setChecked(status)

                if button_name == "render_button":

                    self.toggle_layer_renderable_status(b, shot_name, layer_name)

                elif button_name == "frame_range_button":

                    self.reset_frame_range(b)

                elif button_name == "aov_button":

                    self.aov_mode_reset_layers(parent_button, b)

                elif button_name == "aov_beauty_button" or button_name == "aov_utility_button":

                    aov_group = button_name.split("_")[1]

                    self.aov_toggle(b)
                    util.create_aov_and_override_enabled(layer_name, aov_group, status)

    def toggle_shot_icon_and_tooltip(self, shot_widget, shot_button, button_name):
        """ Function toggles the shot buttons, their icons and tooltips based on the checked status of its layers.

            Args:
                shot_widget (QTreeWidgetItem): QTreeItemWidget for the shot
                shot_button (QToolButton): Instance of any child QToolButton of Shot
                button_name (str): Name of the button
        """

        # Check the checked status of AOV button for all layers under each shot
        status_list = self.return_buttons_status_list(shot_widget, button_name)

        if True in status_list and False in status_list:

            status = "mid"
            shot_button.setChecked(True)

        elif True in status_list and False not in status_list:

            status = "on"
            shot_button.setChecked(True)

        else:

            status = "off"
            shot_button.setChecked(False)

        icon, tooltip = util.return_icon_and_tooltip(button_name, status)

        shot_button.setIcon(icon)
        shot_button.setToolTip(tooltip)

    def toggle_layer_icon_and_tooltip(self, button):
        """ Function toggles the shot buttons, their icons and tooltips based on the checked status of its layers.

            Args:
                button (QToolButton): Instance of any child QToolButton of Render Layer
        """

        button_status = self.return_status(button)
        button_name = button.objectName()

        if button_status:

            status = "on"
            button.setChecked(True)

        else:

            status = "off"
            button.setChecked(False)

        icon, tooltip = util.return_icon_and_tooltip(button_name, status)

        button.setIcon(icon)
        button.setToolTip(tooltip)

    ####################################
    # ---------> VISIBILITY <----------
    ####################################

    def set_shot_visibility(self, button_name="visibility_button"):
        """Checks the status of all top level visibility buttons and toggles the current icon, keeping only one
                   Shot visible at a time.

        """

        shot_widgets = self.return_child_widgets(self.root, "Shot")

        for shot in shot_widgets:
            shot: Shot

            shot_widget = self.return_respective_type(shot, self.root, "QTreeWidgetItem")

            parent_button = shot.return_child_widget(button_name)

            shot_name = shot.__getattribute__("shot_name")
            layer_name = shot_name + "master"

            self.toggle_shot_icon_and_tooltip(shot_widget, parent_button, button_name)

            parent_button.clicked.connect(partial(Shot(shot_name).toggle_icon, parent_button))
            parent_button.clicked.connect(partial(self.hide_other_shots, parent_button))
            parent_button.clicked.connect(partial(self.hide_other_layers, None))
            parent_button.clicked.connect(partial(util.switch_layer, layer_name))

    def set_layer_visibility(self, button_name="visibility_button"):
        """Toggles the icon and sets the correct render layer .renderable attribute to reflect the change.

        """

        buttons = self.return_shot_children_by_name(button_name, None)

        for b in buttons:
            b: QToolButton
            layer_name = RenderLayer.return_layer_name(b)

            b.clicked.connect(partial(self.toggle_layer_icon_and_tooltip, b))
            b.clicked.connect(partial(self.hide_other_shots, None))
            b.clicked.connect(partial(self.hide_other_layers, b))
            b.clicked.connect(partial(self.set_shot_visibility))
            b.clicked.connect(partial(util.switch_layer, layer_name))

    def toggle_layer_visible_status(self, button: QToolButton):
        """Retrieves the .isChecked() status of the button, toggles the icon based on the value, updates the data file
            with the new value and calls the function to toggle the renderable attribute in the scene.

            Args:
                button: instance of the pressed QToolButton

        """

        status = self.return_status(button)

        if status:

            button.setChecked(True)
            button.setIcon(QIcon(Paths.icon("icon_visibility_green.png")))
            button.setToolTip("Layer is currently active.")

        else:

            button.setChecked(False)
            button.setIcon(QIcon(Paths.icon("icon_visibility_off.png")))
            button.setToolTip("Set active layer.")

    def hide_other_shots(self, button: QToolButton, button_name="visibility_button"):
        """Unchecks all the visibility buttons except the current button, so that only one shot at a time
        is highlighted. Additionally, switches the view in Maya to current shot, setting the correct
        playback range and camera.

            Args:
                button (QObject) = A QToolButton, instance of the currently checked button
                button_name: name of the button object
        """

        # Set icon and status for all other buttons

        all_buttons = self.return_widgets_by_name(self.root, button_name)

        if button:

            off_list = [b for b in all_buttons if b is not button]

        else:

            off_list = all_buttons

        for buttons in off_list:
            buttons.setChecked(False)
            buttons.setIcon(QIcon(Paths.icon("icon_visibility_off.png")))

    def hide_other_layers(self, button, button_name="visibility_button"):
        """Checks the status of all child level visibility buttons and toggles the icon, keeping only one RenderLayer
            visible at a time. Toggles the visibility state of the parent Shot.

        """

        layer_buttons = self.return_shot_children_by_name(button_name, None)

        if button:

            off_layers = [b for b in layer_buttons if b is not button]

        else:

            off_layers = layer_buttons

        for buttons in off_layers:
            buttons: QToolButton

            buttons.setChecked(False)

            layer_name = RenderLayer.return_layer_name(buttons)

            RenderLayer(layer_name).toggle_icon(buttons)

    ####################################
    # ---------> RENDERABLE <----------
    ####################################

    def set_layer_renderable(self, button_name="render_button"):
        """Toggles the icon and sets the correct render layer .renderable attribute to reflect the change."""

        # Get render buttons for all layers.
        buttons = self.return_shot_children_by_name(button_name, None)

        # Loop over all layer render buttons
        for b in buttons:
            # Get layer name
            layer_name = RenderLayer.return_layer_name(b)

            # Get shot name
            shot_name = RenderLayer(layer_name).return_shot_name(b)

            # Get Shot
            shot = self.root.treeWidget().findChild(Shot, shot_name)

            # Get shot widget of type QTreeWidgetItem
            shot_widget = self.return_respective_type(shot, self.root, "QTreeWidgetItem")

            # Get shot's render button instance
            parent_button = shot.render_button

            # Connect layer buttons
            b.clicked.connect(partial(self.toggle_layer_renderable_status, b, shot_name, layer_name))
            b.clicked.connect(partial(self.toggle_shot_icon_and_tooltip, shot_widget, parent_button, button_name))

    def toggle_layer_renderable_status(self, button: QToolButton, shot: str, layer: str):
        """Retrieves the .isChecked() status of the button, toggles the icon based on the value, updates the data file
            with the new value and calls the function to toggle the renderable attribute in the scene.

            Args:
                button: instance of the shot's QToolButton
                shot: name of the shot
                layer: name of layer that's being edited

        """

        status = self.return_status(button)

        self.toggle_layer_icon_and_tooltip(button)

        # Save the renderable status to JSON file

        layer_dict = self.data[shot]["layers"][layer]
        layer_dict.update({"renderable": status})

        self.write_data(self.data)

        util.set_layer_renderable(layer, status)

    ####################################
    # ---------> FRAME RANGE <----------
    ####################################

    def on_shot_frame_editing_finished(self):
        """Connects the editing finished on the frame range field to function that changes the frame range."""

        start_fields = self.return_widgets_by_name(self.root, "start")
        end_fields = self.return_widgets_by_name(self.root, "end")

        edit_fields = start_fields + end_fields

        for widget in edit_fields:
            widget.editingFinished.connect(partial(self.change_global_shot_frame_range, widget))

    def change_global_shot_frame_range(self, field: QLineEdit):
        """ Sets shot frame range and sets all shot layers frame ranges to the same value if the layers have no
            frame range overrides.

            Args:
                field: Shot start or end edit field
        """

        parent: Shot = Shot.return_parent(field)  # Get Shot parent of the field widget
        shot_name = parent.shot_name  # Get the name of the shot
        shot_value = int(field.text())  # Get the current value of the shot

        shot_field_name = field.objectName()  # ex: shot_start
        field_name = shot_field_name.split("_")[1]  # ex: start

        # Get shot's render layers
        layer_edit_widgets = self.return_widgets_by_name(parent, field_name)  # Get shot's layers' widgets
        layer_icons = self.return_widgets_by_name(parent, "frame_range_button")  # Get shot's layers' icons

        # Loop over each layer's edit widget;
        # Get the name of the layer
        # Get the frame icon for the layer and check its status
        for layer_edit_field in layer_edit_widgets:

            layer_name = RenderLayer.return_layer_name(layer_edit_field)

            index = layer_edit_widgets.index(layer_edit_field)  # Get respective icon and check its status
            icon: QToolButton = layer_icons[index]
            icon_status = icon.isChecked()

            if not icon_status:  # If the icon is red (overriden), don't change the frame range.

                # Update the dictionary
                self.update_data(shot_name, layer_name, field_name, shot_value)

                # Change edit field text on the layer
                layer_edit_field.setText(str(shot_value))

                # Update layer info in the dictionary
                RenderLayer(layer_name).update_field(field_name, shot_value)

                # Create an override inside maya on the render layer
                util.edit_overrides(layer_name, field_name, shot_value, "defaultRenderGlobals")

        # FRAME RANGE OVERRIDES

    def set_layer_frame_range(self, field: QLineEdit):
        """ Sets layer frame range independent of the shot.

            Args:
                field: Shot start or end edit field
        """

        parent: RenderLayer = RenderLayer.return_parent(field)
        layer_name = parent.layer_name
        layer_value = int(field.text())
        shot_name = parent.return_shot_name(field)

        field_object_name = field.objectName()
        field_name = field_object_name.split("_")[1]

        self.update_data(shot_name, layer_name, field_name, layer_value)
        field.setText(str(layer_value))

    def connect_layer_frame_range_edit_fields(self, widget_name: str):
        """ Updates the layer's end frame in the data file and checks if it differs from the shot's end range.
            If it does, it toggles the frame range icon to red.
        """

        # Get a list of all Shot class widgets
        shot_objects = self.return_child_widgets(self.root, "Shot")

        # Loop over each shot in the list
        for shot in shot_objects:

            # Get shot widget
            shot_widget = self.return_respective_type(shot, self.root, "QTreeWidgetItem")

            # Get all edit fields from the shot's layers
            layer_widgets = self.return_widgets_by_name(shot, widget_name)

            # Get all frame range buttons from the shot's layers
            button_widgets = self.return_widgets_by_name(shot, "frame_range_button")

            # Get shot's frame range button
            shot_range_button = shot.frame_range_button

            # Loop over all start fields
            # Find the respective button to each start field
            # On editing finished, set the start frame on the layer in the dictionary
            # Then, compare the start frame of layer to that of shot and toggle the frame range icon

            for edit_widget in layer_widgets:
                index = layer_widgets.index(edit_widget)
                button = button_widgets[index]
                layer_name = RenderLayer.return_layer_name(edit_widget)

                edit_widget.editingFinished.connect(partial(self.set_layer_frame_range, edit_widget))
                edit_widget.editingFinished.connect(partial(RenderLayer(layer_name).toggle_range_icon, button))
                edit_widget.editingFinished.connect(
                    partial(self.toggle_shot_icon_and_tooltip, shot_widget, shot_range_button, "frame_range_button"))

    def toggle_layer_range_icons(self, button_name="frame_range_button"):
        """ Compares the start and end frames of each layer to respective shot and toggles the icon between default
            and red to indicate if the layer inherits shot's frame range or not. Not dynamic, effective at re-opening
            the Shot Manager.
        """

        shot_widgets = self.return_child_widgets(self.root, "Shot")

        for s in shot_widgets:

            button_widgets = self.return_widgets_by_name(s, button_name)

            for button in button_widgets:
                button: QToolButton
                layer_name = RenderLayer.return_layer_name(button)
                RenderLayer(layer_name).toggle_range_icon(button)

    def reset_frame_range(self, button: QToolButton):
        """ Sets shot frame range to all layers under the shot. Frame range is updated in both JSON and view.

            Args:
                button: QToolButton instance

        """

        button.setChecked(False)
        icon, tooltip = util.return_icon_and_tooltip(button.objectName(), "off")

        button.setIcon(icon)
        button.setToolTip(tooltip)

        layer_name = RenderLayer.return_layer_name(button)
        shot_name = RenderLayer(layer_name).shot_name

        start_value = self.data[shot_name]["start"]
        end_value = self.data[shot_name]["end"]

        self.update_data(shot_name, layer_name, "start", start_value)
        self.update_data(shot_name, layer_name, "end", end_value)

        start_field = self.return_shot_children_by_name("start", shot_name)
        end_field = self.return_shot_children_by_name("end", shot_name)

        for s_field in start_field:
            s_field.setText(str(start_value))
            util.edit_overrides(layer_name, "start", start_value, "defaultRenderGlobals")

        for e_field in end_field:
            e_field.setText(str(end_value))
            util.edit_overrides(layer_name, "end", end_value, "defaultRenderGlobals")

        self.write_data(self.data)

    ####################################
    # ---------> AOV MODE <----------
    ####################################
    # AOV mode enabled/disabled status

    def aov_mode_connect_layer_button(self, button_name="aov_button"):
        """Toggles the icon and AOV render mode for the render layer."""

        # Get AOV buttons for all the layers
        buttons = self.return_shot_children_by_name(button_name, None)

        for button in buttons:

            # Get layer name
            layer_name = RenderLayer.return_layer_name(button)

            # Get shot name
            shot_name = RenderLayer(layer_name).return_shot_name(button)

            # Check the status of all shot's layers and toggle the icon for the parent shot
            button.clicked.connect(partial(self.set_shot_buttons_indicator_color))

            # Change the layer's button to reflect current state
            button.clicked.connect(partial(self.toggle_layer_aov_mode_status, button, shot_name, layer_name))

    def aov_mode_init_layer_button(self, button_name="aov_button"):

        # Get AOV buttons for all the layers
        buttons = self.return_shot_children_by_name(button_name, None)
        data = util.shot_data_directory()

        for button in buttons:
            button: QToolButton

            layer_name = RenderLayer.return_layer_name(button)
            shot_name = RenderLayer(layer_name).return_shot_name(button)

            layers_list = data[shot_name]["render_layers"]
            layer_dict = data[shot_name]["layers"][layer_name]

            # Get AOVs list for the layer
            if layer_dict:

                # If the layer dictionary exists - in case it's an old file or there's an error updating
                for _ in layers_list:
                    aov_mode = layer_dict.get("AOV mode")

                    # Old files had different values for the AOVs key
                    if aov_mode is None or type(aov_mode) is not int:
                        print("This is an old file and there's no AOVs entry in the data file.")
                        pass

                    # Set checked state for each button based on the AOVs value
                    else:

                        if aov_mode == 1:
                            button.setChecked(True)

                        else:
                            button.setChecked(False)

                        self.toggle_layer_icon_and_tooltip(button)

    def toggle_layer_aov_mode_status(self, button: QToolButton, shot: str, layer: str):
        """Retrieves the .isChecked() status of the button, toggles the icon based on the value, updates the data file
            with the new value and calls the function to toggle the renderable attribute in the scene.

            Args:
                button: instance of the shot's QToolButton
                shot: name of the shot
                layer: name of layer that's being edited

        """

        status = bool(self.return_status(button))

        self.toggle_layer_icon_and_tooltip(button)

        # Save the renderable status to JSON file

        layer_dict = self.data[shot]["layers"][layer]
        layer_dict.update({"AOV mode": status})

        self.write_data(self.data)

        self.aov_mode_set_layer_override(status, layer)

    def aov_mode_reset_layers(self, parent_button: QToolButton, button: QToolButton):
        """Retrieves the .isChecked() status of the button, toggles the icon based on the value, updates the data file
            with the new value and updates the AOV render mode in the scene.

            Args:
                parent_button: instance of shot's QCheckBox
                button: instance of the layer's QCheckBox
        """

        layer_name = RenderLayer.return_layer_name(button)
        button_status = parent_button.isChecked()

        button.setChecked(button_status)

        self.toggle_layer_icon_and_tooltip(button)
        self.aov_mode_set_layer_override(button_status, layer_name)

    @staticmethod
    def aov_mode_set_layer_override(button_status: bool, layer: str):
        """ Checks the checked status of a layer's AOV button. Set's the AOVs key value in the dictionary and sets
        the correct Maya override for the layer.

        Args:
            button_status (bool): on or off
            layer (str): name of the render layer
        """

        # Update the key:value pair in the dictionary
        RenderLayer(layer).update_field("AOV mode", button_status)

        # Set the correct override value inside Maya
        plug = "redshiftOptions"
        attrib = "aovGlobalEnableMode"
        mode = button_status

        util.edit_overrides(layer, attrib, mode, plug)

    #############################
    # ---------> AOVs <----------
    #############################

    def aov_init_layer_buttons(self, button_name):
        """Toggles the layer icons based on its dictionary entries."""

        # Get AOV buttons for all the layers
        buttons = self.return_shot_children_by_name(button_name, None)
        data = util.shot_data_directory()

        for button in buttons:
            button: QToolButton

            layer_name = RenderLayer.return_layer_name(button)
            shot_name = RenderLayer(layer_name).return_shot_name(button)

            layers_list = data[shot_name]["render_layers"]
            layer_dict = data[shot_name]["layers"][layer_name]

            # Get AOVs list for the layer
            if layer_dict:

                # If the layer dictionary exists - in case it's an old file or there's an error updating
                for _ in layers_list:
                    aovs = layer_dict.get("AOVs")

                    # Old files had different values for the AOVs key
                    if aovs is None or type(aovs) is not list:
                        print("This is an old file and there's no AOVs entry in the data file.")
                        pass

                    # Set checked state for each button based on the AOVs value
                    else:

                        aov_name = button_name.split("_")[1]

                        if aov_name and aov_name in aovs:
                            button.setChecked(True)

                        else:
                            button.setChecked(False)

                        self.toggle_layer_icon_and_tooltip(button)

    def aov_connect_layer_button(self, button_name):
        """Toggles the icon and AOV render mode for all the layers in the shot."""

        # Get AOV buttons for all the layers
        buttons = self.return_shot_children_by_name(button_name, None)

        for button in buttons:

            button: QToolButton

            layer = RenderLayer.return_layer_name(button)
            shot_name = RenderLayer(layer).return_shot_name(button)
            shot = self.root.treeWidget().findChild(Shot, shot_name)
            shot_widget = self.return_respective_type(shot, self.root, "QTreeWidgetItem")
            parent_button = shot.__getattribute__(button_name)

            # Connect the button to toggle the layer's icon, checked state and update it in the JSON
            button.clicked.connect(partial(self.aov_toggle, button))
            button.clicked.connect(partial(self.toggle_shot_icon_and_tooltip, shot_widget, parent_button, button_name))

    def aov_toggle(self, button: QToolButton):
        """Retrieves the .isChecked() status of the button, toggles the icon based on the value, updates the data file
            with the new value and updates the AOVs in the scene.

            Args:
                button: instance of the layer's QToolButton
        """

        # Get checked state of the button
        button_status = self.return_status(button)

        # Get button name
        button_name = button.objectName()

        # Get the button's Render Layer name
        layer_name = RenderLayer.return_layer_name(button)

        # Get the AOV type
        mode_name = button_name.split("_")[1]

        # Toggle icons for all layers based on Shot's icon
        self.toggle_layer_icon_and_tooltip(button)

        if button_status:
            override_value = 1

        else:
            override_value = 0

        try:
            util.create_aov_and_override_enabled(layer_name, mode_name, override_value)
        except RuntimeError:    # AOVs are missing
            print(f"AOVs missing.")

        # Update the key: value pair in the dictionary

        mode = [mode_name, override_value]

        RenderLayer(layer_name).update_field("AOVs", mode)

    #################################
    # ---------> RENAMING <----------
    #################################

    def show_edit_menu(self):

        buttons = self.return_widgets_by_name(self.root, "edit_button")

        for button in buttons:
            button.customContextMenuRequested.connect(partial(self.create_context_edit_menu, button))

    def create_context_edit_menu(self, button, position):

        # Get shot name
        shot_name = Shot.return_shot_name(button)

        # Create the context menu for edit button
        context_menu = QMenu(self)

        # Create actions for the context menu
        action_rename = QAction("Rename", self)
        action_change_color = QAction("Change shot color", self)

        # Add the actions to the context menu
        context_menu.addAction(action_rename)
        context_menu.addAction(action_change_color)

        # Connect the actions to their respective functions
        action_rename.triggered.connect(lambda: self.rename_shot(shot_name))
        action_change_color.triggered.connect(lambda: self.show_color_dialog(shot_name))

        context_menu.exec_(button.mapToGlobal(position))

    def rename_shot(self, shot):

        existing_shots = util.get_shots()
        data = util.shot_data_directory()  # JSON data file directory
        layer_list = data[shot]["render_layers"]
        new_name, ok = QInputDialog().getText(self, "Rename shot", "New name (match pattern)", text="s000")

        if new_name and ok:

            if not re.match(r'^s\d\d\d$', new_name):

                mc.warning("Wrong format. New name must follow s000 pattern.")
                self.rename_shot(shot)

            elif new_name in existing_shots:
                mc.warning("Shot " + new_name + " already exists!")
                self.rename_shot(shot)

            else:

                self.rename_dict_items(shot, new_name)
                Shot(new_name).update_shot_widgets(data)

                for layer in layer_list:

                    if shot in layer:
                        new_layer_name = layer.replace(shot, new_name)
                        RenderLayer(layer).update_layer_widgets(new_name, new_layer_name)

                util.rename_shot_elements(shot, new_name)
                self.deleteLater()
                self.show_ui()

    def rename_dict_items(self, old_name, new_name):
        """Replaces all instances of the old name with the new name.

            Args:
                old_name (str): name of the shot to be replaced
                new_name (str): name of the new shot

        """
        data = util.shot_data_directory()

        existing_layers = data[old_name]["render_layers"]  # Layers currently in the .json
        renamed_layers = []

        for e_layer in existing_layers:

            layer_suffix = e_layer[4:]  # Remove the shot name from the layer name
            new_layer = new_name + layer_suffix  # Add new shot name to the layer name
            renamed_layers.append(new_layer)  # Add new name of the layer to the list

            layer_dict = data[old_name]["layers"][e_layer]

            for k, v, in layer_dict.copy().items():  # Loop over layers' dictionaries and update their names

                if k == "name":
                    layer_dict["name"] = new_layer

            data[old_name]["layers"][new_layer] = data[old_name]["layers"].pop(e_layer)

        data[old_name][
            "render_layers"] = renamed_layers  # Replace the list in the .json with updated layer names

        # Update the main shot entry

        data[new_name] = data.pop(old_name)  # Replace the shot name in the .json
        data[new_name]["name"] = new_name  # Update the "name" value of the shot in .json

        # Update view
        # Write data to JSON file in a separate thread

        with open(self.data_file_directory, "w") as data_dump:
            json.dump(data, data_dump, indent=4)

    ##########################################
    # ---------> WIDGET MANAGEMENT <----------
    ##########################################

    def return_child_widgets(self, parent, child_class: str):
        """ Returns a list of QTreeWidgetsItems. Function loops over all children and appends
        them to the list. A parent can be either a QTreeWidget root, which returns top level items or
        a QTreeWidgetItem, which returns second level items.

            Args:
                parent (QTreeWidgetItem) = QTreeWidgetItem, container of the shot/layer.
                child_class : Class of the children to be listed, either QTreeWidget, Shot or RenderLayer

        """

        child_list = []

        if child_class == "QTreeWidgetItem":

            if parent.__class__.__name__ == "Shot":
                parent = self.return_respective_type(parent, self.root, "QTreeWidgetItem")

            for index in range(0, parent.childCount()):
                tree_item: QTreeWidgetItem = parent.child(index)  # QTreeWidgetItem

                child_list.append(tree_item)

        elif child_class == "Shot" or child_class == "RenderLayer":

            for index in range(0, parent.childCount()):
                tree_item: QTreeWidgetItem = parent.child(index)  # QTreeWidgetItem

                widget_item = self.tree_object.itemWidget(tree_item, 0)  # A Shot or RenderLayer item

                child_list.append(widget_item)

        return child_list

    def return_widgets_by_name(self, parent: ShotManager.root | QTreeWidgetItem, widget_name):
        """ Returns a list of named widgets of the given parent.

            Args:
                parent (Shot or RenderLayer class object)
                widget_name (str) : Name of the Qt object

        """

        named_widget_list = []

        if parent.__class__.__name__ == "Shot":
            parent = self.return_respective_type(parent, self.root, "QTreeWidgetItem")

        for index in range(0, parent.childCount()):
            tree_item: QTreeWidgetItem = parent.child(index)  # QTreeWidgetItem
            widget_item: Shot | RenderLayer = self.tree_object.itemWidget(tree_item, 0)  # A Shot/Layer class item
            widget = widget_item.__getattribute__(widget_name)
            named_widget_list.append(widget)

        return named_widget_list

    def return_shot_children_by_name(self, widget_name: str, shot_name: str or None):
        """Retrieve the list of widgets with given name.

            Args:
                widget_name (str) = Name of the Qt object
                shot_name (str): (Optional) Name of the shot, to return only shot layers

            Returns:
                button_widgets (list) : A list of widgets with the given widget_name
        """

        # Get all existing shots
        shots = self.return_child_widgets(self.root, "QTreeWidgetItem")

        # Create an empty list for ALL layer buttons with the given widget_name
        all_button_widgets = []

        # Loop over all existing shots
        for shot_widget in shots:

            # Create an empty list for layer buttons with the given name for the given shot name
            button_widgets = []
            child_count = shot_widget.childCount()

            # Loop over the layer buttons
            for index in range(0, child_count):

                layer_widget: QTreeWidgetItem = shot_widget.child(index)
                layer: RenderLayer = self.shotList_treeWidget.itemWidget(layer_widget, 0)

                # Get the name of the shot for each widget
                shot = self.return_respective_type(shot_widget, self.root, "Shot")

                # If the name is the same as the given shot name, add those buttons to the button_widgets list
                s_name = shot.shot_name

                if widget_name is not None:

                    button = layer.__getattribute__(widget_name)  # QObject, parameter of Render Layer

                    if shot_name == s_name:
                        button_widgets.append(button)
                        all_button_widgets.append(button)

                    else:
                        all_button_widgets.append(button)

            if shot_name:
                return button_widgets

        if not shot_name:
            return all_button_widgets

    def return_buttons_status_list(self, parent, widget_name):
        """ Returns a list of .checked state for all layers' buttons with a given widget name for the given parent.

            Args:
                parent (ShotManager.root | Shot | RenderLayer): Instance of the parent object
                widget_name (str): Name of the widget
        """

        widget_status_list = []

        for index in range(0, parent.childCount()):

            tree_item: QStandardItem = parent.child(index)  # QTreeWidgetItem
            parent_widget: Shot | RenderLayer = self.tree_object.itemWidget(tree_item, 0)  # A Shot/Layer class item
            widget = parent_widget.__getattribute__(widget_name)

            widget_status = parent_widget.return_button_checked_state(widget)

            widget_status_list.append(widget_status)

        return widget_status_list

    def return_layer_widgets_by_name(self, widget_name):
        """Returns a list of widgets with given name and their parent for all layers.

            Args:
                widget_name (str) = Name of the Qt object
        """

        shot_widget_list = self.return_child_widgets(self.root, "QTreeWidgetItem")
        button_widgets = []

        tree_object = self.shotList_treeWidget

        for shot_widget in shot_widget_list:

            num_of_layers = shot_widget.childCount()

            for index in range(0, num_of_layers):

                layer_widget: QTreeWidgetItem = shot_widget.child(index)
                layer: RenderLayer = tree_object.itemWidget(layer_widget, 0)

                if widget_name is not None:

                    button = layer.__getattribute__(widget_name)  # QObject, parameter of Render Layer
                    button_widgets.append([button, shot_widget])

                else:

                    button_widgets = []

        return button_widgets

    def return_respective_type(self, item, parent: ShotManager.root | QTreeWidgetItem, type_out: str):

        widgets = self.return_child_widgets(parent, "QTreeWidgetItem")
        shot_items = self.return_child_widgets(parent, "Shot")
        layers = self.return_child_widgets(parent, "RenderLayer")

        type_in = item.__class__.__name__

        item_out = None

        if type_in == "QTreeWidgetItem" and type_out == "Shot":

            index = widgets.index(item)
            item_out = shot_items[index]

        elif type_in == "QTreeWidgetItem" and type_out == "RenderLayer":

            index = widgets.index(item)
            item_out = layers[index]

        elif type_in == "Shot":

            index = shot_items.index(item)
            item_out = widgets[index]

        elif type_in == "RenderLayer":

            index = layers.index(item)
            item_out = widgets[index]

        return item_out

    ##############################
    # ---------> REMOVE <---------
    ##############################

    def delete_shot(self):
        """Shows a pop-up window to confirm their choice."""

        buttons = self.return_widgets_by_name(self.root, "delete_button")
        top_widgets = self.return_child_widgets(self.root, "QTreeWidgetItem")

        for b in buttons:
            index = buttons.index(b)
            parent_widget = top_widgets[index]
            shot_name = Shot.return_shot_name(b)

            b.clicked.connect(partial(self.confirm_shot_removal, shot_name, parent_widget, b))

    def delete_layer(self, button_name="delete_button"):
        """Deletes the render layer inside Maya and in the model."""

        delete_buttons = self.return_layer_widgets_by_name(button_name)

        for b in delete_buttons:
            delete_button = b[0]
            layer_name = RenderLayer.return_layer_name(delete_button)

            delete_button.clicked.connect(partial(self.confirm_layer_removal, layer_name, delete_button))

    def delete_all_shot_layers(self, parent: QTreeWidgetItem):
        """Checks the parent for child widgets and removes all the render layers in Maya scene based on the widget
        names.

        Args:
            parent (QTreeWidgetItem): Parent widget (top level item)

        """

        layer_items = self.return_child_widgets(parent, "RenderLayer")
        layer_widgets = self.return_child_widgets(parent, "QTreeWidgetItem")
        shot_widgets = self.return_child_widgets(self.root, "QTreeWidgetItem")

        if parent in shot_widgets:

            children = self.return_child_widgets(parent, "QTreeWidgetItem")

            for c in children:
                c: QTreeWidgetItem
                index = layer_widgets.index(c)
                layer_item = layer_items[index]
                layer_name = layer_item.objectName()
                util.delete_render_layer(layer_name)

    def remove_shot_widget(self, button: QToolButton):
        """ Removes the widget from the tree.

        Args:
            button (QToolButton) : An instance of the Remove button.
        """

        shot_widgets = self.return_child_widgets(self.root, "QTreeWidgetItem")
        shots = self.return_child_widgets(self.root, "Shot")

        frame_widget: QFrame = button.parent()  # QFrame containing the pressed remove button

        widget: Shot = frame_widget.parent()  # Shot item containing the QFrame

        widget_name = widget.objectName()  # Name of the Shot ie s050

        index = shots.index(widget)  # Int index of the Shot in the widget list

        # Remove items from Model

        self.data.pop(widget_name)

        self.write_data(self.data)

        # Remove items from View

        try:

            item_to_remove: QTreeWidgetItem = shot_widgets[index]

        except RuntimeError:

            item_to_remove: QTreeWidgetItem = shot_widgets[index + 1]

        self.root.removeChild(item_to_remove)
        self.root.removeChild(QTreeWidgetItem(item_to_remove).parent())

        self.set_up_model(self.data)

        self.shotList_treeWidget.update()

    def remove_layer_widget(self, button: QToolButton):
        """ Removes the widget from the tree.

        Args:
            button (QToolButton) : An instance of the Remove button.

        """

        delete_buttons = self.return_layer_widgets_by_name("delete_button")
        new_data = self.data

        for b in delete_buttons:

            delete_button: QToolButton = b[0]

            if button == delete_button:
                parent_shot_widget: QTreeWidgetItem = b[1]  # Shot container
                layer = RenderLayer.return_parent(delete_button)
                layer_widget: QTreeWidgetItem = self.return_respective_type(layer, parent_shot_widget,
                                                                            "QTreeWidgetItem")
                parent_shot_widget.removeChild(layer_widget)

                # Remove items from Model

                layer_name = RenderLayer.return_layer_name(delete_button)
                shot_name = RenderLayer(layer_name).return_shot_name(button)
                layers = self.data[shot_name]["render_layers"]
                new_layer_list = [layer for layer in layers if layer != layer_name]
                new_data[shot_name]["render_layers"] = new_layer_list
                new_data[shot_name]["layers"].pop(layer_name)

                self.write_data(new_data)

    ###############################
    # ---------> UTILITY <---------
    ###############################

    def add_render_layer_widget(self):
        """ Update model view with the newly created layers. """

        selection = self.get_selection()
        existing_layers = []

        for sel in selection:

            shot_widget: QTreeWidgetItem = sel[2]
            shot_name = sel[0]

            layers = self.return_child_widgets(shot_widget, "RenderLayer")

            for each_layer in layers:  # Check which layers are already widgets

                existing_layers.append(each_layer.objectName())

            layer_list = self.data[shot_name]["render_layers"]
            layer_color = self.data[shot_name]["color"]

            new_layers = [layer for layer in layer_list if layer not in existing_layers]

            # Create layers per shot

            for layer in new_layers:
                child_item = QTreeWidgetItem()
                shot_widget.addChild(child_item)

                new_layer_instance = RenderLayer(layer)
                new_layer_instance.update_layer_widgets(shot_name, layer)
                new_layer_instance.setObjectName(layer)
                new_layer_instance.render_button.setChecked(True)

                self.shotList_treeWidget.setItemWidget(child_item, 0, new_layer_instance)
                Shot.apply_frame_style(new_layer_instance, layer_color)
                child_item.setSizeHint(0, QSize(440, 60))

            self.set_layer_renderable()
            self.update_layer_count(shot_name, str(len(layer_list)))

    def get_selection(self):

        active_selection = []
        selection = self.shotList_treeWidget.selectedItems()

        for tree_widget in selection:
            index = self.shotList_treeWidget.indexFromItem(tree_widget, 0)
            item = self.shotList_treeWidget.indexWidget(index)
            shot_name = item.objectName()
            active_selection.append([shot_name, index, tree_widget])

        return active_selection

    def update_layer_count(self, shot, count):

        count_labels = self.return_widgets_by_name(self.root, "layers_label")

        for label in count_labels:

            if shot in label.objectName():
                label: QLabel
                label.setText(count + " layers")

    ##########################################
    # ---------> ADDITIONAL DIALOGS <---------
    ##########################################

    def show_color_dialog(self, shot_name):
        """
        Function to show a color dialog where the user can choose the color of the shot.
        The selected color will be applied to the shot and all layers.
        """

        # Define the colors and their corresponding icons
        button_dict = util.return_resource_dict("BUTTON_ICONS")
        colors = button_dict["color_button"]

        dialog = QDialog()
        dialog.setWindowTitle("Choose Color")
        dialog.setFixedSize(400, 80)
        layout = QGridLayout(dialog)

        light_group = "_".join([f"{shot_name}", "light"])
        camera_group = "_".join([f"{shot_name}", "camera"])
        layers = self.data[shot_name]["render_layers"]

        # Create a tool button for each color
        for col, color_name in enumerate(colors.keys()):

            icon, tooltip = util.return_icon_and_tooltip("color_button", color_name)

            color_button = QToolButton(dialog)
            color_button.setIcon(icon)
            color_button.setToolTip(tooltip)
            color_button.setIconSize(QSize(32, 32))

            color_button.clicked.connect(partial(Shot(shot_name).update_field, "color", color_name))
            color_button.clicked.connect(partial(util.set_outliner_color, shot_name, light_group))
            color_button.clicked.connect(partial(util.set_outliner_color, shot_name, camera_group))
            color_button.clicked.connect(partial(util.change_layer_color, layers, color_name))

            color_button.clicked.connect(partial(dialog.hide))
            color_button.clicked.connect(lambda: self.deleteLater())
            color_button.clicked.connect(lambda: self.show_ui())

            layout.addWidget(color_button, 0, col)

        dialog.exec_()

    def confirm_shot_removal(self, shot_name: str, parent_widget: QTreeWidgetItem, button: QToolButton):
        """Accepting the prompt will remove the shot from the scene; shot-specific set, lights group, camera,
        render layers will be removed and the model will be updated to reflect these changes.

            Args:
                shot_name (str): name of the shot
                parent_widget (QTreeWidgetItem): The widget container of the shot.
                button (QToolButton): Instance of the remove button that was pressed.
        """

        message_text = "Have you thought this through? Are you sure you want to delete this shot?\n\nThe " \
                       "following will be deleted for this shot:\n\nShot-specific set\nCamera\nLights\nRender layers"

        confirm_window = QtWidgets.QMessageBox()
        confirm_window.setWindowTitle("Remove shot")
        confirm_window.setInformativeText(message_text)
        confirm_window.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        confirm_window.setWindowModality(Qt.WindowModality.ApplicationModal)
        confirm_window.exec()

        if confirm_window.accepted:
            try:
                util.delete_shot_elements(shot_name)
                self.delete_all_shot_layers(parent_widget)
            except NameError:       # Maya not loaded
                pass
            self.remove_shot_widget(button)
        else:
            print("Rejected")

    def confirm_layer_removal(self, layer_name: str, button: QToolButton):
        """Accepting the prompt will remove the shot from the scene; shot-specific set, lights group, camera,
        render layers will be removed and the model will be updated to reflect these changes.

            Args:
                layer_name (str): name of the layer
                button (QToolButton): Instance of the remove button that was pressed.
        """

        message_text = "Do you want to delete this render layer?"

        confirm_window = QtWidgets.QMessageBox()
        confirm_window.setWindowTitle("Remove layer")
        confirm_window.setInformativeText(message_text)
        confirm_window.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        confirm_window.accepted.connect(QMessageBox.accept(confirm_window))
        confirm_window.accepted.connect(partial(util.delete_render_layer, layer_name))
        confirm_window.accepted.connect(partial(self.remove_layer_widget, button))
        confirm_window.accepted.connect(lambda: print("Layer removed."))

        confirm_window.rejected.connect(QMessageBox.reject(confirm_window))
        confirm_window.rejected.connect(lambda: print("Rejected"))

        confirm_window.setWindowModality(Qt.WindowModality.ApplicationModal)
        confirm_window.exec()
