# type: ignore[reportPossiblyUnboundVariable]

import sys
import json
import json.decoder
import os
import re
from random import randrange

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget
from shiboken6 import wrapInstance

from source.util_paths import Path as path
from source.creators import LayerCreator

try:
    import maya.cmds as mc
    import maya.mel as mel
    import maya.app.renderSetup.model.renderSetup as render
    import maya.app.renderSetup.model.renderLayer as renderLayer
    import maya.app.renderSetup.model.override as override
    import maya.app.renderSetup.model.container as container
    import maya.app.renderSetup.model.collection as collection
    import pymel.core as pm
    from maya import OpenMayaUI as omui
except ModuleNotFoundError:
    pass


def node_exists(keywords, case_sensitive=True):
    """Checks if a node contains a list of keywords

    Args:
        keywords (list): list of keywords
        case_sensitive (object): whether the check should be case-sensitive

    Returns:
        bool: True if node exists, else False
    """
    existing_keywords = []
    for node in mc.ls(r=True):
        existing_keywords = []
        for kw in keywords:
            if case_sensitive:
                if kw in node:
                    existing_keywords.append(kw)
            else:
                if kw.lower() in node.lower():
                    existing_keywords.append(kw)
    return len(existing_keywords) == len(keywords)

def camera_exists(shot):
    """Check if a camera exists with the given shot name"""

    for node in mc.ls(tr=True, r=True):
        children = mc.listRelatives(node, ad=True, typ='camera')
        if children:
            for cam in children:
                if shot in cam:
                    return True
    return False

def light_exists(shot):
    """Check if a light exists with the given shot name"""

    for node in mc.ls(tr=True, r=True):
        if 'light' in node:
            if shot in node:
                return True
    return False

def set_exists(shot):
    """Check if a set exists with the given shot name"""

    for node in mc.ls(set=True, r=True):
        if shot in node:
            return True
    return False

def sequence_exists(shot):
    """Check if a sequence exists with the given shot name"""

    for node in mc.ls(type='shot', r=True):
        if shot in node:
            return True
    return False

def maya_is_loaded():
    """Returns True if Maya is loaded, else False."""

    if "maya" in sys.modules:
        return True

    return False

def get_maya_window():
    """Returns Maya's main window as Python object"""

    ptr = omui.MQtUtil.mainWindow()  # pyright: ignore
    maya_window = wrapInstance(int(ptr), QWidget)

    return maya_window

def renderer_is_redshift():
    """Prints a warning if the current scene renderer is not Redshift"""

    if mc.getAttr("defaultRenderGlobals.currentRenderer") != 'redshift':

        mc.warning("Redshift is not current renderer")
        return False

    else:
        return True

def set_redshift_renderer():
    """Loads the Redshift plugin and sets Redshift as the current scene renderer"""

    if renderer_is_redshift():
        pass

    else:

        # List the plugins that are currently loaded
        plugins = mc.pluginInfo(query=True, listPlugins=True)

        # Load Redshift
        if 'redshift4maya' in plugins:
            print('Redshift is already loaded.')

        else:

            try:
                mc.loadPlugin('redshift4maya')
                print('Redshift is now loaded.')

            except Exception as e:
                print(e)
                return

        # Set renderer
        mc.setAttr('defaultRenderGlobals.currentRenderer', 'redshift', type='string')
        mc.warning('Renderer set to Redshift')

def set_correct_fps():
    """Sets Maya to use 25 FPS in the scene"""

    cu = mc.currentUnit(query=True, time=True)

    if cu == "pal":

        pass

    else:

        mc.currentUnit(time="pal")

def find_latest(search_dir, stream):
    """Checks for the latest publish version in the directory and returns a path to that folder

    Args:
        search_dir (string): A path to published folder on the libraries drive, ex. "resources/presets/published"
        stream (string): Name of the stream for the folder, ex "main"
    Returns:
        Path to the latest version folder, if exists, otherwise None.

    """
    library_path = f"{os.getenv('ACTIVE_LIBRARY_PATH', 'L:')}"

    if library_path:

        dir_full_path = os.path.join(library_path, search_dir)
        dir_folder = os.walk(dir_full_path, topdown=True)
        path_to_versions = None
        versions = []

        for directory, folders, files in dir_folder:
            for folder in folders:
                if re.search(stream, folder) and re.search(r'.*?v\d\d\d$', folder):
                    versions.append(folder)
                    path_to_versions = directory

        if versions:

            latest = versions[-1]
            end_path = os.path.join(path_to_versions, latest)
            end_path.replace("\\", "/")

            return end_path

        else:

            mc.warning("Template directory cannot be found.")
            pass

    else:

        path_to_project = path.sm_folder
        return path_to_project

def load_style_sheet():
    """Loads the file with style sheets for the application."""

    ui_directory = path.resource_file("style_sheet.css")

    with open(ui_directory, encoding="UTF-8", mode="r") as file:
        styles = file.read()
    return styles

def load_frame_style():
    """Loads the file with style sheets for the QFrame."""

    ui_directory = path.resource_file("frame_styles.json")

    with open(ui_directory, encoding="UTF-8", mode="r") as file:
        styles = json.load(file)
    return styles

def get_random_color():
    """ Returns a random color from the list. """

    # Set shot color
    color_list = ("red", "green", "blue", "yellow", "purple", "orange")
    random_index = randrange(0, len(color_list))
    color = color_list[random_index]
    return color

def return_resource_dict(key: str):
    """Returns the correct dictionary for items used throughout the Shot Manager scripts.

        Args:
            key (str): name of the key for the dictionary
    """

    dict_directory = path.resource_file("dictionaries.json")

    with open(dict_directory, encoding="UTF-8", mode="r") as file:
        resource_dict = json.load(file)

    return resource_dict[key]

def get_shots():
    """This function looks for shot sets in the scene.

    Returns:
        shots (list): List of strings.
    """

    sets = mc.ls(sets=True)
    shots = []

    # Check set name against a regex to see if it's a shot
    for s in sets:
        if re.search(r'^s\d\d\d$', s):
            # shot_number = (s.split("s"))[-1]
            shots.append(s)

    return shots

def process_group_structure(structure, parent=None):
    groups = []
    group = None
    nodes = mc.ls()
    name = structure.get('name')
    color = structure.get('color')

    # Check if group exists already
    for node in nodes:
        if node == name:
            group = node

    # Create new if it doesn't
    if not group:
        if parent:
            group = mc.group(p=parent, n=name, em=True)
        else:
            group = mc.group(n=name, em=True)

        # Set color in outliner
        if color:
            mc.setAttr(f'{group}.useOutlinerColor', True)
            mc.setAttr(f'{group}.outlinerColor', *color)

    # Add to list of groups
    groups.append(group)

    # Create children groups
    for child in structure.get("children", []):
        groups.extend(process_group_structure(child, parent=group))

    return groups

def create_default_groups():
    """Checks the scene for default groups and creates them if they don't exist"""
    group_nodes = []
    groups = [
        {
            'name': 'cameras',
            'color': (0.545, 0.737, 1)
        },
        {
            'name': 'scene_lights',
            'color': (1, 0.759, 0),
            'children': [{
                'name': 'generic',
                'color': (1, 0.759, 0)
            }]
        },
        {
            'name': 'geo',
            'color': (0, 0.451, 1)
        },
        {
            'name': 'fx',
            'color': (1, 0.286, 0.913)
        },
        {
            'name': 'temp',
            'color': (1, 1, 1)
        },
    ]

    # Create or get groups
    for g in groups:
        group_nodes.extend(process_group_structure(g))

    return group_nodes

def create_global_sets():
    """Checks the scene for global shot sets and creates them if they don't exist"""

    if set_exists("global_shot"):

        global_set = "global_shot"

    else:
        global_set = mc.sets(n="global_shot", em=True)

    if set_exists("global_foreground"):

        global_fg = "global_foreground"

    else:
        global_fg = mc.sets(n="global_foreground", em=True)

    if set_exists("global_background"):

        global_bg = "global_background"

    else:
        global_bg = mc.sets(n="global_background", em=True)

    mc.sets(global_fg, fe=global_set, edit=True)
    mc.sets(global_bg, fe=global_set, edit=True)

def create_global_rs_sets():
    """Checks the scene for global shot sets and creates them if they don't exist"""

    vis_sets = mc.ls(type="RedshiftVisibility")

    if "rsVisibility_global_fg" in vis_sets:

        "rsVisibility_global_fg"

    else:

        mc.shadingNode("RedshiftVisibility", n="rsVisibility_global_fg", au=True)

    if "rsVisibility_global_bg" in vis_sets:

        "rsVisibility_global_bg"

    else:

        mc.shadingNode("RedshiftVisibility", n="rsVisibility_global_bg", au=True)

# ----> MAYA FUNCTIONS <----

# LAYER SWITCH

def switch_layer(layer):
    """Sets the active layer, camera and frame range to the given layer.

    Args:
        layer (string): Layer name, layerName.
    """

    set_active_layer(layer)
    set_active_camera()
    set_frame_range()

def set_frame_range():
    """ Returns the frame range of the given layer.
    """

    playback = mc.play(q=True, state=True)  # Get the playback range

    range_start = int(mc.getAttr("defaultRenderGlobals.startFrame"))
    range_end = int(mc.getAttr("defaultRenderGlobals.endFrame"))

    mc.playbackOptions(max=range_end)
    mc.playbackOptions(min=range_start)

    if not playback:
        mc.currentTime(range_start, edit=True)

def set_active_camera():
    """ Sets the active camera to the one assigned to the current render layer."""

    cameras = mc.ls(type="camera", r=True)

    for cam in cameras:

        renderable = mc.getAttr(cam + ".renderable")

        if renderable:
            mc.lookThru(cam)

def set_active_layer(layer):
    """ Sets the active layer.

    Args:
        layer (string): Name of the render setup layer.
    """

    layer_name = get_render_layer_name(layer)

    try:
        mc.editRenderLayerGlobals(currentRenderLayer=layer_name)

    except TypeError:  # Layer doesn't exist
        mc.warning("There is not render layer attached to this shot.")
        pass

    except NameError:
        print(" Maya module isn't loaded.")
        pass

def get_render_layer_name(layer):
    """Returns render layer name, rs_layerName."""

    name = "rs_" + layer

    return name

def get_render_setup_layer_name(layer):
    """Returns render setup layer name, layerName."""

    if "rs_" in layer:
        layer = layer[3:]

    return layer

# SHOT CREATION

def create_sets(shot):
    """Creates Maya sets with the correct naming.

        Args:
        shot (string): Name of the shot, i.e. s010
    """
    master_set = shot
    fg_set = shot + "_foreground"
    bg_set = shot + "_background"
    fx_set = shot + "_fx"
    exclude_set = shot + "_exclude"

    set_list = [master_set, fg_set, bg_set, fx_set, exclude_set]

    for maya_set in set_list:

        if set_exists(maya_set):

            mc.warning("Set for this shot already exists.")
            pass

        else:

            mc.sets(n=maya_set, em=True)

            if maya_set is not master_set:
                mc.sets(maya_set, fe=master_set)

def create_camera(shot):
    """Import the latest published camera rig, adds the correct shot name prefix to all the nodes in the camera
    group and assigns the outliner color to the top node.

        Args:
        shot (string): Name of the shot, i.e. s010
    """
    # Check if the camera with this name is in the scene

    if camera_exists(shot):

        mc.warning("Camera for this shot already exists.")
        pass

    else:

        camera_dir = "E:/Projects/maya/templates"

        # Create camera's top group

        camera_group = "_".join([f"{shot}", "camera"])

        # Import camera setup

        camera_path = os.path.join(camera_dir, "s000_camera.mb")
        mc.file(camera_path, rnn=True, i=True, f=True)

        # Rename the camera nodes

        all_transforms = mc.ls(tr=True, r=True)
        temp_list = []

        for nodes in all_transforms:

            if "s000" in nodes:
                temp_list.append(nodes)

        mc.select(temp_list)

        for item in pm.selected():
            item.rename(item.name().replace('s000', f"{shot}"))

        # Parent the camera's top group under cameras group
        scene_items = mc.ls(transforms=True, r=True)

        try:

            mc.parent(camera_group, "cameras")

        except ValueError:  # Group has a namespace

            for item in scene_items:

                if re.search(r'cameras\s?', item):
                    mc.parent(camera_group, item)

        # Assign color to the camera node in the outliner

        set_outliner_color(shot, camera_group)

        # Rename the rsBokeh node, since it doesn't get renamed on import

        bokeh_items = mc.ls(type="RedshiftBokeh", r=True)

        for i in bokeh_items:

            if "cam_rsBokeh" in i or "s000_camera_cam_rsBokeh" in i:
                sel = mc.select(i)
                mc.rename(sel, shot + "_rsBokeh")

def create_light_group(shot):
    """ Creates a light group with the shot name prefix under the main lights group.

    Args:
        shot (string): NAme of the shot, ie s010.
    """

    group_exists = light_exists(shot)

    if group_exists:

        mc.warning("Light group for this shot already exists.")
        pass

    else:

        light_group = mc.group(em=True, n=(shot + "_light"))

        set_outliner_color(shot, light_group)

        try:

            mc.parent(light_group, "scene_lights")

        except ValueError:  # Light group is missing

            mc.warning("Scene_lights group is missing in the scene.")
            pass

def create_sequence(shot_name):
    """ Creates a new shot in the Camera Sequencer and assigns the correct name, camera and frame range.

        Args:
            shot_name (string): NAme of the shot, ie s010.
    """

    if sequence_exists(shot_name):

        mc.warning("Sequence for this shot already exists.")
        pass

    else:

        data = create_data_file()

        start = int(data[shot_name]["start"])
        end = int(data[shot_name]["end"])

        mc.shot(shot_name + "_seq", sn=shot_name, st=start, et=end, sst=start, set=end)

        mc.playbackOptions(min=start, max=end, ast=start, aet=end)

        mc.connectAttr(shot_name + "_seq.startFrame", shot_name + "_seq.sequenceStartFrame", f=True)

def delete_shot_elements(shot):
    """ Deletes all sets, sequences and groups connected to the given shot.

    Args:
        shot(string) = Name of the shot.

    """

    set_list = mc.ls(sets=True)
    sequence_list = mc.ls(type="shot")
    obj_list = mc.ls(transforms=True)
    bokeh_list = mc.ls(type="RedshiftBokeh")

    for s in set_list:

        if shot in s:

            try:

                mc.delete(s)

            except ValueError:  # Top group is deleted together with children

                pass

    for seq in sequence_list:

        if shot in seq:
            mc.delete(seq)

    for obj in obj_list:

        if shot in obj:

            try:

                mc.delete(obj)

            except ValueError:  # Top group is deleted together with children

                pass

    for b in bokeh_list:

        if shot in b:
            mc.delete(b)

def get_maya_color(color):
    """This function contains color dictionaries for outliner elements, based on the colors available in render
    setup.

    Args:
        color (string): Name of the color, which is assigned to the shot

    Returns:
        color (tuple): A tuple of 3 float values representing the R, G and B color values, for use in outliner.
    """

    outliner_colors_dict = return_resource_dict("OUTLINER_COLORS")

    outliner_color = outliner_colors_dict[color]

    return outliner_color

def change_layer_color(layer, color):
    """ Changes the color of the layer in the Render Setup Editor.

        Args:
            layer (str): Name of the layer
            color (str): Color to be assigned to the layer, MUST start with a capital letter ex. Red
    """

    if isinstance(layer, list):
        for each in layer:
            mc.setAttr(each + ".labelColor", color.capitalize(), type="string")

    else:
        mc.setAttr(layer + ".labelColor", color.capitalize(), type="string")

def set_outliner_color(shot, group):
    """Enables outliner color override for the given group and assigns a color from the template.

    Args:
        shot (string): Name of the shot, ie s010.
        group (string): Name of the group, as it is in the outliner.
    """

    data = create_data_file()

    shot_color = data[shot]["color"]
    color = get_maya_color(shot_color)

    mc.setAttr(group + ".useOutlinerColor", True)
    mc.setAttr(group + ".outlinerColor", color[0], color[1], color[2])

def edit_overrides(layer, attribute, value, plug):
    """Checks the render layer for existing overrides on the given attribute and creates them if they don't exist.
    Finally, sets the value of the override to given value.

    Args:
        layer (str or list) : Name of render layer or a list of render layer names
        attribute (string): Name of the overriden attribute.
        value (string or integer): Value of the override.
        plug (string): Name of the node which has the given attribute, ex. "defaultRenderGlobals"
    """

    # Sets
    has_overrides = []
    no_overrides = []

    # CHECK IF OVERRIDES EXIST

    render_layer = render.instance().getRenderLayer(layer)
    settings_collection = render_layer.renderSettingsCollectionInstance()
    collection_overrides = settings_collection.getOverrides()
    ov_value = 0

    if value is not None:

        if isinstance(value, str):
            try:
                ov_value = int(value) * 240.0

            except ValueError or TypeError:

                ov_value = value

        if isinstance(value, int):

            if attribute == "aovGlobalEnableMode":

                ov_value = value

            else:

                ov_value = value * 240.0

        for override in collection_overrides:

            if attribute in override.name():

                override.setAttrValue(ov_value)

                if render_layer not in has_overrides:
                    has_overrides.append(render_layer)
            else:

                if render_layer not in no_overrides:
                    no_overrides.append(render_layer)

    # FILTER THE LIST FOR ONLY LAYERS WITHOUT OVERRIDES
    need_overrides = [x for x in no_overrides if x not in has_overrides]

    for r_layer in need_overrides:
        ov = r_layer.createAbsoluteOverride(plug, attribute)
        ov.setAttrValue(ov_value)

def rename_shot_elements(old_shot, new_shot):
    """ Checks if the elements of the old shot exist in the scene and renames them to a new shot name."""

    # Rename sets

    sets = []

    for set_node in mc.ls(set=True, r=True):
        if old_shot in set_node:
            sets.append(set_node)

    for se in sets:
        mc.rename(se, new_shot + se[4:])

    # Rename all transforms

    transforms = []
    patterns = []

    for node in mc.ls():
        if old_shot in node:
            transforms.append(node)
        if "Selector" in node and old_shot in node:
            patterns.append(node)

    for p in patterns:
        old_pattern = mc.getAttr(p + ".pattern")
        new_pattern = old_pattern.replace(old_shot, new_shot)
        mc.setAttr(p + ".pattern", new_pattern, type="string")

    for t in transforms:

        new_name = t.replace(old_shot, new_shot)

        try:
            mc.rename(t, new_name)

        except RuntimeError:
            pass

def rename_layers(old_name, new_name):
    """ Checks if the elements of the old shot exist in the scene and renames them to a new shot name."""

    for node in mc.ls():
        if old_name in node:
            updated_name = node.replace(old_name, new_name)
            try:
                mc.rename(node, updated_name)
            except RuntimeError:
                pass

# RENDER LAYERS

def delete_render_layer(layer):
    """ Deletes the render layer and all connected render nodes.

        Args:
            layer (string) : Name of the layer.
    """

    col_set = ["collection", "renderSettingsCollection", "renderSettingsChildCollection", "aovCollection",
               "aovChildCollection"]

    ov_set = ["override", "absOverride", "absUniqueOverride", "relOverride", "relUniqueOverride",
              "valueOverride"]

    render.instance().switchToLayerUsingLegacyName("defaultRenderLayer")

    rl = render.instance().getRenderLayer(layer)
    special_collections = rl.getChildren()  # RenderSettingsCollection, AOVCollection, LightsCollection
    groups = rl.getGroups()

    # REMOVE SPECIAL RENDER LAYER COLLECTION AND ITS CHILDREN
    for special_col in special_collections:

        # Find all overrides (type = AbsUniqueOverride) in RenderSettingsCollections
        # and all AOVChildCollections in AOVCollection
        child_collections_1 = special_col.getChildren()

        for child_col_1 in child_collections_1:

            if child_col_1:

                child_type = mc.nodeType(child_col_1.name())

                # COLLECTIONS - GET SUB-COLLECTIONS

                for col_type in col_set:

                    if child_type == col_type:

                        """Object is a collection"""

                        child_collections_2 = child_col_1.getChildren()

                        if child_collections_2 and len(child_collections_2) > 0:

                            for child_col_2 in child_collections_2:
                                """Returns override from the sub collection of special collection"""

                                override.delete(child_col_2)

                        container.delete(child_col_1)

        # COLLECTIONS - REMOVE

        container.delete(special_col)

    # REMOVE ALL GROUPS AND ITS CHILDREN

    for grp in groups:

        cols = grp.getChildren()

        for col in cols:

            grp_child_cols = col.getChildren()  # Get collections under the group

            for childCol in grp_child_cols:

                grp_child_type = mc.nodeType(childCol.name())

                for grp_col_type in col_set:

                    if grp_child_type == grp_col_type:
                        container.delete(childCol)

            container.delete(col)

        container.delete(grp)

    # REMOVE RANDOM UNSORTED COLLECTIONS

    unsorted_cols = rl.getCollections()

    if unsorted_cols and len(unsorted_cols) != 0:
        for c in unsorted_cols:
            unsorted_child_type = mc.nodeType(c.name())

            for ci2 in col_set:
                if unsorted_child_type == ci2:
                    for ci3 in col_set:
                        c3Type = mc.nodeType(c.name())
                        if c3Type == ci3:
                            override.delete(c)
                    if c.hasSelector:
                        c._deleteSelector()
                    container.delete(c)
            for oi2 in ov_set:
                if unsorted_child_type == oi2:
                    override.delete(c)
            if c.hasSelector:
                c._deleteSelector()
            container.delete(c)
    renderLayer.delete(rl)

def get_layer_info_from_scene(layer_name: str):
    """Retrieves start frame, end frame, renderable status and AOV enabled status from the given layer.

        Args:
            layer_name: layer name

        Returns:
            layer_info (tuple): layer name, start frame, end frame, renderable status and AOV enabled status

    """

    setup_layer = get_render_layer_name(layer_name)
    layer = get_render_setup_layer_name(layer_name)

    layer_instance = render.instance().getRenderLayer(layer)
    settings_collection = layer_instance.renderSettingsCollectionInstance()
    collection_overrides = settings_collection.getOverrides()

    # Temp variables

    start_frame = 1001
    end_frame = 1001
    aov_status = True

    for override in collection_overrides:

        name = override.name()

        if "startFrame" in name:
            start_frame: int = mc.getAttr(name + ".attrValue")

        if "endFrame" in name:
            end_frame: int = mc.getAttr(name + ".attrValue")

        if "aovGlobalEnable" in name:
            aov_status: bool = mc.getAttr(name + ".attrValue")

    renderable_status: bool = mc.getAttr(setup_layer + ".renderable")

    layer_info = layer, start_frame, end_frame, renderable_status, aov_status

    return layer_info

def get_layer_info_from_view(data: dict, shot_name: str, layer_name: str):
    layer_dict = LayerCreator(None).layer_dict_exists(data, shot_name)
    layer_info_dict = layer_dict[layer_name]

    start = layer_info_dict["start"]
    end = layer_info_dict["end"]
    renderable = layer_info_dict["renderable"]
    aov = layer_info_dict["AOV mode"]

    layer = get_render_setup_layer_name(layer_name)

    layer_instance = render.instance().getRenderLayer(layer)
    settings_collection = layer_instance.renderSettingsCollectionInstance()
    collection_overrides = settings_collection.getOverrides()

    for override in collection_overrides:

        name = override.name()

        if "start" in name:
            mc.setAttr(name + ".attrValue", start)

        elif "end" in name:
            mc.setAttr(name + ".attrValue", end)

def set_layer_renderable(layer_name, value):
    setup_layer = get_render_layer_name(layer_name)

    mc.setAttr(setup_layer + ".renderable", value)

def get_renderable_status_from_scene(layer_name):
    layers = mc.ls(type="renderLayer")

    for layer in layers:

        layer_setup_name = get_render_setup_layer_name(layer)

        if layer_name == layer_setup_name:
            status = mc.getAttr(layer + ".renderable")

            return status

def create_aov_and_override_enabled(layer: str, aov_group: str, override_value: int):
    """ Creates beauty and utility AOVs in Maya. Creates an AOV collection for the layers and creates overrides
        for each AOV.

        Args:
            layer (str): name of the render layer
            aov_group (str): beauty or utility, type of AOVs to be added to the shot
            override_value (int): Enabled/disabled.
    """

    node_list = mc.ls(type="RedshiftAOV")
    aov_list = []
    crypto_list = []

    # Check for existing Cryptomatte nodes in the scene
    for node in node_list:
        if "Crypto" in node:
            crypto_list.append(node)

    # Lists of AOVs to loop over depending on which button has been clicked

    if aov_group == "beauty":
        aov_list = (
            "Diffuse Lighting", "Reflections", "Specular Lighting", "Refractions", "Global Illumination", "Shadows")

    elif aov_group == "utility":
        aov_list = ("Cryptomatte", "Cryptomatte", "Depth")

    # Loop over AOVs in the list, create them if they don't exist. Check if they have an
    # override in the given layer, if not, create it.

    for aov in aov_list:

        # Don't create more than 2 Cryptomatte nodes
        if aov_group == "utility" and aov == "Cryptomatte" and len(crypto_list) > 1:
            create_aov_collection(layer, "CryptoNode", override_value)
            create_aov_collection(layer, "CryptoMat", override_value)

        else:

            aov_name = aov.replace(" ", "")

            # For type search inside Maya, plus the node name and AOV name are two different things.
            node_name = "rsAov_" + aov_name

            if node_name in node_list:

                if aov_collection_exists(layer, aov_name):
                    ov_node = aov_override_exists(layer, aov_name)
                    if ov_node:
                        ov_name = ov_node[0].name()
                        mc.setAttr(ov_name + ".attrValue", override_value)  # Z normalized
                        # print(f"{aov} node already exists.")

            else:
                try:
                    func = f'rsCreateAov -type "{aov}";'
                    mel.eval(func)

                except RuntimeError as e:  # For renamed Cryptomattes (I think)
                    print(f"Error {e} came up. Sorry!")

                else:
                    # Add AOVs to render setup
                    # mel.eval("redshiftAddAov")
                    mel.eval("redshiftUpdateActiveAovList();")
                    print(f"{aov} has been created.")

                if aov_group == "utility" and aov == "Depth":
                    # Set correct Depth AOV mode
                    mc.setAttr("rsAov_Depth.depthMode", 1)  # Z normalized

            # Create collection with overrides for the layer and the given aov

            if aov != "Cryptomatte":

                create_aov_collection(layer, aov_name, override_value)

            else:

                # Rename the Cryptomatte nodes and set correct values for material crypto
                # Create collections for the Cryptomattes, which are a bit of a trouble child. We need two
                # collections for the cryptos, so the standard single collection doesn't work and as
                # an added bonus they get renamed, so the AOV type is still "Cryptomatte", anything else responds
                # to the new name. Fun times.

                rename_crypto_nodes()
                create_crypto_collections(layer, override_value)

def aov_collection_exists(layer: str, aov: str):
    """ Returns True if the layer has an AOV collection and overrides for the specific AOV.

        Args:
            layer (str): name of the render layer
            aov (str): name of the AOV
    """

    render_layer = render.instance().getRenderLayer(layer)
    aov_col_exists = render_layer.hasAOVCollectionInstance()

    if aov_col_exists:
        # Check if the AOVs Collection exists. The collection should be automatically created
        # when an AOV override is created.

        aov_col = render_layer.aovCollectionInstance()
        aov_child_col = aov_col.getCollections()

        # Loop over all child collections and check for overrides
        for collection in aov_child_col:
            aov_name = collection.name()

            if aov in aov_name:
                return collection
    return None

def aov_override_exists(layer: str, aov: str):
    """ Returns True if the layer has an override for the specific AOV, else False.

        Args:
            layer (str): name of the render layer
            aov (str): name of the AOV
    """

    # Check if the collection exists for the layer and aov
    col = aov_collection_exists(layer, aov)

    if col:
        # Get collection overrides
        overrides: list = col.getOverrides()
        if overrides:
            return overrides
    return {}

def create_aov_collection(layer: str, aov: str, override_value: int):
    """ Create an AOVCollection and AOVChildCollection for the given AOV and override
        the .enabled attribute on the AOV.

        Args:
            layer (str): name of the render layer
            aov (str): name of the aov to be created
            override_value (int): 0 or 1, toggle AOV .enabled
    """

    render_layer = render.instance().getRenderLayer(layer)
    aov_col = render_layer.aovCollectionInstance()
    aov_collection = aov_collection_exists(layer, aov)

    if not aov_collection:

        # Create an AOVChildCollection
        child_collection = collection.create(aov, nodeType="aovChildCollection", parent="AOVCollection",
                                             **{"aovName": f"{aov}"})

        # Append the child collection to the AOVs collection
        aov_col.appendChild(child_collection)

        # Add overrides
        aov_name = "rsAov_" + aov

        # Create an override on .enabled attribute of the AOV
        render_layer.createAbsoluteOverride(f"{aov_name}", "enabled")

    else:

        # If the override is missing, create it
        if not aov_override_exists(layer, aov):
            aov_name = "rsAov_" + aov

            # Create an override on .enabled attribute of the AOV
            render_layer.createAbsoluteOverride(f"{aov_name}", "enabled")

        else:

            if "Crypto" not in aov:

                # Set the value of the override
                aov_node = "rsAov_" + aov + ".enabled"
                mc.setAttr(aov_node, override_value)

            else:
                # Set the value of the override
                crypto_node_ovs = aov_override_exists(layer, "CryptoNode")
                for node_ov in crypto_node_ovs:
                    node_ov.setAttrValue(override_value)

                crypto_mat_ovs = aov_override_exists(layer, "CryptoMat")
                for mat_ov in crypto_mat_ovs:
                    mat_ov.setAttrValue(override_value)

def create_crypto_collections(layer: str, override_value: int):
    """ After the cryptomatte AOVs have been created, checks for their name and creates a collection with override
        if it doesn't exist.

        Args:
            layer (str): name of the render layer
            override_value (int): 0 or 1 for .enabled status
    """
    node_list = mc.ls(type="RedshiftAOV")
    crypto_list = []

    # Check for existing Cryptomatte nodes in the scene
    for node in node_list:
        if "Crypto" in node:
            crypto_list.append(node)

    for aov in crypto_list:
        aov_name = aov.split("_")[1]
        create_aov_collection(layer, aov_name, override_value)

def rename_crypto_nodes():
    """ Rename Cryptomatte nodes from their default names. Set correct settings for the
        material AOV.
    """

    node_list = mc.ls(type="RedshiftAOV")
    crypto_list = []

    # Check for existing Cryptomatte nodes in the scene
    for node in node_list:
        if "Crypto" in node:
            crypto_list.append(node)

    for aov in crypto_list:

        index = crypto_list.index(aov)
        aov_name = aov + ".name"

        if index == 0:
            # Rename the first Cryptomatte AOV to Node
            mc.setAttr(aov_name, "CryptoNode", type="string")
            mc.rename(aov, "rsAov_CryptoNode")

        elif index == 1:

            # Rename the second Cryptomatte AOV to Mat and set correct mode
            mc.setAttr(aov_name, "CryptoMat", type="string")
            mc.rename(aov, "rsAov_CryptoMat")
            mc.setAttr("rsAov_CryptoMat.idType", 1)

def toggle_aov_enabled_override(layer: str, aov_group: str, override_value: int):
    """ Creates beauty and utility AOVs in Maya. Creates an AOV collection for the layers and creates overrides
        for each AOV.

        Args:
            layer (str): name of the render layer
            aov_group (str): beauty or utility, type of AOVs to be added to the shot
            override_value (str): String "enabled" or "disabled"
    """

    aov_list = []

    # Lists of AOVs to loop over depending on which button has been clicked
    # TODO: add a global variable for lists

    if aov_group == "beauty":
        aov_list = (
            "Diffuse Lighting", "Reflections", "Specular Lighting", "Refractions", "Global Illumination", "Shadows")

    elif aov_group == "utility":
        aov_list = ("Cryptomatte", "Cryptomatte", "Depth")

    # Loop over AOVs in the list, create them if they don't exist. Check if they have an
    # override in the given layer, if not, create it.

    for aov in aov_list:
        aov_name = aov.replace(" ", "")
        if aov != "Cryptomatte":

            # Add overrides for the layer
            create_aov_collection(layer, aov_name, override_value)
        else:
            create_crypto_collections(layer, override_value)

def return_icon_tooltip(button_name:str, status:str):
    """ Returns the correct icon and tooltip for the button
        with the given status.
        Args:
            button_name (str): Name of the button.
            status (str): Status can be "on", "mid", "off".
        Returns:
            tuple: Contains a QIcon and a tooltip string. """

    icon_dict = return_resource_dict("BUTTON_ICONS")
    tooltip_dict = return_resource_dict("TOOLTIPS")
    icon_path = icon_dict[button_name][status]
    tooltip = tooltip_dict[button_name][status]
    icon = QIcon(path.icon(icon_path))

    return icon, tooltip
