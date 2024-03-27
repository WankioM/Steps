"""
TO DO:
    1. Make sure when someone exports , they are told  it can only be exported as admin
    2. Make sure "Export actually works
    """


import bpy
import copy
import math
from itertools import zip_longest

# Global variable to hold recorded steps
# Store previous state information
previous_mesh_info = {}
previous_location = None
starting_location = None
starting_rotation= None
previous_rotation= None
starting_scale=None
previous_scale= None
steps = []
logged_op = None
translation= False
initial_mat= None
mat_change=False
slot_ids={}
initial_mods={}

def get_starting_loc():
    global starting_location
    obj = bpy.context.active_object
    if obj and obj.type == 'MESH':       
        starting_location = ( copy.deepcopy(obj.location), True) 
        print (starting_location)
        

def get_pos_transform (start, end):
    
    global steps
    
    
    
    translation = tuple(e - s for e, s in zip(end, start))
    print(f"The translation vector is: {translation}")
    
    command = (
        f"bpy.ops.transform.translate("
        f"value=({translation[0]}, {translation[1]}, {translation[2]}), "
        f"orient_type='GLOBAL', "
        f"orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), "
        f"orient_matrix_type='GLOBAL', "
        f"mirror=False, "
        f"use_proportional_edit=False, "
        f"proportional_edit_falloff='SMOOTH', "
        f"proportional_size=1, "
        f"use_proportional_connected=False, "
        f"use_proportional_projected=False, "
        f"snap=False, "
        f"snap_elements={{'INCREMENT'}}, "
        f"use_snap_project=False, "
        f"snap_target='CLOSEST', "
        f"use_snap_self=True, "
        f"use_snap_edit=True, "
        f"use_snap_nonedit=True, "
        f"use_snap_selectable=False, "
        f"alt_navigation=True)"
    )
    print(f"\n Command: {command}")
    steps.append(command)
    return command


def get_starting_rotation():
    global starting_rotation
    obj = bpy.context.active_object
    if obj and obj.type == 'MESH':  
        
        rot = obj.rotation_euler
        
        # Extract rotations around X, Y, and Z axes (in radians)
        rotation_x = rot.x
        rotation_y = rot.y
        rotation_z = rot.z
        
        rotation= (rotation_x , rotation_y , rotation_z )     
        
        starting_rotation = copy.deepcopy(rotation)
        print (f"\n Rotation {starting_rotation}")
        

def rotation_command (start, end):
    
    global steps
    global starting_rotation
    
    print(f"start {start} end {end} in deg {tuple(math.degrees(angle) for angle in end)}")
    
    if end is not None and start is not None and len(end) == len(start):
        rotation = tuple(e - s for e, s in zip(end, start))
    
    else:
        # Handle the case when 'end' or 'start' is None or they have different lengths
        print("Error: 'end' or 'start' is None, or they have different lengths.")
        rotation = None  
    print(f"The rotation vector is: {rotation}")
    
 
    if rotation[0] != 0:  # X-axis rotation
        command_x = (
            f"bpy.ops.transform.rotate(value={-(rotation[0])}, "
            f"orient_axis='X')"
        )
        steps.append(command_x)

    if rotation[1] != 0:  # Y-axis rotation
        command_y = (
            f"bpy.ops.transform.rotate(value={-(rotation[1])}, "
            f"orient_axis='Y')"
        )
        steps.append(command_y)

    if rotation[2] != 0:  # Z-axis rotation
        command_z = (
            f"bpy.ops.transform.rotate(value={-(rotation[2])}, "
            f"orient_axis='Z')"
        )
        steps.append(command_z)
        
        

def get_starting_scale():
    global starting_scale
    obj = bpy.context.active_object
    if obj and obj.type == 'MESH':       
        starting_scale = copy.deepcopy(obj.scale)
        print (starting_scale)
        

def get_scale_factor(start, end):
    
    global steps
    
    
    
 
    print(f"starting scale {start} end {end}")
    factor = tuple(e / s for e, s in zip(end, start))
    print(f"The scale factor is: {factor}")
    
    command = (
    f"bpy.ops.transform.resize("
    f"value=({factor[0]}, {factor[1]}, {factor[2]}), "
    f"orient_type='GLOBAL')"
)

    print(f"\n Command: {command}")
    steps.append(command)
    return command
    


    

def log_mesh_changes(dummy):
    
    obj = bpy.context.active_object
    
    
    global logged_op
    global translation
    global previous_mesh_info
    global previous_location
    global starting_location
    global starting_scale
    global previous_rotation
    global previous_scale
    
    
    
    if obj and obj.type == 'MESH':
        
        # Get the last operator executed
        last_operator = bpy.context.window_manager.operators[-1].bl_idname
        
        # only log the last operator if it has changed to prevent millions of lines
        if last_operator != logged_op:
            print(f'Lasty Operator {last_operator} lop {logged_op}')
            
            logged_op=last_operator
            
            #check if operator was a translation one
            if last_operator == 'TRANSFORM_OT_translate':
                translation = True
            
        # Track mesh modifications (vertices, edges, faces)
        mesh_data = obj.data
        vertices_count = len(mesh_data.vertices)
        edges_count = len(mesh_data.edges)
        faces_count = len(mesh_data.polygons)
        
        mesh_changes = {
            'vertices': vertices_count,
            'edges': edges_count,
            'faces': faces_count
        }
        
        if previous_mesh_info:
            # Compare previous state with current state
            for key, value in mesh_changes.items():
                if previous_mesh_info.get(key) != value:
                    print(f' Debug  key: {previous_mesh_info.get(key)} value: {value}')
                    print(f"Mesh {key} count changed: {value}")
                    
                #print('\n')
        
        previous_mesh_info.update(mesh_changes)
        
        # Track object location changes
        current_location = obj.location
        if current_location != previous_location:
            
                
            print(f"Object {obj.name} location changed from{previous_location} to: {current_location}")
            
            # Calculate translation instead
            
        
            previous_location = copy.copy(current_location)
            locationchange= (True , {last_operator}) 
        # Log changes or properties of the mesh
        #This next line has been commented out to prevent filling up myy logs
        # print(f"Mesh changes - Vertices: {vertices_count}, Edges: {edges_count}, Faces: {faces_count}")
        
        
        # Rotation
        current_rotation = obj.rotation_euler
        
        # Extract rotations around X, Y, and Z axes (in radians)
        rotation_x = current_rotation.x
        rotation_y = current_rotation.y
        rotation_z = current_rotation.z
        
        current_rotation= (rotation_x , rotation_y , rotation_z )
        if current_rotation != previous_rotation:    
            print(f"Object {obj.name} rotation changed from {previous_rotation} to: {current_rotation}")
            previous_rotation = copy.copy(current_rotation)
            rotationchange= (True , {last_operator}) 
            
        #Scale   
        current_scale = obj.scale
        if current_scale != previous_scale:        
            print(f"Object {obj.name} location changed from{previous_location} to: {current_location}")
            previous_scale = copy.copy(current_scale)
            
    
            
def get_mat_command(current_mat, initial_mat):
    obj = bpy.context.active_object 
  
    
  
    
   
    #get the loop count to avoid checking past the material slots
    #this code will have to be done when applying
    min_length = min(len(current_mat), len(initial_mat))
   
    
    zipped_lists = zip_longest(current_mat, initial_mat, fillvalue=None)

    
    #get the material slot that changed
    global slot_ids
    slot_ids = {}
    for i, (current_val, initial_val) in enumerate(zipped_lists):
        if current_val != initial_val:
            slot_ids[i] = (current_val, initial_val)
            global mat_change
            mat_change= True
            
    print(f"slots {slot_ids}")
    

def apply_mat_command(slot_ids):
    
    global mat_change
    print(f"Slots id  {slot_ids}")
    
    if mat_change:
   
        command = ""
        for slot_id, (current_material, initial_material) in slot_ids.items():
            print(f"Current material {current_material}")
            #if the change wwe made was to remove all material slots
            if current_material == None:
                command+=(
                f"bpy.context.object.active_material_index={slot_id}\n"
                f"bpy.ops.object.material_slot_remove()")
                
            else:
                if slot_id < len(bpy.context.object.material_slots):
                    command += (
                        f"bpy.context.object.material_slots[{slot_id}].material = bpy.data.materials['{current_material.name}']\n"
                    )
                else:
                    command += (
                        f"bpy.ops.object.material_slot_add()\n"
                        f"bpy.context.object.material_slots[-1].material = bpy.data.materials['{current_material.name}']\n"
                    )
            
       
        
        global steps
        steps.append(command)
        
def get_mod_props():
    mod_props = {}  # Assuming mod_props is a dictionary declared somewhere

    obj = bpy.context.active_object

    for modifier in bpy.context.object.modifiers:
        print("Modifier Name:", modifier.name)
        allprops = dir(bpy.context.object.modifiers[modifier.name])
        moddict = {}

        for prop in allprops:
            value = getattr(obj.modifiers[modifier.name], prop, None)
            print(prop, value)
            moddict[prop] = value

        mod_props[modifier.name] = moddict
        print('-----------------------------------')

    print(f'Modprops dict {mod_props}')
    return mod_props



def compare_dicts(a, b):
    
    global steps

    for key in b.keys():
      print (f"Modifier {key}")
      if key not in a :
        print(f"Modifier {key} has been added")
        
        #get the command to apply the key with all its subvalues
        mod=bpy.context.object.modifiers[key].type
        
    
       
        command=(f"bpy.ops.object.modifier_add(type='{mod}')")
        steps.append(command)
        for prop in (b[key]).keys():
            if prop not in ["__doc__","name", "rna_type","type", "is_override_data", "__module__", "__slots__", "bl_rna", "damping_time", "execution_time"]:
                value_str = f"'{b[key][prop]}'" if isinstance(b[key][prop], str) else b[key][prop]
                command = f"bpy.context.object.modifiers['{key}'].{prop} = {value_str}"
                steps.append(command)

        
      



        if key in a:
          print (b[key])
          
          for prop in (b[key]).keys():
            
            if b[key][prop] != a[key][prop]:
              print(f"Modifier {key} value {prop} changed from {a[key][prop]} to {b[key][prop]}")



        #check if a modifier has been removed
    for key in a .keys():  
        if key not in b:
            print(f"Modifier {key} has been removed")
    
            command = f"bpy.ops.object.modifier_remove(modifier='{key}')"
            steps.append(command)


    
    

class StartOperator(bpy.types.Operator):
    bl_idname = "myaddon.start"
    bl_label = "Start Recording"
    
    recording = bpy.props.BoolProperty(default=False)
    
    def execute(self, context):
        context.scene.myaddon_start.recording = True 
        global steps
        
        # Clear the steps list before starting a new recording
        steps.clear()
        
        global starting_location
        get_starting_loc()
        get_starting_rotation()
        get_starting_scale()
        
        
        # Register the handler to monitor changes
        bpy.app.handlers.depsgraph_update_post.append(log_mesh_changes)
        
        # Register the material changes
        global initial_mat
        obj = bpy.context.active_object
    
        if obj and obj.type == 'MESH':
            initial_mat=obj.data.materials[:]
            print (initial_mat)
            global initial_mods
            initial_mods=get_mod_props()
        

        
        
        print("Recording changes started.... ")
        return {'FINISHED'}
    
class StopOperator(bpy.types.Operator):
    bl_idname = "myaddon.stop"
    bl_label = "Stop"
    
    
    
    def execute(self, context):
        
        context.scene.myaddon_start.recording = False
        
        global translation
        global steps
        global starting_rotation
        global starting_scale
        
        print("Custom stop operator executed!")
        
        obj = bpy.context.active_object
    
        if obj and obj.type == 'MESH':
            print('obj is mesh')
            
            global starting_location
           
        
            if translation:
                print(f' sl {starting_location} , {obj.location}')
                get_pos_transform (starting_location[0], obj.location)
                
        #update rotation steps
        
            current_rotation = obj.rotation_euler
        
            # Extract rotations around X, Y, and Z axes (in radians)
            rotation_x = current_rotation.x
            rotation_y = current_rotation.y
            rotation_z = current_rotation.z
            
            current_rotation =(rotation_x , rotation_y , rotation_z)
        
            if current_rotation != starting_rotation:
                
                print(f' sr {starting_rotation } , {current_rotation}')
                rotation_command (starting_rotation, current_rotation)
                
            #scale
            current_scale=obj.scale
            if current_scale != starting_scale:
                
                print(f' ssc {starting_scale } , {current_scale}')
                get_scale_factor (starting_scale, current_scale)
                
                
                
                
            #check if material changed
            current_mat=obj.data.materials[:]
            if current_mat != initial_mat:
                get_mat_command(current_mat, initial_mat)
                
                
            #check if modifiers have changed
            global initial_mods
            current_mods=get_mod_props()
            if current_mods == initial_mods:
                print (f"MODS STAYED THE SAME")
            else:
                compare_dicts(initial_mods, current_mods)
                
        
        
        
                
        for step in steps:        
            print(f" STEPS {step} \n")
            
        return {'FINISHED'}
    
class ApplyOperator(bpy.types.Operator):
    bl_idname = "myaddon.apply"
    bl_label = "Apply"
    
    def execute(self, context):
        
        print("Custom apply operator executed!")
       
        global steps
        
        apply_mat_command(slot_ids)
        
        for command in steps:
            # Evaluate and execute each command as a Blender Python function
            print (f"\n evaluating {command}")
            exec(command)
            
       
        
        return {'FINISHED'}
    
class ExportOperator(bpy.types.Operator):
    bl_idname = "myaddon.export"
    bl_label = "Export"
    
    def execute(self, context):
        global steps
       
        filepath = "saved_steps.py" 
        
        # Open the file in write mode
        with open(filepath, "w") as file:
            # Write each step from the 'steps' variable to the file
            for step in steps:
                file.write(step + "\n")  # Write each step followed by a newline
        print("Custom export operator executed!")
        return {'FINISHED'}

class StepsTracker(bpy.types.Panel):
    """Creates a Panel in the scene context of the View3d editor"""
    bl_label = "Steps Tracker"
    bl_idname = "STEP5_PT_layout"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Steps Tracker"
    
    

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        # Create a simple row.
        layout.label(text=" Hit Track to Start tracking your steps")


        # Big render button
       
        row = layout.row()
        row.scale_y = 1.5
        row.operator("myaddon.start")

        # Different sizes in a row
        layout.label(text="Next")
        row = layout.row(align=True)
        row.operator("myaddon.stop")

        sub = row.row()
        sub.scale_x = 2.0
        sub.operator("myaddon.apply")

        row.operator("myaddon.export")


def register():
    bpy.utils.register_class(StartOperator) 
    bpy.utils.register_class(StopOperator)
    bpy.utils.register_class(ApplyOperator)
    bpy.utils.register_class(ExportOperator)
    bpy.utils.register_class(StepsTracker)


def unregister():
    bpy.utils.unregister_class(StartOperator)
    bpy.utils.unregister_class(StopOperator)
    bpy.utils.unregister_class(ApplyOperator)
    bpy.utils.unregister_class(ExportOperator)
    bpy.utils.unregister_class(StepsTracker)


if __name__ == "__main__":
   
    register()
