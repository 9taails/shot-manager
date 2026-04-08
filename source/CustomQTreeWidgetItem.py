from PySide6.QtGui import (
    QStandardItem
)
from PySide6.QtWidgets import (
    QWidget,
    QToolButton,
)

from ui.Paths import Paths
import source.utilities as util


class CustomQTreeWidgetItem(QWidget, QStandardItem):
    """
    Custom widget representing a shot.

    Attributes:
        data_file_directory (str): The path to the data file.
        frame_styles (dict): Dictionary containing style sheet for QFrame
        style_sheet (dict): Dictionary containing global style sheet

    """

    def __init__(self):
        super().__init__()

        self.shot_name = None
        self.visibility_button = None
        self.data_file_directory = Paths.return_shot_data_full_filepath()  # Path to data file
        self.style_sheet = util.load_style_sheet()
        self.frame_styles = util.load_frame_style()

    def apply_frame_style(self, color):
        """ Applies a style sheet to QFrame button for active/inactive shot.

            Args:
                color (str): color name from the style sheet
        """

        # Get the correct style sheet for the QFrame
        style = self.frame_styles["QFrame"][color]

        # Assign the style sheet
        self.setStyleSheet(style)

    def toggle_style_frame(self):
        """ Reads in the style sheet and applies the correct frame style based on visibility of the shot."""

        data = util.shot_data_directory()
        shot_color = data[self.shot_name]["color"]
        active_color = shot_color + "_active"

        if self.visibility_button.isChecked():

            self.apply_frame_style(active_color)

        else:

            self.apply_frame_style(shot_color)

    @staticmethod
    def return_parent(widget):
        """
        Returns the parent Shot object containing the widget.

        Args:
            widget (QWidget): The widget to find the parent Shot object for.

        Returns:
            shot_widget (Shot): The parent Shot object containing the widget.
        """

        frame_widget = widget.parentWidget()
        parent = frame_widget.parentWidget()

        return parent

    def return_child_widget(self, widget_name):
        """
        Returns the child widget with the given name.

        Args:
            widget_name (str): The name of the child widget to return.

        Returns:
            widget (QWidget): The child widget with the given name.
        """

        widget = self.__getattribute__(widget_name)
        return widget

    def return_shot_dictionary(self):
        pass

    @staticmethod
    def return_button_checked_state(widget: QToolButton):
        """ Returns the checked state of a QToolButton. """

        return widget.isChecked()

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
