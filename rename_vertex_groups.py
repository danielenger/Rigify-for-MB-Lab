import bpy

metarig_bone_names = { # metarig_bone : mblab_bone
    "spine":"pelvis",
    "spine.001":"spine01",
    "spine.002":"spine02",
    "spine.003":"spine03",
    # "spine.004":"neck", 
    "spine.005":"neck",
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

mblab_bone_names = { # mblab_bone : DEF-metarig_bone - for rename only
    "upperarm_twist_L":"DEF-upper_arm.L",
    "upperarm_L":"DEF-upper_arm.L.001",
    "lowerarm_twist_L":"DEF-forearm.L.001",
    "lowerarm_L":"DEF-forearm.L",
    "thigh_twist_L":"DEF-thigh.L",
    "thigh_L":"DEF-thigh.L.001",
    "calf_twist_L":"DEF-shin.L.001",
    "calf_L":"DEF-shin.L",
    "upperarm_twist_R":"DEF-upper_arm.R",
    "upperarm_R":"DEF-upper_arm.R.001",
    "lowerarm_twist_R":"DEF-forearm.R.001",
    "lowerarm_R":"DEF-forearm.R",
    "thigh_twist_R":"DEF-thigh.R",
    "thigh_R":"DEF-thigh.R.001",
    "calf_twist_R":"DEF-shin.R.001",
    "calf_R":"DEF-shin.R",
}

# add bone names from metarig_bone_names dict and add renamed to mblab_bone_names dict
def update_mblab_bone_names():
    for metarig_bone, mblab_bone in metarig_bone_names.items():
        mblab_bone_names[mblab_bone] = "DEF-" + metarig_bone

class RigifyMetaRigForMBLab_OT_rename_mblab_to_rigify(bpy.types.Operator):
    """Rename Vertex Groups to match Rigify Rig
    - select the character mesh first"""
    bl_idname = "object.rigify_meta_rig_for_mblab_rename_mblab_to_rigify"
    bl_label = "MB-Lab to Rigify"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        mblab_mesh = context.active_object
        if mblab_mesh.type == 'MESH':
            update_mblab_bone_names()
            # go through mblab_bone_names dictinary and try rename vertex groups
            for mblab_bone, metarig_bone in mblab_bone_names.items():
                try:
                    mblab_mesh.vertex_groups[mblab_bone].name = metarig_bone
                except:
                    print("Error: '%s' could not be found in vertex groups" % mblab_bone)
        else:
            print("Error: '%s' is not a mesh object" % mblab_mesh.name)
        return {'FINISHED'}

class RigifyMetaRigForMBLab_OT_rename_rigify_to_mblab(bpy.types.Operator):
    """Rename Vertex Groups to match MB-Lab rig
    - select the character mesh first"""
    bl_idname = "object.rigify_meta_rig_for_mblab_rename_rigify_to_mblab"
    bl_label = "Rigify to MB-Lab"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        mblab_mesh = context.active_object
        if mblab_mesh.type == 'MESH':
            update_mblab_bone_names()
            # go through mblab_bone_names dictinary and try rename vertex groups
            for mblab_bone, metarig_bone in mblab_bone_names.items():
                try:
                    mblab_mesh.vertex_groups[metarig_bone].name = mblab_bone
                except:
                    print("Error: '%s' could not be found in vertex groups" % metarig_bone)
        else:
            print("Error: '%s' is not a mesh object" % mblab_mesh.name)
        return {'FINISHED'}
