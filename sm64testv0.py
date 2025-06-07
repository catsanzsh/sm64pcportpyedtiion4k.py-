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
class MarioPlayer(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = 'capsule'
        self.color = color.red
        self.collider = 'capsule'
        self.scale_y = 2

        self.gravity = 1.0
        self.jump_height = 12
        self.jump_duration = 0.5
        self.jumping = False
        self.walk_speed = 8
        self.air_speed = 6
        self.air_time = 0
        self.grounded = False

        self.camera_pivot = Entity(parent=self, y=2)
        camera.parent = self.camera_pivot
        camera.position = (0, 0, -10)  # Adjusted camera position
        camera.rotation = (-10, 0, 0)  # Adjusted camera rotation
        mouse.locked = True

    def update(self):
        self.handle_movement()
        self.apply_gravity()
        self.handle_camera()

    def handle_camera(self):
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
        
        ray = raycast(self.world_position + Vec3(0, 0.5, 0), direction, ignore=[self,], distance=0.5)
        if not ray.hit:
            self.position += move_amount

    def apply_gravity(self):
        ground_check = raycast(self.world_position, Vec3(0, -1, 0), ignore=[self,], distance=1.1)
        
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
        if key == 'space' and self.grounded:
            self.jump()

    def jump(self):
        self.grounded = False
        self.animate_y(self.y + self.jump_height, duration=self.jump_duration, curve=curve.out_expo)
        invoke(self.land, delay=self.jump_duration)

    def land(self):
        pass

# --- Level and Environment ---
def create_level():
    ground = Entity(model='plane', scale=(100, 1, 100), color=color.rgb(100, 200, 50), texture='white_cube', texture_scale=(100, 100), collider='box')

    platforms = [
        Entity(model='cube', scale=(10, 1, 10), position=(15, 5, 10), color=color.orange, texture='white_cube', texture_scale=(10,10), collider='box'),
        Entity(model='cube', scale=(5, 1, 15), position=(-10, 8, 5), color=color.azure, texture='white_cube', texture_scale=(5,15), collider='box'),
        Entity(model='cube', scale=(5, 1, 5), position=(0, 12, -15), color=color.pink, texture='white_cube', texture_scale=(5,5), collider='box')
    ]

    wall1 = Entity(model='cube', scale=(100, 10, 1), position=(0, 5, 50), collider='box', visible=False)
    wall2 = Entity(model='cube', scale=(100, 10, 1), position=(0, 5, -50), collider='box', visible=False)
    wall3 = Entity(model='cube', scale=(1, 10, 100), position=(50, 5, 0), collider='box', visible=False)
    wall4 = Entity(model='cube', scale=(1, 10, 100), position=(-50, 5, 0), collider='box', visible=False)

# --- Collectibles ---
class Star(Entity):
    def __init__(self, position=(0,0,0)):
        super().__init__(
            model='sphere',
            color=color.yellow,
            scale=1.5,
            position=position,
            collider='sphere'
        )
        self.collected = False

    def update(self):
        self.rotation_y += time.dt * 100
        if self.intersects(player).hit and not self.collected:
            self.collected = True
            print_on_screen("You got a star!", position=(-0.2, 0.1), scale=2, duration=3)
            try:
                Audio('coin', pitch=1, volume=0.5)
            except:
                print("Could not play sound. Make sure a sound file (e.g., 'coin.wav') is in the project folder.")
            self.fade_out(duration=0.5)
            destroy(self, delay=0.5)

# --- Initialization ---
Sky()

create_level()

player = MarioPlayer(position=(0, 5, 0))

star = Star(position=(0, 14, -15))

# --- Run Game ---
app.run()
