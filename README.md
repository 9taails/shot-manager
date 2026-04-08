# Shot Manager

A render layer management tool for Maya/Redshift workflow. It allows for creating, editing and removing multiple render layers at once. 
A preview video of how it works can be watched here: 
https://vimeo.com/1122576817?fl=pl&fe=sh

## Functionality

### Shot
Creates Maya sets and a default shot master render layer which serves as a filter for scene items. Switching between shots in Shot Manager will automatically change the view to the camera assigned to the shot and adjust the timeline to shot's frame range. Render layers added to the shot will inherit changes made to the shot without the need to manually adjust every render layer.

Current settings which can be changed:
- Frame range
- Name
- AOV mode
- AOVs (Beauty, Cryptomatte, Utility)
- Renderable status
- Color of the render layers and respective outliner groups' color for the shot
- Deleting all render layers and camera groups belonging to the shot

### Render layer
- Possible to create multiple render layers in one go, based on render layer templates
- Render layers inherit shot's settings, but can be also edited on individual basis
- Naming convention for all collections and overrides within a render layer

Render layer presets
- master (for quick test renders, filtering items in the scene; a "working" layer)
- foreground
- background
- global foreground
- global background
- custom (correct collection naming and inherited settings, but needs to be populated manually; can have any custom name which will be added to the shot name, ex. s050customLayer)

### Scene setup
1. Creates default global groups: cameras, geo, lights
2. Creates default shot-based groups inside the global groups; sXXX_camera, sXXX_light
3. Creates global and shot-based sets
  - Sets can have non-exclusive membership, unlike groups, ie. the same node can be a member of multiple sets
  - Items in the global sets will, by default, go into all render layers. It's useful for scenes where the same objects go into all shots and the only things changing are frame ranges and camera.
4. Creates default Redshift Visibility sets for background and foreground. Render layer presets already have the correct overrides set up, so for example the foreground layer will have Redshifts Primary Visibility ON for items in the foreground set and OFF for items in the background set.
5. Imports a template camera rig with a Redshift Bokeh node connected.

### Limitations
- One-way sync:
  Shot Manager to Maya only. Any changes made inside Maya to the settings managed by Shot Manager will not update, ie. changing start frame inside a render layer     will not update in Shot Manager. It does not sync pre-existing layers.
- Default start frame for all new shots:
  All shots start on frame 1001 when created.
- Works for animation at 25fps.
- No customisation is currently implemented; for the script to work, a specific naming convention needs to be followed.
