
bl_info = {
    'name': "Blender Extension Test",
    'author': 'mmt3d',
    'version': (2026, 7, 7),
    'blender': (3, 3, 0),
    'location': "location test",
    'description': "description test",
    'warning': "",
    'wiki_url': 'https://github.com/mmt3d/bl-ext-test/blob/main/README.md',
    'tracker_url': 'https://github.com/mmt3d/bl-ext-test',
    'category': 'Import-Export'
}

import bpy

class SIMPLEADDON_OT_hello(bpy.types.Operator):
    bl_idname = "simple_addon.say_hello"
    bl_label = "Say Hello13"
    bl_description = "Prints a message to the console"
    def execute(self, context):
        self.report({'INFO'}, "Hello13 from Blender Addon!")
        print("Hello13 from Blender Addon!")
        return {'FINISHED'}


class SIMPLEADDON_PT_panel(bpy.types.Panel):
    bl_label = "Simple Addon Panel"
    bl_idname = "SIMPLEADDON_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Simple'
    def draw(self, context):
        layout = self.layout
        layout.operator("simple_addon.say_hello")


def register():
    bpy.utils.register_class(SIMPLEADDON_OT_hello)
    bpy.utils.register_class(SIMPLEADDON_PT_panel)


def unregister():
    bpy.utils.unregister_class(SIMPLEADDON_PT_panel)
    bpy.utils.unregister_class(SIMPLEADDON_OT_hello)
