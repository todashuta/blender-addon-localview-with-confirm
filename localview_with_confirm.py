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
    "name": "Safe Localview",
    "author": "todashuta",
    "version": (0, 0, 4),
    "blender": (3, 3, 0),
    "location": "-",
    "description": "-",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "3D View"
}


import bpy


def get_addon_prefs():
    addon_prefs = bpy.context.preferences.addons[__name__].preferences
    return addon_prefs


shading_types = {
        "WIREFRAME": "Wireframe",
        "SOLID": "Solid",
}


class SafeLocalviewOperator(bpy.types.Operator):
    bl_idname = "view3d.safe_localview"
    bl_label = "Safe Localview"

    @classmethod
    def poll(cls, context):
        return bpy.ops.view3d.localview.poll()

    def execute(self, context):
        prefs = get_addon_prefs()
        in_localview = context.space_data.local_view is not None
        shading_type = context.space_data.shading.type
        if (in_localview and
                shading_type in {'MATERIAL', 'RENDERED'}):
            t = prefs.preferred_shading_type
            context.space_data.shading.type = t
            msg = f"Viewport Shading changed to {shading_types[t]}"
            self.report({"INFO"}, msg)

        return bpy.ops.view3d.localview(frame_selected=prefs.frame_selected)


def auto_rebind(self, context):
    unregister_keymaps()
    register_keymaps()


class SafeLocalviewPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    items = (
            ("WIREFRAME", "Wireframe", ""),
            ("SOLID",     "Solid",     ""))
    preferred_shading_type: bpy.props.EnumProperty(
            name="Preferred Shading Type",
            items=items)

    frame_selected: bpy.props.BoolProperty(
            name="Frame Selected",
            description="Move the view to frame the selected objects",
            default=True)

    use_shortcut: bpy.props.BoolProperty(
            name="Use Default Shortcut",
            default=True,
            update=auto_rebind)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "preferred_shading_type")
        row.prop(self, "frame_selected")
        row.prop(self, "use_shortcut")


addon_keymaps = []
def register_keymaps():
    prefs = get_addon_prefs()
    if not prefs.use_shortcut:
        return

    kc = bpy.context.window_manager.keyconfigs.addon
    if not kc:
        return

    km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new(SafeLocalviewOperator.bl_idname, "SLASH", "PRESS")
    addon_keymaps.append((km, kmi))

    km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new(SafeLocalviewOperator.bl_idname, "NUMPAD_SLASH", "PRESS")
    addon_keymaps.append((km, kmi))

def unregister_keymaps():
    for km,kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


classes = (
        SafeLocalviewPreferences,
        SafeLocalviewOperator,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    register_keymaps()


def unregister():
    unregister_keymaps()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
