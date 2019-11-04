import bpy


class RIGIFYFORMBLAB_OT_enable_rigify(bpy.types.Operator):
    bl_idname = "object.rigifyformblab_enable_rigify"
    bl_label = "Enable Rigify add-on"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.preferences.addon_enable(module="rigify")
        return {'FINISHED'}


class RIGIFYFORMBLAB_PT_panel(bpy.types.Panel):
    bl_idname = "RIGIFYFORMBLAB_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Rigify for MB-Lab"
    # bl_context = "objectmode"
    bl_category = "Rigify for MB-Lab"

    def draw(self, context):

        legacy_mode = False
        addons = bpy.context.preferences.addons
        if "legacy_mode" in addons['rigify'].preferences:
            legacy_mode = addons['rigify'].preferences['legacy_mode'] == 1

        col = self.layout.column()

        if not "rigify" in context.preferences.addons.keys():
            col.operator('object.rigifyformblab_enable_rigify')
        else:
            col.operator('object.rigifyformblab_addrig')

            if legacy_mode:
                col.operator('object.rigifyformblab_generaterig')

            col.label(text="Rename Vertex Groups:")
            col.operator('object.rigifyformblab_rename_vertex_groups')
            col.operator('object.rigifyformblab_unrename_vertex_groups')

            # if legacy_mode:
            #     col.label(text="Manual Weight Paint:", icon='ERROR')
