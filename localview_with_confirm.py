# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


bl_info = {
    "name": "Local View with Confirm",
    "author": "todashuta",
    "version": (0, 2, 2),
    "blender": (3, 6, 0),
    "location": "3D Viewport > View Menu > Local View > Enter Local View / Exit Local View",
    "description": "Confirm upon exit Local View",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "3D View"
}


import bpy


def get_addon_prefs(context):
    addon_prefs = context.preferences.addons[__name__].preferences
    return addon_prefs


class LocalviewWithConfirmOperator(bpy.types.Operator):
    bl_idname = "view3d.localview_with_confirm"
    bl_label = "Local View with Confirm"

    frame_selected: bpy.props.BoolProperty(
            name="Frame Selected",
            description="Move the view to frame the selected objects",
            default=True)

    @classmethod
    def poll(cls, context):
        return bpy.ops.view3d.localview.poll()

    def execute(self, context):
        return bpy.ops.view3d.localview(frame_selected=self.frame_selected)

    def invoke(self, context, event):
        if context.space_data.local_view is None:
            return self.execute(context) # enter Local View
        shading_type = context.space_data.shading.type
        scnene_props = context.scene.LocalViewWithConfirmAddonProps
        confirm = False
        match shading_type:
            case "WIREFRAME" if scnene_props.confirm_wireframe:
                confirm = True
            case "SOLID"     if scnene_props.confirm_solid:
                confirm = True
            case "MATERIAL"  if scnene_props.confirm_material:
                confirm = True
            case "RENDERED"  if scnene_props.confirm_rendered:
                confirm = True
        if confirm:
            wm = context.window_manager
            if bpy.app.version >= (4, 2, 0):
                return wm.invoke_confirm(self, event, icon="QUESTION", title="",
                                         message="Do you want to exit Local View?")
            else:
                return wm.invoke_confirm(self, event)
        return self.execute(context) # exit Local View without confirm


def set_confirm_wireframe(self, value):
    oldval = self.confirm_wireframe
    self["confirm_wireframe"] = value
    #print(self, oldval, value)
    if (oldval, value) == (False, True):
        self.confirm_solid = True
    if (oldval, value) == (True, False):
        pass # do nothing
def set_confirm_solid(self, value):
    oldval = self.confirm_solid
    self["confirm_solid"] = value
    #print(self, oldval, value)
    if (oldval, value) == (False, True):
        self.confirm_material = True
    if (oldval, value) == (True, False):
        self.confirm_wireframe = False
def set_confirm_material(self, value):
    oldval = self.confirm_material
    self["confirm_material"] = value
    #print(self, oldval, value)
    if (oldval, value) == (False, True):
        self.confirm_rendered = True
    if (oldval, value) == (True, False):
        self.confirm_solid = False
def set_confirm_rendered(self, value):
    oldval = self.confirm_rendered
    self["confirm_rendered"] = value
    #print(self, oldval, value)
    if (oldval, value) == (False, True):
        pass # do nothing
    if (oldval, value) == (True, False):
        self.confirm_material = False

class LocalviewWithConfirmProps(bpy.types.PropertyGroup):
    confirm_wireframe: bpy.props.BoolProperty(name="Confirm upon exit Local View",
                                              set=set_confirm_wireframe,
                                              get=lambda self: self.get("confirm_wireframe", False))
    confirm_solid:     bpy.props.BoolProperty(name="Confirm upon exit Local View",
                                              set=set_confirm_solid,
                                              get=lambda self: self.get("confirm_solid",     False))
    confirm_material:  bpy.props.BoolProperty(name="Confirm upon exit Local View",
                                              set=set_confirm_material,
                                              get=lambda self: self.get("confirm_material",  True))
    confirm_rendered:  bpy.props.BoolProperty(name="Confirm upon exit Local View",
                                              set=set_confirm_rendered,
                                              get=lambda self: self.get("confirm_rendered",  True))


def auto_rebind(self, context):
    unregister_keymaps()
    register_keymaps()


class LocalviewWithConfirmPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    frame_selected: bpy.props.BoolProperty(
            name="Frame Selected",
            description="Move the view to frame the selected objects",
            default=True,
            update=auto_rebind)

    use_shortcut: bpy.props.BoolProperty(
            name="Use Default Shortcut",
            default=False,
            update=auto_rebind)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "use_shortcut")
        inner_row = row.row()
        inner_row.active = self.use_shortcut
        inner_row.prop(self, "frame_selected")


addon_keymaps = []
def register_keymaps():
    prefs = get_addon_prefs(bpy.context)
    if not prefs.use_shortcut:
        return

    kc = bpy.context.window_manager.keyconfigs.addon
    if not kc:
        return

    km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new(LocalviewWithConfirmOperator.bl_idname, "SLASH", "PRESS")
    kmi.properties.frame_selected = prefs.frame_selected
    addon_keymaps.append((km, kmi))

    km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new(LocalviewWithConfirmOperator.bl_idname, "NUMPAD_SLASH", "PRESS")
    kmi.properties.frame_selected = prefs.frame_selected
    addon_keymaps.append((km, kmi))

def unregister_keymaps():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


classes = (
        LocalviewWithConfirmPreferences,
        LocalviewWithConfirmOperator,
        LocalviewWithConfirmProps,
)


def shading_menu_func(self, context):
    layout = self.layout
    shading_type = context.space_data.shading.type
    scnene_props = context.scene.LocalViewWithConfirmAddonProps
    match shading_type:
        case "WIREFRAME":
            layout.prop(scnene_props, "confirm_wireframe")
        case "SOLID":
            layout.prop(scnene_props, "confirm_solid")
        case "MATERIAL":
            layout.prop(scnene_props, "confirm_material")
        case "RENDERED":
            layout.prop(scnene_props, "confirm_rendered")

    #layout.separator()
    #layout.prop(scnene_props, "confirm_wireframe")
    #layout.prop(scnene_props, "confirm_solid")
    #layout.prop(scnene_props, "confirm_material")
    #layout.prop(scnene_props, "confirm_rendered")


def view_local_menu_func(self, context):
    layout = self.layout
    layout.separator()
    op = layout.operator(LocalviewWithConfirmOperator.bl_idname,
                    text="Exit Local View" if context.space_data.local_view else "Enter Local View")
    prefs = get_addon_prefs(context)
    op.frame_selected = prefs.frame_selected


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.LocalViewWithConfirmAddonProps = bpy.props.PointerProperty(type=LocalviewWithConfirmProps)
    bpy.types.VIEW3D_PT_shading.append(shading_menu_func)
    bpy.types.VIEW3D_MT_view_local.append(view_local_menu_func)

    register_keymaps()


def unregister():
    unregister_keymaps()

    bpy.types.VIEW3D_MT_view_local.remove(view_local_menu_func)
    bpy.types.VIEW3D_PT_shading.remove(shading_menu_func)
    if hasattr(bpy.types.Scene, "LocalViewWithConfirmAddonProps"):
        del bpy.types.Scene.LocalViewWithConfirmAddonProps

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
