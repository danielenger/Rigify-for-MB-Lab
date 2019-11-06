import bpy
from mathutils import Vector

def is_finger(name):
    finger_names = ['thumb', 'index', 'middle', 'ring', 'pinky']
    for f in finger_names:
        if f in name:
            return True
    return False


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

        mblab_mesh = None
        mblab_rig = None
        mblab_orig_bones = []
        for obj in bpy.data.objects.values():
            if 'manuellab_id' in obj.keys():
                mblab_mesh = obj
                if mblab_mesh.parent.type == 'ARMATURE':
                    mblab_rig = mblab_mesh.parent
                break

        if not mblab_mesh or not mblab_rig:
            print("Can't find mblab character. What's going on?")

        # keep a list of the original bones, minus the fingers. For some
        # reason these bones (minus the fingers) are kept in the rigify
        # rig and are not needed. I'm going to delete them at the end
        for pbone in mblab_rig.pose.bones:
            if not 'muscle' in pbone.name and not is_finger(pbone.name) and not 'root' in pbone.name:
                mblab_orig_bones.append(pbone.name)

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
            meta_rig = bpy.context.active_object
            bpy.context.view_layer.objects.active = meta_rig
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
                if ('DEF-lwrm' in name or 'DEF-tcs' in name or 'DEF-shld' in name \
                    or 'DEF-bcs' in name) and '_L' in name:
                    bone.layers[19] = True
                if ('MCH-lwrm' in name or 'MCH-tcs' in name or 'MCH-shld' in name \
                    or 'MCH-bcs' in name) and '_L' in name:
                    bone.layers[19] = True

                if ('DEF-lwrm' in name or 'DEF-tcs' in name or 'DEF-shld' in name \
                    or 'DEF-bcs' in name) and '_R' in name:
                    bone.layers[20] = True
                if ('MCH-lwrm' in name or 'MCH-tcs' in name or 'MCH-shld' in name \
                    or 'MCH-bcs' in name) and '_R' in name:
                    bone.layers[20] = True

                if ('DEF-lgs' in name or 'DEF-lwrl' in name) and '_L' in name:
                    bone.layers[21] = True
                if ('MCH-lgs' in name or 'MCH-lwrl' in name) and '_L' in name:
                    bone.layers[21] = True

                if ('DEF-lgs' in name or 'DEF-lwrl' in name) and '_R' in name:
                    bone.layers[22] = True
                if ('MCH-lgs' in name or 'MCH-lwrl' in name) and '_R' in name:
                    bone.layers[22] = True

                if 'DEF-abd' in name or 'DEF-spn' in name or 'DEF-pct' in name or \
                   'DEF-bk' in name or 'DEF-glt' in name:
                    bone.layers[23] = True
                if 'MCH-abd' in name or 'MCH-spn' in name or 'MCH-pct' in name or \
                   'MCH-bk' in name or 'MCH-glt' in name:
                    bone.layers[23] = True

                if 'DEF-nk' in name or 'MCH-nk' in name:
                    bone.layers[24] = True

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

        if is_muscle_rig:
            # clean extra bones left behind
            # TODO: for some reason when I set the layers it results in 
            # some bones from the original rig left behind,
            # but it's a bit wonky. The names have .00X after them, because
            # they have the same name as the rigify_rig bones. I need to
            # delete those to clean up. I kept an original list of the bones.
            # Now I need to adjust this list to account for this naming
            # discrepancy. I'll go with the assumption that if there exists a
            # name like the original, but has .00X pattern appended to it,
            # then that bone should be deleted.
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            rigify_rig.select_set(True)
            bpy.ops.object.mode_set(mode='EDIT')
            for bone in rigify_rig.pose.bones:
                for i in range(0, len(mblab_orig_bones)):
                    if mblab_orig_bones[i] in bone.name:
                        if '.00' in bone.name:
                            mblab_orig_bones[i] = bone.name
            bpy.ops.armature.select_all(action='DESELECT')
            for bn in mblab_orig_bones:
                bpy.ops.object.select_pattern(pattern=bn)
            bpy.ops.armature.delete()
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.context.object.display_type = 'SOLID'
            bpy.context.object.data.display_type = 'BBONE'

        return {'FINISHED'}
