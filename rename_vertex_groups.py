import bpy


mblab_base_bone_names = {  # mblab_bone : DEF-metarig_bone
    "upperarm_twist_L": "DEF-upperarm_L",
    "upperarm_L":       "DEF-upperarm_L.001",
    "lowerarm_L":       "DEF-lowerarm_L",
    "lowerarm_twist_L": "DEF-lowerarm_L.001",

    "upperarm_twist_R": "DEF-upperarm_R",
    "upperarm_R":       "DEF-upperarm_R.001",
    "lowerarm_R":       "DEF-lowerarm_R",
    "lowerarm_twist_R": "DEF-lowerarm_R.001",

    "thigh_twist_L": "DEF-thigh_L",
    "thigh_L":       "DEF-thigh_L.001",
    "thigh_twist_R": "DEF-thigh_R",
    "thigh_R":       "DEF-thigh_R.001",

    "calf_twist_L": "DEF-calf_L.001",
    "calf_L":       "DEF-calf_L",
    "calf_twist_R": "DEF-calf_R.001",
    "calf_R":       "DEF-calf_R",
}

mblab_muscle_bone_names = {  # mblab_bone : DEF-metarig_bone
    "upperarm_L":       "DEF-upperarm_L",
    "lowerarm_L":       "DEF-lowerarm_L",
    "upperarm_R":       "DEF-upperarm_R",
    "lowerarm_R":       "DEF-lowerarm_R",

    "thigh_L":      "DEF-thigh_L",
    "thigh_R":      "DEF-thigh_R",
    "calf_L":       "DEF-calf_L",
    "calf_R":       "DEF-calf_R",
}

mblab_base_bone_names_legacy_mode = {  # mblab_bone : DEF-metarig_bone
    "upperarm_twist_L": "DEF-upperarm.01_L",
    "upperarm_L":       "DEF-upperarm.02_L",
    "lowerarm_twist_L": "DEF-lowerarm.01_L",
    "lowerarm_L":       "DEF-lowerarm.02_L",

    "upperarm_twist_R": "DEF-upperarm.01_R",
    "upperarm_R":       "DEF-upperarm.02_R",
    "lowerarm_twist_R": "DEF-lowerarm.01_R",
    "lowerarm_R":       "DEF-lowerarm.02_R",

    "thigh_twist_L": "DEF-thigh.01_L",
    "thigh_L":       "DEF-thigh.02_L",
    "thigh_twist_R": "DEF-thigh.01_R",
    "thigh_R":       "DEF-thigh.02_R",
    
    "calf_twist_L":  "DEF-calf.01_L",
    "calf_L":        "DEF-calf.02_L",
    "calf_twist_R":  "DEF-calf.01_R",
    "calf_R":        "DEF-calf.02_R",

    "thumb01_L":    "DEF-thumb01_L.01", # TODO test this!
    "index01_L":    "DEF-index01_L.01",
    "middle01_L":   "DEF-middle01_L.01",
    "ring01_L":     "DEF-ring01_L.01",
    "pinky01_L":    "DEF-pinky01_L.01",

    "thumb01_R":    "DEF-thumb01_R.01",
    "index01_R":    "DEF-index01_R.01",
    "middle01_R":   "DEF-middle01_R.01",
    "ring01_R":     "DEF-ring01_R.01",
    "pinky01_R":    "DEF-pinky01_R.01",
}


def legacy_mode():
    addons = bpy.context.preferences.addons
    if "legacy_mode" in addons['rigify'].preferences:
        if addons['rigify'].preferences['legacy_mode'] == 1:
            return True
    return False

def is_muscle_char(obj):
    for name in obj.vertex_groups.keys():
        if "muscle" in name:
            return True
    return False


class RIGIFYFORMBLAB_OT_rename_vertex_groups(bpy.types.Operator):
    bl_idname = "object.rigifyformblab_rename_vertex_groups"
    bl_label = "Rename to 'DEF-*'"
    bl_description = "Rename vertex groups for Rigify Rig"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        char = context.active_object

        if legacy_mode():
            for mblab_bone, metarig_bone in mblab_base_bone_names_legacy_mode.items():
                if mblab_bone in char.vertex_groups:
                    char.vertex_groups[mblab_bone].name = metarig_bone
        else:
            if is_muscle_char(char):
                for mblab_bone, metarig_bone in mblab_muscle_bone_names.items():
                    if mblab_bone in char.vertex_groups:
                        char.vertex_groups[mblab_bone].name = metarig_bone
            else:
                for mblab_bone, metarig_bone in mblab_base_bone_names.items():
                    if mblab_bone in char.vertex_groups:
                        char.vertex_groups[mblab_bone].name = metarig_bone

        for name, v_group in char.vertex_groups.items():
            if not name.startswith("DEF-"):
                v_group.name = "DEF-" + name

        return {'FINISHED'}


class RIGIFYFORMBLAB_OT_unrename_vertex_groups(bpy.types.Operator):
    bl_idname = "object.rigifyformblab_unrename_vertex_groups"
    bl_label = "Undo Rename"
    bl_description = "Reverse renamed vertex groups"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        char = context.active_object

        if legacy_mode():
            for mblab_bone, metarig_bone in mblab_base_bone_names_legacy_mode.items():
                if metarig_bone in char.vertex_groups:
                    char.vertex_groups[metarig_bone].name = mblab_bone
        else:
            if is_muscle_char(char):
                for mblab_bone, metarig_bone in mblab_muscle_bone_names.items():
                    if metarig_bone in char.vertex_groups:
                        char.vertex_groups[metarig_bone].name = mblab_bone
            else:
                for mblab_bone, metarig_bone in mblab_base_bone_names.items():
                    if metarig_bone in char.vertex_groups:
                        char.vertex_groups[metarig_bone].name = mblab_bone

        for name, v_group in char.vertex_groups.items():
            if name.startswith("DEF-"):
                v_group.name = name.lstrip("DEF-")

        return {'FINISHED'}
