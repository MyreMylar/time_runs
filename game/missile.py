import math
import pygame

from game.projectile import Projectile
from game.explosion import Explosion
from game.damage import DamageType


class Missile(Projectile):
    def __init__(self, start_pos, initial_heading_vector, damage, explosions_sprite_sheet, is_ai_bullet=False):
        super().__init__()
        self.is_ai_bullet = is_ai_bullet
        self.explosions_sprite_sheet = explosions_sprite_sheet
        self.image_name = "images/missile.png"
        self.original_image = pygame.image.load(self.image_name).convert_alpha()
        self.image = self.original_image.copy()
        self.sprite = pygame.sprite.Sprite()
       
        self.sprite.rect = self.image.get_rect()
        self.world_rect = self.sprite.rect.copy()
        self.sprite.rect.center = start_pos

        self.current_vector = [initial_heading_vector[0], initial_heading_vector[1]]

        self.position = [float(self.sprite.rect.center[0]), float(self.sprite.rect.center[1])]
        self.world_position = [float(self.sprite.rect.center[0]), float(self.sprite.rect.center[1])]
        self.sprite.image = self.image

        self.should_die = False

        self.bullet_speed = 225.0
        self.damage = damage

        self.shot_range = 1024

        self.timeToHomeIn = False
        self.homingTimeAcc = 0.0
        self.homingTime = 0.2
        self.homingRadius = 256

    def update_sprite(self, all_bullet_sprites):
        self.sprite.image = self.image
        all_bullet_sprites.add(self.sprite)
        return all_bullet_sprites

    def update_movement_and_collision(self, tiled_level, collideable_tiles, players, monsters,
                                      time_delta, time_multiplier, new_explosions, explosions):
        if self.is_ai_bullet:
            for player in players:
                if player.test_projectile_collision(self.sprite.rect):
                    self.should_die = True
        else:
            for monster in monsters:
                if monster.test_projectile_collision(self.sprite.rect):
                    self.should_die = True

        for tile_x in range(tiled_level.zero_tile_x, tiled_level.end_tile_x):
            for tile_y in range(tiled_level.zero_tile_y, tiled_level.end_tile_y):
                tile = tiled_level.tile_grid[tile_x][tile_y]
                if tile.test_projectile_collision(self.sprite.rect):
                    self.should_die = True

        self.shot_range -= time_delta * time_multiplier * self.bullet_speed
        self.world_position[0] += (self.current_vector[0] * time_delta * time_multiplier * self.bullet_speed)
        self.world_position[1] += (self.current_vector[1] * time_delta * time_multiplier * self.bullet_speed)
        self.world_rect.center = self.world_position
        
        self.position[0] = self.world_position[0] - tiled_level.position_offset[0]
        self.position[1] = self.world_position[1] - tiled_level.position_offset[1]
        self.sprite.rect.center = self.position

        if self.shot_range <= 0.0:
            self.should_die = True

        # calc facing angle
        direction_magnitude = math.sqrt(self.current_vector[0] ** 2 + self.current_vector[1] ** 2)
        unit_dir_vector = [0, 0]
        if direction_magnitude > 0.0:
            unit_dir_vector = [self.current_vector[0] / direction_magnitude,
                               self.current_vector[1] / direction_magnitude]
        facing_angle = math.atan2(-unit_dir_vector[0], -unit_dir_vector[1])*180/math.pi

        bullet_centre_position = self.sprite.rect.center
        self.image = pygame.transform.rotate(self.original_image, facing_angle)
        self.sprite.rect = self.image.get_rect()
        self.sprite.rect.center = bullet_centre_position

        if self.should_die:
            new_explosion = Explosion(self.world_position, self.explosions_sprite_sheet,
                                      96, self.damage, DamageType.MISSILE)
            new_explosions.append(new_explosion)
            explosions.append(new_explosion)

    def get_closest_monster_in_radius(self, monsters):
        closest_monster_distance = 100000.0
        closest_monster_in_radius = None
        for monster in monsters:
            x_dist = self.position[0] - monster.position[0]
            y_dist = self.position[1] - monster.position[1]
            total_dist = math.sqrt((x_dist * x_dist) + (y_dist * y_dist))
            if total_dist < self.homingRadius:
                if total_dist < closest_monster_distance:
                    closest_monster_distance = total_dist
                    closest_monster_in_radius = monster
        return closest_monster_in_radius, closest_monster_distance

    def calculate_aiming_vector(self, target, distance):
        x_direction = target.position[0] - self.position[0]
        y_direction = target.position[1] - self.position[1]
        return [x_direction/distance, y_direction/distance]
