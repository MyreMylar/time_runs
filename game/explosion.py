import random
import pygame

from game.damage import Damage


class Explosion(pygame.sprite.Sprite):
    def __init__(self, start_pos, explosion_sheet, size, damage_amount, damage_type, *groups):

        super().__init__(*groups)
        self.radius = size
        self.collide_radius = self.radius
        self.explosion_sheet = explosion_sheet
        self.explosion_frames = 16
        self.explosion_images = []
        random_explosion_int = random.randrange(0, 512, 64)
        for i in range(0, self.explosion_frames):
            x_start_index = (i * 64)
            explosion_frame = self.explosion_sheet.subsurface(pygame.Rect(x_start_index + 1,
                                                                          random_explosion_int + 1, 62, 62))
            explosion_frame = pygame.transform.scale(explosion_frame, (self.radius*2, self.radius*2))
            self.explosion_images.append(explosion_frame)

        self.image = self.explosion_images[0]
                
        self.rect = self.explosion_images[0].get_rect()
        self.rect.center = start_pos

        self.position = [float(self.rect.center[0]), float(self.rect.center[1])]
        self.world_position = [float(self.rect.center[0]), float(self.rect.center[1])]
        
        self.should_die = False
        self.life_time = 0.45
        self.time = self.life_time
        self.frameTime = self.life_time / self.explosion_frames
        self.frame = 1

        self.damage = Damage(damage_amount, damage_type)
        
    def update_sprite(self, all_explosion_sprites, time_delta, time_multiplier, tiled_level):
       
        self.position[0] = self.world_position[0] - tiled_level.position_offset[0]
        self.position[1] = self.world_position[1] - tiled_level.position_offset[1]
        self.rect.center = self.position
        
        self.time -= time_delta * time_multiplier
        if self.time < 0.0:
            self.should_die = True

        if self.frame < self.explosion_frames and (self.life_time - self.time) > (self.frameTime * self.frame):
            self.image = self.explosion_images[self.frame]
            self.frame += 1

        all_explosion_sprites.add(self)
            
        return all_explosion_sprites

    def update_movement_and_collision(self):
        pass
