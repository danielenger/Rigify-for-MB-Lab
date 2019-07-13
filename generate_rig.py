import bpy
from mathutils import Vector


class RIGIFYFORMBLAB_OT_generaterig(bpy.types.Operator):
    bl_idname = "object.rigifyformblab_generaterig"
    bl_label = "Generate Rig"
    bl_description = "Generate Rigify Rig"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        is_muscle_rig = False

        rigify_rig = None
        muscle_rig = None

        muscle_parents = {}
        subtargets = {}

        legacy_mode = False
        if "legacy_mode" in context.preferences.addons['rigify'].preferences:
            legacy_mode = True if context.preferences.addons[
                'rigify'].preferences['legacy_mode'] == 1 else False

        # Muscle rig?
        for bone_name in bpy.context.active_object.data.bones.keys():
            if "muscle" in bone_name:
                is_muscle_rig = True
                break

        if not is_muscle_rig:
            bpy.ops.pose.rigify_generate()

        else:

            org_meta_rig = bpy.context.active_object

            bpy.ops.object.mode_set(mode='OBJECT')
            
            # Duplicate meta rig twice as muscle rig and meta rig (copy)
            bpy.context.view_layer.objects.active = org_meta_rig
            bpy.ops.object.duplicate()
            muscle_rig = bpy.context.active_object
            bpy.ops.object.duplicate()
            meta_rig = bpy.context.active_object

            muscle_rig.name = "TEMP_MUSCLE_RIG" + muscle_rig.name
            meta_rig.name = "TEMP_META_RIG" + meta_rig.name


            # Delete muscle and helper bones from meta rig
            bpy.ops.object.select_all(action='DESELECT')
            meta_rig.select_set(True)
            bpy.context.view_layer.objects.active = meta_rig

            bpy.ops.object.mode_set(mode='EDIT')
            meta_rig.data.layers[1] = True
            meta_rig.data.layers[2] = True
            bpy.ops.armature.select_all(action='DESELECT')
            bpy.ops.object.select_pattern(pattern="*muscle*")
            bpy.ops.object.select_pattern(pattern="*rot_helper*")
            bpy.ops.armature.delete()
            bpy.ops.object.mode_set(mode='OBJECT')


            # Start work on muscle rig
            bpy.ops.object.select_all(action='DESELECT')
            muscle_rig.select_set(True)
            bpy.context.view_layer.objects.active = muscle_rig
            bpy.ops.object.mode_set(mode='EDIT')

            # Rename muscle bones
            for name, bone in muscle_rig.data.edit_bones.items():
                if "rot_helper" in name:
                    bone.name = "MCH-" + name
                    bone.use_deform = False
                if "muscle" in name:
                    if "_H" in name or "_T" in name:
                        bone.name = "MCH-" + name
                        bone.use_deform = False
                    else:
                        bone.name = "DEF-" + name
            bpy.ops.object.mode_set(mode='OBJECT')

            # Save constraint subtargets - muscle rig
            bpy.ops.object.mode_set(mode='POSE')
            for name, bone in muscle_rig.pose.bones.items():
                if "rot_helper" in name or "muscle" in name:
                    temp_constraints = {}
                    for c_name, constraint in bone.constraints.items():
                        sub_name = constraint.subtarget
                        if "MCH" not in constraint.subtarget:
                            sub_name = "DEF-" + sub_name
                        temp_constraints[c_name] = sub_name
                    subtargets[name] = temp_constraints


            # Start editing muscle rig
            bpy.ops.object.mode_set(mode='EDIT')

            # Save the parents - muscle rig
            for name, bone in muscle_rig.data.edit_bones.items():
                if "rot_helper" in name or "muscle" in name:
                    if "MCH" not in bone.parent.name and "DEF" not in bone.parent.name:
                        legacy_parent_names = {
                            "thigh_L":"DEF-thigh.01_L", 
                            "thigh_R":"DEF-thigh.01_R", 
                            "calf_L":"DEF-calf.01_L", 
                            "calf_R":"DEF-calf.01_R", 
                            "upperarm_L":"DEF-upperarm.01_L",
                            "upperarm_R":"DEF-upperarm.01_R",
                            "lowerarm_L":"DEF-lowerarm.01_L",
                            "lowerarm_R":"DEF-lowerarm.01_R"
                            }
                        if legacy_mode:
                            if bone.parent.name in legacy_parent_names.keys():
                                parent_name = legacy_parent_names[bone.parent.name]
                            else:
                                parent_name = "DEF-" + bone.parent.name
                        else:
                            parent_name = "DEF-" + bone.parent.name
                    else:
                        parent_name = bone.parent.name
                    muscle_parents[name] = parent_name
                    

            # Unparent muscle bones - muscle rig
            for name, bone in bpy.context.active_object.data.edit_bones.items():
                if "rot_helper" in name or "muscle" in name:
                    bone.parent = None

            # Delete non-muscle bones from muscle rig
            bpy.ops.armature.select_all(action='DESELECT')
            for name, bone in muscle_rig.data.edit_bones.items():
                if not ("rot_helper" in name or "muscle" in name):
                    bone.select = True
            bpy.ops.armature.delete()

            # Move bones to layer 3 and 4
            for name, bone in muscle_rig.data.edit_bones.items():
                if "MCH" in name:
                    bone.layers[2] = True
                if "DEF" in name:
                    bone.layers[3] = True
            for name, bone in muscle_rig.data.edit_bones.items():
                if "MCH" in name or "DEF" in name:
                    bone.layers[0] = False
                    bone.layers[1] = False


            # Generate Rigify rig
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            meta_rig.select_set(True)
            bpy.context.view_layer.objects.active = meta_rig
            bpy.ops.pose.rigify_generate()
            rigify_rig = bpy.context.active_object

            # Delete meta rig (copy)
            bpy.ops.object.select_all(action='DESELECT')
            meta_rig.select_set(True)
            bpy.context.view_layer.objects.active = meta_rig
            bpy.ops.object.delete(use_global=False)

            # Join muscle rig with generated Rigify rig
            bpy.ops.object.select_all(action='DESELECT')
            muscle_rig.select_set(True)
            rigify_rig.select_set(True)
            bpy.context.view_layer.objects.active = rigify_rig
            bpy.ops.object.join()

            # Re-parent and reconnect muscle bones
            bpy.ops.object.mode_set(mode='EDIT')
            for bone_name, parent_name in muscle_parents.items():

                # Re-parent bones
                rigify_rig.data.edit_bones[bone_name].parent = rigify_rig.data.edit_bones[parent_name] # BUG key "DEF-thigh_R" not found'
# ###
#                         if legacy_mode:
#                             if bone.parent.name == "calf_L":
#                                 parent_name = "DEF-calf.01_L"
#                             elif bone.parent.name == "calf_R":
#                                 parent_name = "DEF-calf.01_R"
#                             else:
#                                 parent_name = "DEF-" + bone.parent.name
#                         else:
#                             parent_name = "DEF-" + bone.parent.name
# ###
                # Reconnect muscle bones
                if "muscle" in bone_name:
                    if not ("_H" in bone_name or "_T" in bone_name):
                        rigify_rig.data.edit_bones[bone_name].use_connect = True

            # Reestablish Constraint subtargets
            bpy.ops.object.mode_set(mode='POSE')
            for bone_name, constraint in subtargets.items():
                for c_name, sub_name in constraint.items():
                    rigify_rig.pose.bones[bone_name].constraints[c_name].subtarget = sub_name
        

        rigify_rig = bpy.context.active_object

        # Fix IK pole targets
        bpy.ops.object.mode_set(mode='EDIT')
        for ext in ["_L", "_R"]:
            if legacy_mode:
                thigh_name = "DEF-thigh.02_L"
                calf_name = "DEF-calf.01_L"
            else:
                thigh_name = "DEF-thigh" + ext
                calf_name = "DEF-calf" + ext

            h = rigify_rig.data.edit_bones[thigh_name].head.copy()
            t = rigify_rig.data.edit_bones[calf_name].tail.copy()
            m = (h + t) / 2
            if legacy_mode:
                name = "knee_target.ik" + ext
            else:
                name = "thigh" + ext + "_ik_target"
            rigify_rig.data.edit_bones[name].head.x = m[0]
            rigify_rig.data.edit_bones[name].tail.x = m[0]
            rigify_rig.data.edit_bones[name].head.z = m[2]
            rigify_rig.data.edit_bones[name].tail.z = m[2]
        
        bpy.ops.object.mode_set(mode='POSE')

        # Set "DEF-spine03" B-Bone handle
        bpy.context.object.data.bones["DEF-spine03"].bbone_handle_type_end = 'ABSOLUTE'
        
        # Fix custom shape scale
        if legacy_mode:        
            rigify_rig.pose.bones["hand.ik_L"].custom_shape_scale = 2.5
            rigify_rig.pose.bones["hand.ik_R"].custom_shape_scale = 2.5
            rigify_rig.pose.bones["hand.fk_L"].custom_shape_scale = 2.5
            rigify_rig.pose.bones["hand.fk_R"].custom_shape_scale = 2.5
        else:
            rigify_rig.pose.bones["hand_L_ik"].custom_shape_scale = 2.5
            rigify_rig.pose.bones["hand_R_ik"].custom_shape_scale = 2.5


        return {'FINISHED'}
