import bpy
from math import sin, cos, radians

# create planet
def create_body(name, radius, orbit_distance, color, orbit_speed, num_frames, origin=None):
    
    if origin is None:
        origin_location = (0, 0, 0)
    else:
        origin_location = bpy.data.objects[origin].location
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=(origin_location[0] + orbit_distance, origin_location[1], origin_location[2]))
    orbiting_body = bpy.context.active_object
    orbiting_body.name = name
    orbiting_body.data.materials.append(bpy.data.materials.new(name=name))
    orbiting_body.data.materials[0].diffuse_color = color
    
    bpy.ops.object.shade_smooth()

    if origin is not None:
        orbiting_body.parent = bpy.data.objects[origin]
    
    orbiting_body.location = (orbit_distance, 0, 0)
    orbiting_body.rotation_mode = 'XYZ'
    orbiting_body.keyframe_insert(data_path="location", frame=1)
    orbiting_body.keyframe_insert(data_path="rotation_euler", frame=1)

    for frame in range(1, num_frames):
        angle = radians(frame * orbit_speed)
        x = orbit_distance * cos(angle)
        y = orbit_distance * sin(angle)
        orbiting_body.location = (x, y, 0)
        orbiting_body.rotation_euler = (0, 0, angle)
        orbiting_body.keyframe_insert(data_path="location", index=-1, frame=frame+1)
        orbiting_body.keyframe_insert(data_path="rotation_euler", index=-1, frame=frame+1)

    angle = radians(num_frames * orbit_speed)
    x = orbit_distance * cos(angle)
    y = orbit_distance * sin(angle)
    orbiting_body.location = (x, y, 0)
    orbiting_body.rotation_euler = (0, 0, angle)
    orbiting_body.keyframe_insert(data_path="location", index=-1, frame=num_frames)
    orbiting_body.keyframe_insert(data_path="rotation_euler", index=-1, frame=num_frames)
    
# create ring
def create_ring(parent_name, major_radius, minor_radius, color):
    parent_object = bpy.data.objects[parent_name]
    bpy.ops.mesh.primitive_torus_add(location=(0, 0, 0), major_radius=major_radius, minor_radius=minor_radius)
    ring = bpy.context.active_object
    ring.name = parent_name + "_Ring"
    ring.data.materials.append(bpy.data.materials.new(name=parent_name + "_Ring"))
    ring.data.materials[0].diffuse_color = color
    ring.parent = parent_object
    
    bpy.ops.object.shade_smooth()
    
    ring.rotation_euler = (radians(10), radians(10), 0)

# delete objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# make scene dark
world = bpy.context.scene.world
world.use_nodes = True
bg_node = world.node_tree.nodes.get('Background')
if bg_node:
    bg_node.inputs[0].default_value = (0, 0, 0, 1)

SR = 69.5700 / 20
AU = 5

# create sun
bpy.ops.mesh.primitive_uv_sphere_add(radius=SR, location=(0, 0, 0))
sun = bpy.context.active_object
sun.name = "Sun"

bpy.ops.object.light_add(type='POINT', radius=35, location=(0, 0, 0))
sun_light = bpy.context.active_object
sun_light.data.energy = 9999
sun_light.data.shadow_soft_size = 35

# sun material
sun_material = bpy.data.materials.new(name="Sun_Material")
sun.data.materials.append(sun_material)
sun_material.use_nodes = True
nodes = sun_material.node_tree.nodes
nodes.clear()

# sun emission
emission_node = nodes.new(type='ShaderNodeEmission')
emission_node.inputs[0].default_value = (1, 0.8, 0.1, 1)
emission_node.inputs[1].default_value = 20
output_node = nodes.new(type='ShaderNodeOutputMaterial')
links = sun_material.node_tree.links
links.new(emission_node.outputs[0], output_node.inputs[0])

# create planets
create_body("Mercury", 0.2440, 
5, #(0.39 * AU + SR),
(0.5, 0.5, 0.5, 1), 5, 721, "Sun")

create_body("Venus", 0.6052, 
8, #(0.72 * AU + SR),
(0.8, 0.4, 0.1, 1), 4, 721, "Sun")

create_body("Earth", 0.6371, 
10, #(AU + SR),
(0.1, 0.1, 1, 1), 3.5, 721, "Sun")

create_body("Mars", 0.3390, 
12, #(1.52 * AU + SR),
(1, 0.1, 0.1, 1), 3, 721, "Sun")

create_body("Jupiter", 6.9911/3, 
16, #(5.2 * AU + SR),
(0.8, 0.5, 0.2, 1), 2, 721, "Sun")

create_body("Saturn", 5.8232/3, 
21, #(9.54 * AU + SR)/2.5,
(0.9, 0.8, 0.6, 1), 1.5, 721, "Sun")

create_body("Uranus", 2.5362/3, 
25, #(19.2 * AU + SR)/4,
(0.6, 0.8, 0.9, 1), 1, 721, "Sun")

create_body("Neptune", 2.4622/3, 
28, #(30.06 * AU + SR)/5,
(0.1, 0.1, 0.9, 1), 0.5, 721, "Sun")

# create moon and rings
create_body("Moon", 0.2,
1,
(0.5, 0.5, 0.5, 1), 4, 721, "Earth")

create_ring("Saturn", major_radius=2.3, minor_radius=0.3, color=(0.3, 0.3, 0.3, 1))

# add camera
bpy.ops.object.camera_add(location=(-40, 40, 15), rotation=(radians(75), 0, radians(225)))
camera = bpy.context.active_object
bpy.context.scene.camera = camera

# rendering
bpy.context.scene.render.engine = 'BLENDER_EEVEE'
bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
bpy.context.scene.render.ffmpeg.format = 'MPEG4'
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 720