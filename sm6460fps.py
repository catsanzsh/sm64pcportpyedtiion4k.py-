# test.py
# Super Mario 64 - Python 3.13 Ursina Edition (600x400)

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

# --- Game Setup ---
app = Ursina(
    title='Super Mario 64 Python',
    borderless=False,
    fullscreen=False,
    size=(600, 400),
    vsync=True
)

# --- Player Definition ---
# We will create a custom player controller to emulate Mario's physics.
class MarioPlayer(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Player model and collider
        self.model = 'capsule'
        self.color = color.red
        self.collider = 'capsule'
        self.scale_y = 2

        # Player physics properties
        self.gravity = 1.0
        self.jump_height = 12
        self.jump_duration = 0.5
        self.jumping = False
        self.walk_speed = 8
        self.air_speed = 6
        self.air_time = 0
        self.grounded = False

        # Camera setup
        self.camera_pivot = Entity(parent=self, y=2)
        camera.parent = self.camera_pivot
        camera.position = (0, 5, -18)
        camera.rotation = (-15, 0, 0)
        mouse.locked = True

    def update(self):
        self.handle_movement()
        self.apply_gravity()
        self.handle_camera()

    def handle_camera(self):
        # Rotate player and camera based on mouse movement
        self.rotation_y += mouse.velocity[0] * 40
        self.camera_pivot.rotation_x -= mouse.velocity[1] * 40
        self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -45, 45)

    def handle_movement(self):
        direction = Vec3(
            self.forward * (held_keys['w'] - held_keys['s'])
            + self.right * (held_keys['d'] - held_keys['a'])
        ).normalized()

        speed = self.walk_speed if self.grounded else self.air_speed
        move_amount = direction * speed * time.dt
        
        # Raycast to prevent moving through walls
        if not self.intersects(ignore=[self,]).hit:
             self.position += move_amount

    def apply_gravity(self):
        # Check if grounded using a short raycast downwards
        ground_check = raycast(self.world_position, (0, -1, 0), ignore=[self,], distance=1.1)
        
        if ground_check.hit:
            if not self.grounded:
                self.y = ground_check.world_point.y + 1
                self.grounded = True
                self.air_time = 0
        else:
            self.grounded = False
            self.air_time += time.dt
            self.y -= (self.gravity + self.air_time) * 4 * time.dt

    def input(self, key):
        if key == 'space':
            self.jump()

    def jump(self):
        if self.grounded:
            self.grounded = False
            self.animate_y(self.y + self.jump_height, duration=self.jump_duration, curve=curve.out_expo)
            invoke(self.land, delay=self.jump_duration)

    def land(self):
        # This function is called after the jump animation finishes
        # Gravity will take over from here
        pass

# --- Level and Environment ---
def create_level():
    # Main ground
    ground = Entity(model='plane', scale=(100, 1, 100), color=color.rgb(100, 200, 50), texture='white_cube', texture_scale=(100, 100), collider='box')

    # Floating platforms
    platforms = [
        Entity(model='cube', scale=(10, 1, 10), position=(15, 5, 10), color=color.orange, texture='white_cube', texture_scale=(10,10), collider='box'),
        Entity(model='cube', scale=(5, 1, 15), position=(-10, 8, 5), color=color.azure, texture='white_cube', texture_scale=(5,15), collider='box'),
        Entity(model='cube', scale=(5, 1, 5), position=(0, 12, -15), color=color.pink, texture='white_cube', texture_scale=(5,5), collider='box')
    ]

    # Walls to keep the player in
    wall1 = Entity(model='cube', scale=(100, 10, 1), position=(0, 5, 50), collider='box', visible=False)
    wall2 = Entity(model='cube', scale=(100, 10, 1), position=(0, 5, -50), collider='box', visible=False)
    wall3 = Entity(model='cube', scale=(1, 10, 100), position=(50, 5, 0), collider='box', visible=False)
    wall4 = Entity(model='cube', scale=(1, 10, 100), position=(-50, 5, 0), collider='box', visible=False)

# --- Collectibles ---
class Star(Entity):
    def __init__(self, position=(0,0,0)):
        super().__init__(
            model='sphere', # A simple star model
            color=color.yellow,
            scale=1.5,
            position=position,
            collider='sphere',
            shader=lit_with_shadows_shader
        )
        self.collected = False

    def update(self):
        self.rotation_y += time.dt * 100 # Spin the star
        if self.intersects(player).hit and not self.collected:
            self.collected = True
            print_on_screen("You got a star!", position=(-0.2, 0.1), scale=2, duration=3)
            # This requires a sound file named 'coin.wav' or similar in the same folder
            try:
                Audio('coin', pitch=1, volume=0.5)
            except:
                print("Could not play sound. Make sure a sound file (e.g., 'coin.wav') is in the project folder.")
            self.fade_out(duration=0.5)
            destroy(self, delay=0.5)

# --- Initialization ---
# Skybox
Sky()

# Create the level geometry
create_level()

# Create the player instance
player = MarioPlayer(position=(0, 5, 0))

# Create a collectible star
star = Star(position=(0, 14, -15))

# --- Run Game ---
app.run()
