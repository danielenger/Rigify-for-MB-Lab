import math
import bpy
from mathutils import Vector


class RIGIFYFORMBLAB_OT_addrig(bpy.types.Operator):
    bl_idname = "object.rigifyformblab_addrig"
    bl_label = "Add Meta Rig"
    bl_description = "Add Meta Rig"
    bl_options = {'REGISTER', 'UNDO'}

    bool_straight_legs: bpy.props.BoolProperty(name="Straight Legs",
                                               description="",
                                               default=False)

    knee_offset_y: bpy.props.FloatProperty(name="Knee y Offset",
                                                default=0.0,  # -0.01,
                                                step=0.3,
                                                precision=3)

    bool_super_finger: bpy.props.BoolProperty(name="Finger Rig Type: limbs.super_finger (non-legacy)",
                                              description="",
                                              default=False)

    def execute(self, context):

        mblab_rig = None

        is_muscle_rig = False
        is_ik_rig = False

        legacy_mode = False
        if "legacy_mode" in context.preferences.addons['rigify'].preferences:
            legacy_mode = True if context.preferences.addons[
                'rigify'].preferences['legacy_mode'] == 1 else False

        # Get MB-lab rig
        mblab_mesh = None
        for obj in bpy.data.objects.values():
            if 'manuellab_id' in obj.keys():
                mblab_mesh = obj
                if mblab_mesh.parent.type == 'ARMATURE':
                    mblab_rig = mblab_mesh.parent
                break

        if not mblab_mesh:
            self.report({'ERROR'}, 'MB-Lab rig not found!')
            return {'CANCELLED'}


        # Muscle rig?
        for bone_name in mblab_rig.data.bones.keys():
            if "muscle" in bone_name:
                is_muscle_rig = True
                break

        # IK rig?
        for bone_name in mblab_rig.data.bones.keys():
            if "IK" in bone_name:
                is_ik_rig = True
                break

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

        # Duplicate MB-lab rig
        mblab_rig.hide_viewport = False
        context.view_layer.objects.active = mblab_rig
        mblab_rig.select_set(True)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.duplicate()
        meta_rig = context.active_object
        meta_rig.name = mblab_rig.name + "_metarig"
        bpy.ops.object.mode_set(mode='OBJECT')

        # Delete IK and struct bones
        if is_ik_rig:
            bpy.ops.object.mode_set(mode='EDIT')
            meta_rig.data.layers[0] = True
            meta_rig.data.layers[1] = True
            meta_rig.data.layers[2] = True
            bpy.ops.armature.select_all(action='DESELECT')

            for bone_name, bone in meta_rig.data.edit_bones.items():
                if "IK" in bone_name or "struct" in bone_name:
                    bone.select = True
            bpy.ops.armature.delete()

            bpy.ops.armature.select_all(action='SELECT')
            bpy.ops.armature.bone_layers(layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False,
                                                 False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            meta_rig.data.layers[1] = False
            meta_rig.data.layers[2] = False


            meta_rig.data.edit_bones['head'].use_connect = True

            # Delete constraints
            bpy.ops.object.mode_set(mode='POSE')
            for bone_name, bone in meta_rig.pose.bones.items():
                if not ("rot_helper" in bone_name or "muscle" in bone_name):
                    for constraint in bone.constraints.values():
                        bone.constraints.remove(constraint)
            
            bpy.ops.object.mode_set(mode='OBJECT')


        # Fix dislocated joints in thigh and calf
        if is_muscle_rig:
            bpy.ops.object.mode_set(mode='EDIT')
            for ext in ["_L", "_R"]:
                calf_head = meta_rig.data.edit_bones["calf" + ext].head.copy()
                foot_head = meta_rig.data.edit_bones["foot" + ext].head.copy()
                meta_rig.data.edit_bones["thigh" + ext].tail = calf_head
                meta_rig.data.edit_bones["calf" + ext].tail = foot_head
            bpy.ops.object.mode_set(mode='OBJECT')


        # Straight legs and knee offset fix
        if self.bool_straight_legs:
            for ext in ["_L", "_R"]:

                thigh_name = "thigh" + ext
                calf_name = "calf" + ext

                meta_rig.select_set(False)
                mblab_rig.select_set(True)
                context.view_layer.objects.active = mblab_rig

                bpy.ops.object.mode_set(mode='EDIT')

                thigh_head = context.active_object.data.edit_bones[thigh_name].head.copy()
                thigh_tail = context.active_object.data.edit_bones[calf_name].tail.copy()
                new_length = context.active_object.data.edit_bones[thigh_name].length
                new_straight_legs_knee_pos = new_length * \
                    ((thigh_tail - thigh_head).normalized()) + thigh_head
                new_straight_legs_knee_pos.y = context.active_object.data.edit_bones[
                    calf_name].head.y
                new_knee_pos = new_straight_legs_knee_pos
                new_knee_pos.y = new_straight_legs_knee_pos.y + self.knee_offset_y

                if not is_muscle_rig:
                    thigh_twist_name = "thigh_twist" + ext
                    calf_twist_name = "calf_twist" + ext                    
                    thigh_twist_len = context.active_object.data.edit_bones[thigh_twist_name].length
                    thigh_twist_tail = thigh_twist_len * \
                        ((new_knee_pos - thigh_head).normalized()) + thigh_head
                    calf_twist_len = context.active_object.data.edit_bones[calf_twist_name].length
                    calf_tail = context.active_object.data.edit_bones[calf_name].tail.copy()
                    calf_twist_tail = calf_twist_len * \
                        ((calf_tail - new_knee_pos).normalized()) + new_knee_pos


                bpy.ops.object.mode_set(mode='OBJECT')

                meta_rig.select_set(True)
                mblab_rig.select_set(False)
                context.view_layer.objects.active = meta_rig

                bpy.ops.object.mode_set(mode='EDIT')

                context.active_object.data.edit_bones[thigh_name].tail = new_knee_pos

                if not is_muscle_rig:
                    context.active_object.data.edit_bones[thigh_twist_name].tail = thigh_twist_tail

                    context.active_object.data.edit_bones[calf_twist_name].head = new_knee_pos
                    context.active_object.data.edit_bones[calf_twist_name].tail = calf_twist_tail

                bpy.ops.object.mode_set(mode='OBJECT')


        bpy.ops.object.mode_set(mode='EDIT')

        # Fix rolls
        bpy.ops.armature.select_all(action='DESELECT')
        for bone_name in ["thigh", "calf"]:
            for ext in ["_L", "_R"]:
                name = bone_name + ext
                meta_rig.data.edit_bones[name].select = True
        bpy.ops.armature.calculate_roll(type='GLOBAL_POS_Y')

        bpy.ops.armature.select_all(action='DESELECT')
        meta_rig.data.edit_bones["foot_L"].select = True
        meta_rig.data.edit_bones["foot_R"].select = True
        bpy.ops.armature.calculate_roll(type='GLOBAL_NEG_Z')

        bpy.ops.armature.select_all(action='DESELECT')
        meta_rig.data.edit_bones["toes_L"].select = True
        meta_rig.data.edit_bones["toes_R"].select = True
        bpy.ops.armature.calculate_roll(type='GLOBAL_POS_Z')

        if is_muscle_rig:
            for bone_name in ["rot_helper01", "rot_helper03", "rot_helper06"]:
                for ext in ["_L", "_R"]:
                    name = bone_name + ext
                    meta_rig.data.edit_bones[name].roll = meta_rig.data.edit_bones[name].roll + math.pi

            meta_rig.data.edit_bones["clavicle_L"].roll = math.radians(94.6248)
            meta_rig.data.edit_bones["clavicle_R"].roll = math.radians(-94.6248)


        # Fix disconnected toes
        meta_rig.data.edit_bones['toes_L'].use_connect = True
        meta_rig.data.edit_bones['toes_R'].use_connect = True

        # Disconnect upperarms from clavicle
        meta_rig.data.edit_bones['upperarm_L'].use_connect = False
        meta_rig.data.edit_bones['upperarm_R'].use_connect = False

        # re-parent thumbs
        meta_rig.data.edit_bones[
            'thumb01_L'].parent = meta_rig.data.edit_bones['index00_L']
        meta_rig.data.edit_bones[
            'thumb01_R'].parent = meta_rig.data.edit_bones['index00_R']

        # Connect spine with neck
        meta_rig.data.edit_bones['spine03'].tail = meta_rig.data.edit_bones['neck'].head.copy()
        if not legacy_mode:
            meta_rig.data.edit_bones['neck'].use_connect = True

        # Legacy mode settings:
        if legacy_mode:
            
            # legacy_mode finger roll
            for ext in ["_L","_R"]:
                for bone in meta_rig.data.edit_bones["hand" + ext].children_recursive:
                    bone.roll = bone.roll + math.pi
        
            # legacy_mode unparent "twist" bones
            for bone_name, bone in meta_rig.data.edit_bones.items():
                if "twist" in bone_name:
                    bone.parent = None

        # Create heels
        if legacy_mode:

            for ext in ["_L", "_R"]:
                bone_heel = meta_rig.data.edit_bones.new("heel" + ext)
                foot_bone = meta_rig.data.edit_bones["foot" + ext]
                heel_tail_x = foot_bone.head.x
                bone_heel.tail = Vector((heel_tail_x, mblab_rig.location.y, mblab_rig.location.z))
                bone_heel.use_connect = True
                bone_heel.parent = meta_rig.data.edit_bones["calf" + ext]
    
        else:
            for ext in ["_L", "_R"]:
                bone_name = "heel" + ext
                bone_heel = meta_rig.data.edit_bones.new(bone_name)
                bone_heel.bbone_x = 0.01
                bone_heel.bbone_z = 0.01
                foot_bone = meta_rig.data.edit_bones["foot" + ext]
                # heel x location relative to foot head
                bone_heel.tail.x = 0.1 if ext == "_L" else -0.1
                heel_head_x = (bone_heel.tail.x - foot_bone.head.x) / \
                    2 + foot_bone.head.x
                heel_tail_x = (foot_bone.head.x - bone_heel.tail.x) / \
                    2 + foot_bone.head.x
                bone_heel.head = Vector((heel_head_x, mblab_rig.location.y, mblab_rig.location.z))
                bone_heel.tail = Vector((heel_tail_x, mblab_rig.location.y, mblab_rig.location.z))
                # parent
                bone_heel.use_connect = False
                bone_heel.parent = foot_bone

        # Inherit scale
        for bone in meta_rig.data.edit_bones.values():
            bone.use_inherit_scale = True

        # Unlock transforms
        for name, bone in meta_rig.pose.bones.items():
            bone.lock_location[0] = False
            bone.lock_location[1] = False
            bone.lock_location[2] = False
            bone.lock_scale[0] = False
            bone.lock_scale[1] = False
            bone.lock_scale[2] = False

        # TODO rigify layers

        # set rigify types
        if legacy_mode:

            meta_rig.pose.bones["pelvis"].rigify_type = "spine"
            meta_rig.pose.bones["pelvis"].rigify_parameters.chain_bone_controls = "1, 2, 3, 4"
            
            meta_rig.pose.bones["neck"].rigify_type = "neck_short"

            for bone_name in ["clavicle_L", "clavicle_R", "breast_L", "breast_R"]:
                meta_rig.pose.bones[bone_name].rigify_type = "basic.copy"

            for ext in ["_L", "_R"]:
                bone_name = 'thigh' + ext
                meta_rig.pose.bones[bone_name].rigify_type = "biped.leg"

                bone_name = 'upperarm' + ext
                meta_rig.pose.bones[bone_name].rigify_type = "biped.arm"

                meta_rig.pose.bones["index00" + ext].rigify_type = "palm"

                for name in ['thumb01', 'index01', 'middle01', 'ring01', 'pinky01']:
                    bone_name = name + ext
                    meta_rig.pose.bones[bone_name].rigify_type = "finger"

        else:

            meta_rig.pose.bones["pelvis"].rigify_type = "spines.super_spine"
            meta_rig.pose.bones["pelvis"].rigify_parameters['neck_pos'] = 5

            for bone_name in ["clavicle_L", "clavicle_R", "breast_L", "breast_R"]:
                meta_rig.pose.bones[bone_name].rigify_type = "basic.super_copy"

            limb_segments = 1 if is_muscle_rig else 2

            for ext in ["_L", "_R"]:
                bone_name = 'thigh' + ext
                meta_rig.pose.bones[bone_name].rigify_type = "limbs.super_limb"
                meta_rig.pose.bones[bone_name].rigify_parameters.limb_type = 'leg'
                meta_rig.pose.bones[bone_name].rigify_parameters.segments = limb_segments
                meta_rig.pose.bones[bone_name].rigify_parameters.rotation_axis = 'x'

                bone_name = 'upperarm' + ext
                meta_rig.pose.bones[bone_name].rigify_type = "limbs.super_limb"
                meta_rig.pose.bones[bone_name].rigify_parameters.limb_type = 'arm'
                meta_rig.pose.bones[bone_name].rigify_parameters.segments = limb_segments

                meta_rig.pose.bones["index00" +
                                            ext].rigify_type = "limbs.super_palm"

                for name in ['thumb01', 'index01', 'middle01', 'ring01', 'pinky01']:
                    bone_name = name + ext
                    meta_rig.pose.bones[bone_name].rigify_type = "limbs.simple_tentacle"

        meta_rig.data.bones["breast_L"].hide = False
        meta_rig.data.bones["breast_R"].hide = False


        # fix crooked fingers
        finger_names = ["thumb", "index", "middle", "ring", "pinky"]
        if not legacy_mode:
            for finger_name in finger_names:
                for ext in ["_L", "_R"]:
                    bone_name = finger_name + "01" + ext
                    if self.bool_super_finger:
                        meta_rig.pose.bones[bone_name].rigify_type = "limbs.super_finger"
                        meta_rig.pose.bones[bone_name].rigify_parameters.primary_rotation_axis = 'X'
                    else:
                        meta_rig.pose.bones[bone_name].rigify_parameters.roll_alignment = 'manual'

        bpy.ops.object.mode_set(mode='POSE')

        return {'FINISHED'}
