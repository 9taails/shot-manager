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
        """Toggle icon and checked status on the shot-level buttons.
        Args:
        button_name (str): name of the button
        """
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
                button_name = button.objectName() # This is fine, button is a QToolButton
                try:
                    self.toggle_shot_icon_and_tooltip(shot_widget, button, button_name)
                except AttributeError:      # Sometimes, it can't find the button on init
                    pass
                except KeyError:        # For non-toggable buttons
                    pass

    def reset_layers(self, shot_widget, parent_button, button_name):
        """ Loops over all shot's layers icons and toggles the checked status of all
        those icons to the same status the shot icon has. Used in resetting all
        frame range overrides on layers and setting renderable status on all shot
        layers at once.

            Args:
                shot_widget (QTreeWidgetItem): container of Shot
                parent_button (QToolButton): attrib of Shot
                button_name (str): name of the button
        """

        shot = self.return_respective_type(shot_widget, self.root, "Shot")
        shot_name = shot.shot_name

        layer_buttons = self.return_shot_children_by_name(button_name, shot_name)
        status = self.return_status(parent_button)

        for b in layer_buttons:

            layer_name = RenderLayer.return_layer_name_by_widget(b)
            layer_name = CustomWidgetBase.get_widget_name_from_child(b) # Use static helper method

            if isinstance(b, QToolButton):

                # Set check state on all layers' buttons to parent button check state
                b.setChecked(status)

                if button_name == "render_button":

                    self.toggle_layer_renderable_status(b, shot_name, layer_name)

                elif button_name == "frame_range_button":

                    self.reset_frame_range(b)

                elif button_name == "aov_button":

                    self.aov_mode_reset_layers(parent_button, b)

                elif button_name in ["aov_beauty_button", "aov_utility_button"]:

                    aov_group = button_name.split("_")[1]

                    self.aov_toggle(b)
                    util.create_aov_and_override_enabled(layer_name, aov_group, status)

    def toggle_shot_icon_and_tooltip(self, shot_widget, shot_button, button_name):
        """ Function toggles the shot buttons, their icons and tooltips based on
        the checked status of its layers.

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

        icon, tooltip = util.return_icon_tooltip(button_name, status)

        shot_button.setIcon(icon)
        shot_button.setToolTip(tooltip)

    def toggle_layer_icon_and_tooltip(self, button):
        """ Function toggles the shot buttons, their icons and tooltips based on
        the checked status of its layers.

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

        icon, tooltip = util.return_icon_tooltip(button_name, status)

        button.setIcon(icon)
        button.setToolTip(tooltip)

    ####################################
    # ---------> VISIBILITY <----------
    ####################################

    def set_shot_visibility(self, button_name="visibility_button"):
        """Checks the status of all top level visibility buttons and toggles
        the current icon, keeping only one Shot visible at a time.
        """

        shot_widgets = self.return_child_widgets(self.root, "Shot")

        for shot in shot_widgets:
            shot: Shot

            shot_widget = self.return_respective_type(shot, self.root, "QTreeWidgetItem")

            parent_button = shot.return_child_widget(button_name)

            shot_name = shot.return_shot_name(parent_button)
            shot_name = CustomWidgetBase.get_widget_name_from_child(parent_button) # Use static helper method
            layer_name = shot_name + "master"

            self.toggle_shot_icon_and_tooltip(shot_widget, parent_button, button_name)

            parent_button.clicked.connect(partial(Shot(shot_name).toggle_icon, parent_button))
            parent_button.clicked.connect(partial(self.hide_other_shots, parent_button))
            parent_button.clicked.connect(partial(self.hide_other_layers, None))
            parent_button.clicked.connect(partial(util.switch_layer, layer_name))

    def set_layer_visibility(self, button_name="visibility_button"):
        """Toggles the icon and sets the correct render layer as active."""

        buttons = self.return_shot_children_by_name(button_name, None)

        for b in buttons:
            b: QToolButton
            layer_name = RenderLayer.return_layer_name_by_widget(b)

            b.clicked.connect(partial(self.toggle_layer_icon_and_tooltip, b))
            b.clicked.connect(partial(self.hide_other_shots, None))
            b.clicked.connect(partial(self.hide_other_layers, b))
            b.clicked.connect(partial(self.set_shot_visibility))

            if self.maya_is_loaded():
                b.clicked.connect(partial(util.switch_layer, layer_name))

    def toggle_layer_visible_status(self, button: QToolButton):
        """Retrieves the .isChecked() status of the button and toggles the icon based on
        the value.

            Args:
                button: instance of the pressed QToolButton

        """

        status = self.return_status(button)

        if status:

            button.setChecked(True)
            button.setIcon(QIcon(path.icon("icon_visibility_green.png")))
            button.setToolTip("Layer is currently active.")

        else:

            button.setChecked(False)
            button.setIcon(QIcon(path.icon("icon_visibility_off.png")))
            button.setToolTip("Set active layer.")

    def hide_other_shots(self, button: QToolButton, button_name="visibility_button"):
        """Unchecks all the visibility buttons except the current button, so that
        only one shot at a time is highlighted. Additionally, switches the view
        in Maya to current shot, setting the correct playback range and camera.

            Args:
                button (QObject) = A QToolButton, instance of the currently checked button
                button_name: name of the button object
        """

        # Set icon and status for all other buttons

        all_buttons = self.return_widgets_by_name(self.root, button_name)

        off_list = [b for b in all_buttons if b is not button]

        for buttons in off_list:
            buttons.setChecked(False)
            buttons.setIcon(QIcon(path.icon("icon_visibility_off.png")))

    def hide_other_layers(self, button, button_name="visibility_button"):
        """Checks the status of all child level visibility buttons and toggles
        the icon, keeping only one RenderLayer visible at a time. Toggles the
        visibility state of the parent Shot.
        Args:
        button (QToolButton): instance of the clicked button
        """

        layer_buttons = self.return_shot_children_by_name(button_name, None)

        off_layers = [b for b in layer_buttons if b is not button]

        for buttons in off_layers:
            buttons: QToolButton

            buttons.setChecked(False)

            layer_name = RenderLayer.return_layer_name_by_widget(buttons)

            RenderLayer(layer_name).toggle_icon(buttons)

    ####################################
    # ---------> RENDERABLE <----------
    ####################################

    def set_layer_renderable(self, button_name="render_button"):
        """Toggles the icon and sets the correct render layer .renderable
        attribute to reflect the change.
        """

        # Get render buttons for all layers.
        buttons = self.return_shot_children_by_name(button_name, None)

        # Loop over all layer render buttons
        for b in buttons:
            # Get layer name
            layer_name = RenderLayer.return_layer_name_by_widget(b)


            # Get shot name
            shot_name = RenderLayer(layer_name).return_parent_shot(b)
            shot_name = CustomWidgetBase.get_widget_name_from_child(b)[:4] # Get layer name, then slice for shot name

            # Get Shot
            shot = self.root.treeWidget().findChild(Shot, shot_name)


            # Get shot widget of type QTreeWidgetItem
            shot_widget = self.return_respective_type(shot, self.root, "QTreeWidgetItem")

            # Get shot's render button instance
            parent_button = shot.render_button

            # Connect layer buttons
            b.clicked.connect(partial(self.toggle_layer_renderable_status,
                                      b, shot_name, layer_name))
            b.clicked.connect(partial(self.toggle_shot_icon_and_tooltip,
                                      shot_widget, parent_button, button_name))

    def toggle_layer_renderable_status(self, button, shot, layer):
        """Retrieves the .isChecked() status of the button, toggles the icon based on
        the value, updates the data file with the new value and calls the function
        to toggle the renderable attribute in the scene.

            Args:
                button (QToolButton): instance of the shot's QToolButton
                shot (str): name of the shot
                layer (str): name of layer that's being edited
        """

        status = self.return_status(button)

        self.toggle_layer_icon_and_tooltip(button)

        # Save the renderable status to JSON file

        layer_dict = self.data[shot]["layers"][layer]
        layer_dict.update({"renderable": status})

        self.add_to_dict(self.data)

        util.set_layer_renderable(layer, status)

    ####################################
    # ---------> FRAME RANGE <----------
    ####################################

    def on_shot_frame_editing_finished(self):
        """Connects the editing finished on the frame range field
        to function that changes the frame range.
        """

        start_fields = self.return_widgets_by_name(self.root, "start")
        end_fields = self.return_widgets_by_name(self.root, "end")

        edit_fields = start_fields + end_fields

        for widget in edit_fields:
            widget.editingFinished.connect(partial(self.change_global_shot_frame_range, widget))

    def change_global_shot_frame_range(self, field: QLineEdit):
        """ Sets shot frame range and sets all shot layers frame ranges to the same value
        if the layers have no frame range overrides.

            Args:
                field: Shot start or end edit field
        """

        parent = field.parent()  # Get Shot parent of the field widget
        print(self.parent)
        shot_name = Shot.return_shot_name(field) # Get the name of the shot
        shot_value = int(field.text())  # Get the current value of the shot

        shot_field_name = field.objectName()  # ex: shot_start
        field_name = shot_field_name.split("_")[1]  # ex: start

        # Get shot's render layers
        # Get shot's layers' widgets
        layer_edit_widgets = self.return_widgets_by_name(parent, field_name)
        # Get shot's layers' icons
        layer_icons = self.return_widgets_by_name(parent, "frame_range_button")

        # Loop over each layer's edit widget;
        # Get the name of the layer
        # Get the frame icon for the layer and check its status

        for layer_edit_field in layer_edit_widgets: # This needs to be updated to access ui.start/ui.end

            layer_name = RenderLayer.return_layer_name_by_widget(layer_edit_field)

            # Get respective icon and check its status
            index = layer_edit_widgets.index(layer_edit_field)
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
        shot_name = CustomWidgetBase.get_widget_name_from_child(field)[:4] # Get layer name, then slice for shot name

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
                layer_name = RenderLayer.return_layer_name_by_widget(edit_widget)
                layer_name = CustomWidgetBase.get_widget_name_from_child(edit_widget) # Use static helper method

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
                layer_name = RenderLayer.return_layer_name_by_widget(button)
                layer_name = CustomWidgetBase.get_widget_name_from_child(button) # Use static helper method
                RenderLayer(layer_name).toggle_range_icon(button)

    def reset_frame_range(self, button: QToolButton):
        """ Sets shot frame range to all layers under the shot. Frame range is updated
        in both JSON and view.

            Args:
                button: QToolButton instance

        """

        button.setChecked(False)
        icon, tooltip = util.return_icon_tooltip(button.objectName(), "off")

        button.setIcon(icon)
        button.setToolTip(tooltip)

        layer_name = RenderLayer.return_layer_name_by_widget(button)
        layer_name = CustomWidgetBase.get_widget_name_from_child(button) # Use static helper method
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

        self.add_to_dict(self.data)

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
            layer_name = RenderLayer.return_layer_name_by_widget(button)
            layer_name = CustomWidgetBase.get_widget_name_from_child(button) # Use static helper method

            # Get shot name
            shot_name = RenderLayer(layer_name).return_parent_shot(button)
            shot_name = CustomWidgetBase.get_widget_name_from_child(button)[:4] # Get layer name, then slice for shot name

            # Check the status of all shot's layers and toggle the icon for the parent shot
            button.clicked.connect(partial(self.set_shot_buttons_indicator_color))

            # Change the layer's button to reflect current state
            button.clicked.connect(partial(self.toggle_layer_aov_mode_status, button, shot_name, layer_name))

    def aov_mode_init_layer_button(self, button_name="aov_button"):
        """Sync AOV mode from the JSON file. Options are Enabled, Batch Only, Disabled."""
        # Get AOV buttons for all the layers
        buttons = self.return_shot_children_by_name(button_name, None)
        data = data_model.create_data_file()

        for button in buttons:
            button: QToolButton

            layer_name = RenderLayer.return_layer_name_by_widget(button)
            shot_name = RenderLayer(layer_name).return_parent_shot(button)
            layer_name = CustomWidgetBase.get_widget_name_from_child(button) # Use static helper method
            shot_name = CustomWidgetBase.get_widget_name_from_child(button)[:4] # Get layer name, then slice for shot name

            layers_list = data[shot_name]["render_layers"]
            layers_list = data[shot_name]["render_layers"] # This is fine
            layer_dict = data[shot_name]["layers"][layer_name]

            # Get AOVs list for the layer
            if layer_dict:
                for _ in layers_list:
                    aov_mode = layer_dict.get("AOV mode")

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

        self.add_to_dict(self.data)

        self.aov_mode_set_layer_override(status, layer)

    def aov_mode_reset_layers(self, parent_button: QToolButton, button: QToolButton):
        """Retrieves the .isChecked() status of the button, toggles the icon based on the value, updates the data file
            with the new value and updates the AOV render mode in the scene.

            Args:
                parent_button: instance of shot's QCheckBox
                button: instance of the layer's QCheckBox
        """

        layer_name = RenderLayer.return_layer_name_by_widget(button)
        layer_name = CustomWidgetBase.get_widget_name_from_child(button) # Use static helper method
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
        data = data_model.create_data_file()

        for button in buttons:
            button: QToolButton

            layer_name = RenderLayer.return_layer_name_by_widget(button)
            shot_name = RenderLayer(layer_name).return_parent_shot(button)
            layer_name = CustomWidgetBase.get_widget_name_from_child(button) # Use static helper method
            shot_name = CustomWidgetBase.get_widget_name_from_child(button)[:4] # Get layer name, then slice for shot name

            layers_list = data[shot_name]["render_layers"]
            layers_list = data[shot_name]["render_layers"] # This is fine
            layer_dict = data[shot_name]["layers"][layer_name]

            # Get AOVs list for the layer
            if layer_dict:
                for _ in layers_list:
                    aovs = layer_dict.get("AOVs")

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

            layer = RenderLayer.return_layer_name_by_widget(button)
            shot_name = RenderLayer(layer).return_parent_shot(button)
            shot = self.root.treeWidget().findChild(Shot, shot_name)

            layer = CustomWidgetBase.get_widget_name_from_child(button) # Use static helper method
            shot_name = CustomWidgetBase.get_widget_name_from_child(button)[:4] # Get layer name, then slice for shot name
            shot = self.root.treeWidget().findChild(Shot, shot_name) # This is fine
            shot_widget = self.return_respective_type(shot, self.root, "QTreeWidgetItem")
            parent_button = shot.return_child_widget(button_name)

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
        layer_name = RenderLayer.return_layer_name_by_widget(button)
        layer_name = CustomWidgetBase.get_widget_name_from_child(button) # Use static helper method

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
            print("AOVs missing.")

        # Update the key: value pair in the dictionary

        mode = [mode_name, override_value]

        RenderLayer(layer_name).update_field("AOVs", mode)

    #################################
    # ---------> RENAMING <----------
    #################################

    def show_edit_menu(self):
        """ Display the edit menu on button click. """

        buttons = self.return_widgets_by_name(self.root, "edit_button")

        for button in buttons:
            button.customContextMenuRequested.connect(partial(self.create_context_edit_menu, button))

    def create_context_edit_menu(self, button, position):
        """Create context menu for renaming and changing shot color.

            Args:
            button (QWIdget): instance of the button
            button (QWidget): instance of the button
            position (QPoint) - pointer to the button's position
        """

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
        """Change the name of the shot and its elements.
        Args:
            shot(str): name of the shot
        """

        existing_shots = util.get_shots()
        data = data_model.create_data_file()  # JSON data file directory
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
                        RenderLayer(layer).update_widget_name_value(new_name, new_layer_name)

                util.rename_shot_elements(shot, new_name)
                self.deleteLater()
                self.show_ui()

    def rename_dict_items(self, old_name, new_name):
        """Replaces all instances of the old name with the new name.

            Args:
                old_name (str): name of the shot to be replaced
                new_name (str): name of the new shot

        """
        data = data_model.create_data_file()

        existing_layers = data[old_name]["render_layers"]  # Layers currently in the .json
        renamed_layers = []

        for e_layer in existing_layers:

            layer_suffix = e_layer[4:]  # Remove the shot name from the layer name
            new_layer = new_name + layer_suffix  # Add new shot name to the layer name
            renamed_layers.append(new_layer)  # Add new name of the layer to the list

            layer_dict = data[old_name]["layers"][e_layer]

            for k, _ in layer_dict.copy().items():  # Loop over layers' dictionaries and update their names

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

        with open(self.data_file, encoding="utf-8", mode="w") as data_dump:
            json.dump(data, data_dump, indent=4)

    
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
            parent_widget = top_widgets[index] # This is fine
            shot_name = Shot.return_shot_name(b)

            b.clicked.connect(partial(self.confirm_shot_removal, shot_name, parent_widget, b))

    def delete_layer(self, button_name="delete_button"):
        """Deletes the render layer inside Maya and in the model."""

        delete_buttons = self.return_layer_widgets_by_name(button_name)

        for b in delete_buttons:
            delete_button = b[0]
            delete_button = b[0] # This is fine
            layer_name = RenderLayer.return_layer_name_by_widget(delete_button)

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

        self.add_to_dict(self.data)

        # Remove items from View

        try:

            item_to_remove: QTreeWidgetItem = shot_widgets[index]

        except RuntimeError:

            item_to_remove: QTreeWidgetItem = shot_widgets[index + 1]

        self.root.removeChild(item_to_remove)
        self.root.removeChild(QTreeWidgetItem(item_to_remove).parent())

        self.populate_model(self.data)

        self.tree_view.update()

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

                layer_name = RenderLayer.return_layer_name_by_widget(delete_button)
                shot_name = RenderLayer(layer_name).return_parent_shot(button)
                shot_name = CustomWidgetBase.get_widget_name_from_child(button)[:4] # Get layer name, then slice for shot name
                layers = self.data[shot_name]["render_layers"]
                new_layer_list = [layer for layer in layers if layer != layer_name]
                new_data[shot_name]["render_layers"] = new_layer_list
                new_data[shot_name]["layers"].pop(layer_name)

                self.add_to_dict(new_data)

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

            icon, tooltip = util.return_icon_tooltip("color_button", color_name)

            color_button = QToolButton(dialog)
            color_button.setIcon(icon)
            color_button.setToolTip(tooltip)
            color_button.setIconSize(QSize(32, 32))

            color_button.clicked.connect(partial(Shot(shot_name).update_field, "color", color_name))
            color_button.clicked.connect(partial(util.set_outliner_color, shot_name, light_group))
            color_button.clicked.connect(partial(util.set_outliner_color, shot_name, camera_group))
            color_button.clicked.connect(partial(util.change_layer_color, layers, color_name))

            color_button.clicked.connect(partial(dialog.hide))
            color_button.clicked.connect(lambda: self.deleteLater()) # pylint: disable=unnecessary-lambda
            color_button.clicked.connect(lambda: self.show_ui()) # pylint: disable=unnecessary-lambda

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

        message_text = "Are you sure you want to delete this shot?\n" \
                       f"\nThe following will be deleted for {shot_name}:\n" \
                       "\nSet\nCamera\nLights\nRender layers"

        confirm_window = QMessageBox()
        confirm_window.setWindowTitle("Remove shot")
        confirm_window.setInformativeText(message_text)
        confirm_window.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        confirm_window.setWindowModality(Qt.WindowModality.ApplicationModal)
        confirm_window.exec()

        if confirm_window.accepted:
            try:
                util.delete_shot_elements(shot_name)
                self.delete_all_shot_layers(parent_widget)
            except NameError: # Maya not loaded
                pass
            self.remove_shot_widget(button)
        else:
            print("Rejected")

    def confirm_layer_removal(self, layer_name: str, button: QToolButton):
        """Accepting the prompt will remove the shot from the scene;
        shot-specific set, lights group, camera,render layers will be
        removed and the model will be updated to reflect these changes.

        Args:
            layer_name (str): name of the layer
            button (QToolButton): Instance of the remove button that was pressed.
        """

        message_text = "Do you want to delete this render layer?"

        confirm_window = QMessageBox()
        confirm_window.setWindowTitle("Remove layer")
        confirm_window.setInformativeText(message_text)
        confirm_window.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        confirm_window.accepted.connect(QMessageBox.accept(confirm_window))
        confirm_window.accepted.connect(partial(util.delete_render_layer, layer_name))
        confirm_window.accepted.connect(partial(self.remove_layer_widget, button))
        confirm_window.accepted.connect(lambda: print("Layer removed."))

        confirm_window.rejected.connect(QMessageBox.reject(confirm_window))
        confirm_window.rejected.connect(lambda: print("Rejected"))

        confirm_window.setWindowModality(Qt.WindowModality.ApplicationModal)
        confirm_window.exec()
