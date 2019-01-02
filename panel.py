import bpy
# from bpy.types import Panel

class RigifyMetaRigForMBLab_PT_panel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Rigify Meta-Rig for MB-Lab"
    bl_context = "objectmode"
    bl_category = "MB-Lab"

    def draw(self, context):
        col = self.layout.column()

        col.operator('object.rigify_meta_rig_for_mblab_add_rig')
        col.operator('object.rigify_meta_rig_for_mblab_delete_face_rig')

        box = self.layout.box()
        box.label(text="Rename Vertex Groups:")
        box.operator('object.rigify_meta_rig_for_mblab_rename_mblab_to_rigify')
        box.operator('object.rigify_meta_rig_for_mblab_rename_rigify_to_mblab')
