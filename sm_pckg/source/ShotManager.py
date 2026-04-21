import sys
from functools import partial
import re
import json

from PySide6.QtCore import (
    Qt,
    QModelIndex, 
    QItemSelectionModel, 
    QAbstractItemModel,
    QModelIndex,
    QSize
)

from PySide6.QtWidgets import (
    QDialog,
    QTreeWidgetItem,
    QFrame,
    QHeaderView,
    QLineEdit,
    QToolButton,
    QLabel,
    QMessageBox,
    QInputDialog,
    QMenu,
    QGridLayout
)

from PySide6.QtGui import (
    QStandardItemModel,
    QAction,
    QIcon,
    QStandardItem
    
)

try:
    import maya.cmds as mc # pyright: ignore[reportMissingImports]

except ModuleNotFoundError:  # Local testing
    pass

import source.util as util
from source.util_paths import Path as path
from ui.ui_manager import ShotManagerWindow
from source.custom_widgets import Shot, RenderLayer, ShotManagerDelegate
from source.creators import LayerCreator, ShotCreator
from source.model import data_model

class ShotManager(ShotManagerWindow):   # pylint: disable=too-many-public-methods
    """Class containing the main UI with all functionality for iterating
    through shot's render layers and syncing widget status with the JSON file.
    """

    # Get window's parent
    try:
        parent = util.get_maya_window()  # type: ignore
    except NameError:
        pass

    manager_instance = None     # maintain a single instance of the dialog in Production

    def __init__(self, parent=None):
        super().__init__(parent)

        self.data = data_model.data      # Returns the dictionary inside JSON
        #self.data_file = path.return_data_filepath()  # Path to data file
        #self.data_directory = path.return_sm_dir()  # Path to data folder
        self.style_sheet = util.load_frame_style()
        self.setup_ui(self)

        # Create the model
        self.model = QStandardItemModel()

        # Apply the Delegate
        self.delegate = ShotManagerDelegate(self.tree_view)
        self.tree_view.setItemDelegate(self.delegate)

        # Apply the model
        self.set_model()
        self.root = self.model.invisibleRootItem()
        self.populate_model(self.data)

        self.connect_signals()
        self.check_existing_widgets()
        self.get_selection()
    # Connect button functionality
    def connect_signals(self):
        """ Connects all button signals to their respective functions.
        """

        # pylint: disable=unnecessary-lambda
        self.newShot_button.clicked.connect(lambda: self.show_shot_creator())
        self.newLayer_button.clicked.connect(lambda: self.get_selection())
        self.newLayer_button.clicked.connect(lambda: self.show_layer_creator())
        self.tree_view.selectionModel().selectionChanged.connect(lambda selected, deselected: self.get_selection())
        #self.model.itemChanged.connect(lambda: self.set_model())

        """self.set_shot_visibility()
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
        self.show_edit_menu()"""

    def init_maya(self):
        """ Method checks if the initial Maya setup is correct.
            It sets Redshift as rendered, 25 fps and creates the necessary
            structure for the Shot Manager inside Maya. """

        # Runs in Maya only
        if util.maya_is_loaded():

            util.set_redshift_renderer()
            util.set_correct_fps()
            util.create_default_groups()
            util.create_global_sets()
            util.create_global_rs_sets()

        else:
            print("Maya hasn't been loaded yet.")

    # Windows display

    @classmethod
    def show_ui(cls):
        """Show Shot Manager Window."""

        if cls.manager_instance:
            cls.manager_instance.close()
            cls.manager_instance.deleteLater()

        cls.manager_instance = ShotManager()
        cls.manager_instance.show()

    def show_shot_creator(self):
        """Shows the Shot Builder Dialog."""

        # pylint: disable=unnecessary-lambda
        shot_creator = ShotCreator(self)
        shot_creator.add_shots_button.clicked.connect(lambda : self.populate_model(self.data))
        shot_creator.add_shots_button.clicked.connect(lambda: print("SM Show Shot Builder ", id(self.data)))
        shot_creator.show()


    def show_layer_creator(self):
        """Shows the Layer Creator Dialog."""

        # pylint: disable=unnecessary-lambda
        layer_creator = LayerCreator(self)
        
        layer_creator.createLayers_button.clicked.connect(
            lambda: layer_creator.add_layers_to_data(self.get_selection()))
        
        layer_creator.createLayers_button.clicked.connect(lambda: self.populate_model(self.data))
        #layer_creator.createLayers_button.clicked.connect(lambda: self.add_render_layer_widget())
        layer_creator.createLayers_button.clicked.connect(lambda: layer_creator.accept())
        layer_creator.show()

    #############################################
    # -----------> MODEL MANAGEMENT <----------- #
    #############################################

    def set_model(self):
        """ Sets the QStandardItemModel to the existing QTreeView. """

        # Set the model to the view BEFORE opening editors
        if self.tree_view.model() != self.model:
            self.tree_view.setModel(self.model)
            # Ensure the first column stretches to fill the available width
            self.tree_view.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            self.tree_view.setIndentation(20)

    def check_existing_widgets(self):
        """ Returns a list of existing shot widgets in the tree."""

        item_list = []

        # Get the count of shot items in the model
        count = self.model.rowCount()
        for i in range(count):
            item = self.model.index(i, 0, QModelIndex())
            shot = item.data(role=Qt.ItemDataRole.DisplayRole)
            item_list.append(shot)
        return item_list

    def populate_model(self, data: dict):
        """ Reads in the JSON file and applies the view to the model.
            Args:
                data (dict) : A JSON file containing shot information. """

        shot_list = sorted(list(data.keys()))

        for shot_name in shot_list:
            # Find the shot item in the model
            shot_item = None
            for i in range(self.model.rowCount()):
                item = self.model.item(i)
                if item.text() == shot_name:
                    shot_item = item
                    break

            # Create shot item if missing
            if not shot_item:
                shot_item = QStandardItem(shot_name)
                shot_item.setData("Shot", Qt.ItemDataRole.UserRole + 1)
                self.root.appendRow(shot_item)
                self.tree_view.openPersistentEditor(self.model.indexFromItem(shot_item))

            # Sync layers for this shot
            layer_list = sorted(data[shot_name].get("render_layers", []))
            existing_layers = [shot_item.child(j).text() for j in range(shot_item.rowCount())]

            for layer_name in layer_list:
                if layer_name not in existing_layers:
                    layer_item = QStandardItem(layer_name)
                    layer_item.setData("RenderLayer", Qt.ItemDataRole.UserRole + 1)
                    layer_item.setData(shot_name, Qt.ItemDataRole.UserRole + 2)
                    shot_item.appendRow(layer_item)
                    self.tree_view.openPersistentEditor(self.model.indexFromItem(layer_item))

        self.tree_view.expandAll()
        

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

        elif child_class in ["Shot", "RenderLayer"]:

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
            widget = widget_item.return_child_widget(widget_name)
            named_widget_list.append(widget)

        return named_widget_list

    def return_shot_children_by_name(self, widget_name: str, shot_name: str or None):
        """Retrieve the list of layer widgets with given name.

            Args:
                widget_name (str) = Name of the Qt object
                shot_name (str): (Optional) Name of the shot, to return only shot widgets

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
                layer: RenderLayer = self.tree_view.itemWidget(layer_widget, 0)

                # Get the name of the shot for each widget
                shot = self.return_respective_type(shot_widget, self.root, "Shot")

                # If the name is the same as the given shot name, add those buttons to the button_widgets list
                s_name = getattr(shot, "shot_name")

                button = layer.return_child_widget(widget_name)  # QObject, parameter of Render Layer

                if shot_name == s_name and shot_name is not None:
                    button_widgets.append(button)
                    return button_widgets

                all_button_widgets.append(button)

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
            widget = parent_widget.return_child_widget(widget_name)

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

        tree_object = self.tree_view

        for shot_widget in shot_widget_list:

            num_of_layers = shot_widget.childCount()

            for index in range(0, num_of_layers):

                layer_widget: QTreeWidgetItem = shot_widget.child(index)
                layer: RenderLayer = tree_object.itemWidget(layer_widget, 0)

                if widget_name is not None:

                    button = layer.return_child_widget(widget_name)  # QObject, parameter of Render Layer
                    button_widgets.append([button, shot_widget])

                else:

                    button_widgets = []

        return button_widgets

    def return_respective_type(self, item, parent, type_out):
        """Returns desired object type for the item.
        Args:
            item(QTreeWidgetItem | Shot | Render Layer): object pointer
            parent(ShotManager.root | QTreeWidgetItem): Depending if the object is a shot (parent=root)
                                                        or a layer (parent=QTreeWidgetItem)
            type_out(str): returns the exact name for the shot's output object type
        """

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
                new_layer_instance = RenderLayer(layer) # This is fine
                new_layer_instance.update_widget_name_value(shot_name, layer)
                new_layer_instance.setObjectName(layer)
                new_layer_instance.render_button.setChecked(True)

                self.tree_view.setItemWidget(child_item, 0, new_layer_instance)
                CustomQTreeWidgetItem.apply_frame_style(new_layer_instance, layer_color)
                child_item.setSizeHint(0, QSize(440, 60))


            self.set_layer_renderable()
            self.update_layer_count(shot_name, str(len(layer_list)))

    def get_selection(self):
        """ Returns currently selected items in the tree view. """

        active_selection = []

        for index in self.tree_view.selectionModel().selectedIndexes():
            item = self.model.index(index.row(), index.column(), index.parent())
            shot = item.data(role=Qt.ItemDataRole.DisplayRole)
            print(shot)
            active_selection.append(shot)
        return active_selection

    def update_layer_count(self, shot, count):
        """Updates the number of layers on the Shot widget.

        Args:
            shot(str): name of the shot
            count(str): number of layers
        """

        count_labels = self.return_widgets_by_name(self.root, "layers_label")

        for label in count_labels:

            if shot in label.objectName():
                label: QLabel
                label.setText(count + " layers")
