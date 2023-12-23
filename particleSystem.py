from ursina import *


class Particle(Entity):
    def __init__(self, position=(0, 0, 0), range=0.2, particleModel='cube', particleColor=color.red, particleScale=0.1,speed=6):
        super().__init__(
            model=particleModel,
            color=particleColor,
            range=range,
            position=position,
            scale=particleScale
        )
        self.speed = speed
        self.velocity = Vec3(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)) * 6

    def update(self):
        self.position += self.velocity * time.dt * self.speed
        self.scale += (time.dt * 0.5, time.dt * 0.5, time.dt * 0.5)
        if self.scale > self.range:
            destroy(self)