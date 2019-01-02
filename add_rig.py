import bpy
from mathutils import Vector

# from . rigifymetarigformblab_functions import *

metarig_bone_names = { # metarig_bone : mblab_bone
    "spine":"pelvis",
    "spine.001":"spine01",
    "spine.002":"spine02",
    "spine.003":"spine03",
    # "spine.004":"neck", 
    # "spine.005":"neck",
    "spine.006":"head",

    "breast.L":"breast_L",
    "foot.L":"foot_L",
    "toe.L":"toes_L",
    "shoulder.L":"clavicle_L",
    "hand.L":"hand_L",
    "thumb.01.L":"thumb01_L",
    "thumb.02.L":"thumb02_L",
    "thumb.03.L":"thumb03_L",
    "palm.01.L":"index00_L",
    "f_index.01.L":"index01_L",
    "f_index.02.L":"index02_L",
    "f_index.03.L":"index03_L",
    "palm.02.L":"middle00_L",
    "f_middle.01.L":"middle01_L",
    "f_middle.02.L":"middle02_L",
    "f_middle.03.L":"middle03_L",
    "palm.03.L":"ring00_L",
    "f_ring.01.L":"ring01_L",
    "f_ring.02.L":"ring02_L",
    "f_ring.03.L":"ring03_L",
    "palm.04.L":"pinky00_L",
    "f_pinky.01.L":"pinky01_L",
    "f_pinky.02.L":"pinky02_L",
    "f_pinky.03.L":"pinky03_L",

    "breast.R":"breast_R",
    "foot.R":"foot_R",
    "toe.R":"toes_R",
    "shoulder.R":"clavicle_R",
    "hand.R":"hand_R",
    "thumb.01.R":"thumb01_R",
    "thumb.02.R":"thumb02_R",
    "thumb.03.R":"thumb03_R",
    "palm.01.R":"index00_R",
    "f_index.01.R":"index01_R",
    "f_index.02.R":"index02_R",
    "f_index.03.R":"index03_R",
    "palm.02.R":"middle00_R",
    "f_middle.01.R":"middle01_R",
    "f_middle.02.R":"middle02_R",
    "f_middle.03.R":"middle03_R",
    "palm.03.R":"ring00_R",
    "f_ring.01.R":"ring01_R",
    "f_ring.02.R":"ring02_R",
    "f_ring.03.R":"ring03_R",
    "palm.04.R":"pinky00_R",
    "f_pinky.01.R":"pinky01_R",
    "f_pinky.02.R":"pinky02_R",
    "f_pinky.03.R":"pinky03_R",
}
metarig_bone_arm_names = { # metarig_bone : mblab_bone
    "upper_arm.L":"upperarm_L",
    "forearm.L":"lowerarm_L",
    "upper_arm.R":"upperarm_R",
    "forearm.R":"lowerarm_R",
}

metarig_bone_leg_names = { # metarig_bone : mblab_bone - only legs, no feet!
    "thigh.L":"thigh_L",
    "shin.L":"calf_L",
    "thigh.R":"thigh_R",
    "shin.R":"calf_R",
}


class RigifyMetaRigForMBLab_OT_add_rig(bpy.types.Operator):
    bl_idname = "object.rigify_meta_rig_for_mblab_add_rig"
    bl_label = "Add Meta-Rig"
    bl_description = "MISSING" 
    bl_options = {'REGISTER', 'UNDO'} 

    settings = None
    
    bool_straight_legs : bpy.props.BoolProperty(name="Straight Legs",
                                                    description="", 
                                                    default=True)
    knee_offset_y : bpy.props.FloatProperty(name="Knee y Offset", 
                                                default=0.0,#-0.01,
                                                step=0.3,
                                                precision=3)


    def execute(self, context):
        # self.settings = context.scene.rigifymetarigformblab_settings
        
        mblab_rig = context.active_object

        meta_rig_bone_data = {} # store vectors for head, tail and roll for every meta bone -> "name of meta rig bone" : (head, tail, roll)

        # error handling: a rig needs to be active
        if not mblab_rig.type == 'ARMATURE':
            self.report({'ERROR'}, "Error: '{0}' is not an armature".format(mblab_rig.name))
            return {'CANCELLED'}
        
        ########
        # START edit mode for mblab armature
        ########
        bpy.ops.object.mode_set(mode='EDIT')
        # get bone data from mblab rig and store vectors (head, tail, roll) in meta_rig_bone_data dictionary
        for metarig_bone, mblab_bone in metarig_bone_names.items():
            b = mblab_rig.data.edit_bones[mblab_bone]
            meta_rig_bone_data[metarig_bone] = (b.head.copy(), b.tail.copy(), b.roll)
        # repeat for arm bones
        for metarig_bone, mblab_bone in metarig_bone_arm_names.items():
            b = mblab_rig.data.edit_bones[mblab_bone]
            meta_rig_bone_data[metarig_bone] = (b.head.copy(), b.tail.copy(), b.roll)
        

        # straight legs and knee offset fix for metarig
        if self.bool_straight_legs:
            tmp_leg_dict = {"thigh.L":"shin.L", "thigh.R":"shin.R", }
            for thigh_name, shin_name in tmp_leg_dict.items():
                mblab_thigh_name = metarig_bone_leg_names[thigh_name] # "thigh_L/R"
                mblab_shin_name = metarig_bone_leg_names[shin_name] # "calf_L/R"
                
                # new knee position for straight legs                    
                tmp_thigh_head = mblab_rig.data.edit_bones[mblab_thigh_name].head.copy()
                tmp_thigh_tail = mblab_rig.data.edit_bones[mblab_shin_name].tail.copy()
                tmp_thigh_roll = mblab_rig.data.edit_bones[mblab_thigh_name].roll
                tmp_shin_roll = mblab_rig.data.edit_bones[mblab_shin_name].roll
                new_length = mblab_rig.data.edit_bones[mblab_thigh_name].length 
                new_straight_legs_knee_pos = new_length * ( (tmp_thigh_tail - tmp_thigh_head).normalized() ) + tmp_thigh_head
                # y from mblab knee
                new_straight_legs_knee_pos.y = mblab_rig.data.edit_bones[mblab_shin_name].head.y
                new_knee_pos = new_straight_legs_knee_pos
                new_knee_pos.y = new_straight_legs_knee_pos.y + self.knee_offset_y

                meta_rig_bone_data[thigh_name] = (tmp_thigh_head, new_knee_pos, tmp_thigh_roll)
                meta_rig_bone_data[shin_name] = (new_knee_pos, tmp_thigh_tail, tmp_shin_roll)
        else:
            for metarig_bone, mblab_bone in metarig_bone_leg_names.items():
                b = mblab_rig.data.edit_bones[mblab_bone]
                meta_rig_bone_data[metarig_bone] = (b.head.copy(), b.tail.copy(), b.roll)


        # x location for metarig heels from mblab "foot_L/R" head
        foot_l_x = mblab_rig.data.edit_bones["foot_L"].head.x
        foot_r_x = mblab_rig.data.edit_bones["foot_R"].head.x


        # location for metarig "spine.004" head and "spine.005" head
        tmp_neck_bone = mblab_rig.data.edit_bones["neck"]

        spine005_head = tmp_neck_bone.length/2 * ( (tmp_neck_bone.tail - tmp_neck_bone.head).normalized() ) + tmp_neck_bone.head
        spine005_tail = tmp_neck_bone.tail.copy()
        spine005_roll = tmp_neck_bone.roll

        spine004_head = tmp_neck_bone.head.copy()
        spine004_tail = spine005_head
        spine004_roll = tmp_neck_bone.roll

        meta_rig_bone_data["spine.005"] = (spine005_head, spine005_tail, spine005_roll)
        meta_rig_bone_data["spine.004"] = (spine004_head, spine004_tail, spine004_roll)

        
        ########
        # END edit mode for mblab armature
        ########
        bpy.ops.object.mode_set(mode='OBJECT')
        

        # create meta rig
        #bpy.context.scene.cursor_location = mblab_rig.location
        bpy.ops.object.armature_human_metarig_add()
        meta_rig = context.active_object
        meta_rig.location = mblab_rig.location
        

        ########
        # START edit mode for meta-rig
        ########
        bpy.ops.object.mode_set(mode='EDIT')
        
        # metarig heels            
        foot_l_x = meta_rig_bone_data["foot.L"][0][0] # mblab_rig.data.edit_bones["foot_L"].head.x
        foot_r_x = meta_rig_bone_data["foot.R"][0][0] # mblab_rig.data.edit_bones["foot_R"].head.x
        # y and z from mblab object origin is the same for left and right
        heel_y = mblab_rig.location.y
        heel_z = mblab_rig.location.z            
        bone_name = "heel.02.L"
        bone_heel_l = meta_rig.data.edit_bones[bone_name]
        # metarig heel x location relative in middle to mblab foot head
        heel_l_head_x = (bone_heel_l.head.x - bone_heel_l.tail.x)/2 + foot_l_x
        heel_l_tail_x = (bone_heel_l.tail.x - bone_heel_l.head.x)/2 + foot_l_x
        # create new vectors from collected data
        bone_heel_l_head = Vector( (heel_l_head_x, heel_y, heel_z) )
        bone_heel_l_tail = Vector( (heel_l_tail_x, heel_y, heel_z) )
        bone_heel_l_roll = meta_rig.data.edit_bones[bone_name].roll
        # store data
        meta_rig_bone_data[bone_name] = (bone_heel_l_head, bone_heel_l_tail, bone_heel_l_roll)
        
        bone_name = "heel.02.R"
        bone_heel_r = meta_rig.data.edit_bones[bone_name]
        # metarig heel x location relative in middle to mblab foot head
        heel_r_head_x = (bone_heel_r.head.x - bone_heel_r.tail.x)/2 + foot_r_x
        heel_r_tail_x = (bone_heel_r.tail.x - bone_heel_r.head.x)/2 + foot_r_x
        # create new vectors from collected data
        bone_heel_r_head = Vector( (heel_r_head_x, heel_y, heel_z) )
        bone_heel_r_tail = Vector( (heel_r_tail_x, heel_y, heel_z) )
        bone_heel_r_roll = meta_rig.data.edit_bones[bone_name].roll
        # store data
        meta_rig_bone_data[bone_name] = (bone_heel_r_head, bone_heel_r_tail, bone_heel_r_roll)

        # meta rig pelvis
        new_pelvis_head = meta_rig_bone_data["spine"][0] # mblab_rig.data.edit_bones["pelvis"].head.copy()
        tmp_bone_list = ("pelvis.L", "pelvis.R")
        for bone_name in tmp_bone_list:
            pelvis_head = meta_rig.data.edit_bones[bone_name].head
            pelvis_tail = meta_rig.data.edit_bones[bone_name].tail
            new_pelvis_tail = (pelvis_tail - pelvis_head) + new_pelvis_head
            new_pelvis_roll = meta_rig.data.edit_bones[bone_name].roll            
            meta_rig_bone_data[bone_name] = (new_pelvis_head, new_pelvis_tail, new_pelvis_roll)
        
        # meta rig face rig
        relative_offset = meta_rig.data.edit_bones["face"].head.copy() - meta_rig_bone_data["spine.006"][0]
        for bone in meta_rig.data.edit_bones["face"].parent.children_recursive:                
            bone_name = bone.name
            new_h = bone.head.copy() - relative_offset
            new_t = bone.tail.copy() - relative_offset
            new_r = meta_rig.data.edit_bones[bone_name].roll
            meta_rig_bone_data[bone_name] = (new_h, new_t, new_r)
            
        # go through all bones in meta rig, pass the ones not needed
        for b in meta_rig.data.edit_bones:
            try:
                h, t, r = meta_rig_bone_data[b.name]
                b.head = h
                b.tail = t
                b.roll = r # roll needed for rigify?
            except:
                pass
        
        ########
        # END edit mode for meta-rig
        ########
        bpy.ops.object.mode_set(mode='OBJECT')
        

        return {'FINISHED'}
