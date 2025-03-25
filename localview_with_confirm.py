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
    "version": (0, 1, 0),
    "blender": (3, 6, 0),
    "location": "-",
    "description": "-",
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

    @classmethod
    def poll(cls, context):
        return bpy.ops.view3d.localview.poll()

    def execute(self, context):
        prefs = get_addon_prefs(context)
        return bpy.ops.view3d.localview(frame_selected=prefs.frame_selected)

    def invoke(self, context, event):
        if context.space_data.local_view is None:
            return self.execute(context)
        shading_type = context.space_data.shading.type
        modes = {
                "SOLID":    {"SOLID", "MATERIAL", "RENDERED"},
                "MATERIAL": {         "MATERIAL", "RENDERED"},
                "RENDERED": {                     "RENDERED"},
        }[context.scene.LocalViewWithConfirmAddon_modes]
        if shading_type in modes:
            wm = context.window_manager
            return wm.invoke_confirm(self, event)
        return self.execute(context)


def auto_rebind(self, context):
    unregister_keymaps()
    register_keymaps()


class LocalviewWithConfirmPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    frame_selected: bpy.props.BoolProperty(
            name="Frame Selected",
            description="Move the view to frame the selected objects",
            default=True)

    use_shortcut: bpy.props.BoolProperty(
            name="Use Default Shortcut",
            default=False,
            update=auto_rebind)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "frame_selected")
        row.prop(self, "use_shortcut")


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
    addon_keymaps.append((km, kmi))

    km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new(LocalviewWithConfirmOperator.bl_idname, "NUMPAD_SLASH", "PRESS")
    addon_keymaps.append((km, kmi))

def unregister_keymaps():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


classes = (
        LocalviewWithConfirmPreferences,
        LocalviewWithConfirmOperator,
)


def menu_func(self, context):
    layout = self.layout
    layout.prop(context.scene, "LocalViewWithConfirmAddon_modes")


def register():
    bpy.types.Scene.LocalViewWithConfirmAddon_modes = bpy.props.EnumProperty(
            name="LVWC Modes",
            description="Local View with Confirm Modes",
            default="MATERIAL",
            items=[("SOLID",    "Solid / Material Preview / Rendered", ""),
                   ("MATERIAL", "Material Preview / Rendered",         ""),
                   ("RENDERED", "Rendered",                            "")])

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_PT_shading.append(menu_func)

    register_keymaps()


def unregister():
    unregister_keymaps()

    bpy.types.VIEW3D_PT_shading.remove(menu_func)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    if hasattr(bpy.types.Scene, "LocalViewWithConfirmAddon_modes"):
        del bpy.types.Scene.LocalViewWithConfirmAddon_modes


if __name__ == "__main__":
    register()
