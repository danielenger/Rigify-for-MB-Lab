import bpy
# from bpy.types import Operator

# class RIGIFYMETARIGFORMBLAB_OT_deletefacerig(Operator):
class RigifyMetaRigForMBLab_OT_delete_face_rig(bpy.types.Operator):
    """Delete Face Rig from Rigify Meta-Rig
    - select the character mesh first"""
    bl_idname = "object.rigify_meta_rig_for_mblab_delete_face_rig"
    bl_label = "Delete Face Rig"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        meta_rig = context.active_object
        if meta_rig.type == 'ARMATURE':
            bone_name = "face"
            if bone_name in meta_rig.data.bones:
                bpy.ops.object.mode_set(mode='EDIT')
                for b in meta_rig.data.edit_bones:
                    b.select = False                
                for b in meta_rig.data.edit_bones[bone_name].parent.children_recursive:
                    b.select = True
                bpy.ops.armature.delete()
                bpy.ops.object.mode_set(mode='OBJECT')
            else:
                print("Error: '%s' not found in armature" % bone_name)
        return {'FINISHED'}
