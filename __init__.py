#    Rigify Meta-Rig for MB-Lab
#    Copyright (C) 2019 Daniel Engler

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

bl_info = {
    "name": "Rigify Meta-Rig for MB-Lab",
    "description": "Add a Rigify Meta-Rig for MB-Lab Characters",
    "author": "Daniel Engler",
    "version": (0, 5, 6),
    "blender": (2, 80, 0),
    "location": "View3D > Tools > MB-Lab",
    "category": "Characters",
    "warning": "Weight paint for the neck bones needs to be done manually! MB-Lab rig has one neck bone. The default Rigify rig has two neck bones.",
}

import bpy

from . panel import RigifyMetaRigForMBLab_PT_panel
from . add_rig import RigifyMetaRigForMBLab_OT_add_rig
from . rename_vertex_groups import RigifyMetaRigForMBLab_OT_rename_mblab_to_rigify
from . rename_vertex_groups import RigifyMetaRigForMBLab_OT_rename_rigify_to_mblab
from . delete_face_rig import RigifyMetaRigForMBLab_OT_delete_face_rig

def register():
   bpy.utils.register_class(RigifyMetaRigForMBLab_OT_add_rig)
   bpy.utils.register_class(RigifyMetaRigForMBLab_OT_delete_face_rig)
   bpy.utils.register_class(RigifyMetaRigForMBLab_OT_rename_mblab_to_rigify)
   bpy.utils.register_class(RigifyMetaRigForMBLab_OT_rename_rigify_to_mblab)
   bpy.utils.register_class(RigifyMetaRigForMBLab_PT_panel)
    
def unregister():
   bpy.utils.unregister_class(RigifyMetaRigForMBLab_PT_panel)
   bpy.utils.unregister_class(RigifyMetaRigForMBLab_OT_rename_rigify_to_mblab)
   bpy.utils.unregister_class(RigifyMetaRigForMBLab_OT_rename_mblab_to_rigify)
   bpy.utils.unregister_class(RigifyMetaRigForMBLab_OT_delete_face_rig)
   bpy.utils.unregister_class(RigifyMetaRigForMBLab_OT_add_rig)


if __name__ == "__main__":
    register()