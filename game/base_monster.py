import math
import random
import pygame

from game.bullet import Bullet
from game.missile import Missile


class LOSLine:
    def __init__(self, start_pos, end_pos):
        self.start_pos = [start_pos[0], start_pos[1]]
        self.end_pos = [end_pos[0], end_pos[1]]
        self.line_list = self.create_line_list(int(self.start_pos[0]),
                                               int(self.start_pos[1]),
                                               int(self.end_pos[0]),
                                               int(self.end_pos[1]))
        
    @staticmethod
    def create_line_list(x0, y0, x1, y1):
        line = []
        dx = abs(x1 - x0)    # distance to travel in X
        dy = abs(y1 - y0)    # distance to travel in Y

        if x0 < x1:
            ix = 1           # x will increase at each step
        else:
            ix = -1          # x will decrease at each step

        if y0 < y1:
            iy = 1           # y will increase at each step
        else:
            iy = -1          # y will decrease at each step

        e = 0                # Current error 

        for i in range(dx + dy):
            line.append((x0, y0))
            e1 = e + dy
            e2 = e - dx
            if abs(e1) < abs(e2):
                # Error will be smaller moving on X
                x0 += ix
                e = e1
            else:
                # Error will be smaller moving on Y
                y0 += iy
                e = e2

        return line

    def is_rect_collided(self, rect):
        collided = False
        for point in self.line_list:
            if rect.collidepoint(point):
                collided = True
                break
            
        return collided
        

class MonsterPath:
    def __init__(self):
        self.start_waypoint = [0, 0]
        self.waypoints = []
        self.waypoint_radius = 32


class BaseMonster(pygame.sprite.Sprite):
    def __init__(self, type_id, start_pos, sprite_map, all_monster_sprites, play_area, tiled_level,
                 explosions_sprite_sheet, *groups):
        super().__init__(*groups)
        self.id = type_id
        self.start_pos = start_pos
        self.play_area = play_area
        self.tiled_level = tiled_level

        self.explosions_sprite_sheet = explosions_sprite_sheet
        self.attack_time_delay = 0.5
        self.original_image = sprite_map[1][0]
        if self.id == "rifle":
            self.original_image = sprite_map[1][0]
            self.attack_time_delay = 0.5
        elif self.id == "shotgun":
            self.original_image = sprite_map[1][1]
            self.attack_time_delay = 0.8
        elif self.id == "launcher":
            self.original_image = sprite_map[1][2]
            self.attack_time_delay = 5.0
            
        self.image = self.original_image.copy()
        self.flash_sprite = pygame.sprite.Sprite()
        self.test_collision_sprite = pygame.sprite.Sprite()

        self.sprite_rot_centre_offset = [0.0, 0.0]
                       
        self.rect = self.image.get_rect()

        self.rect.center = self.start_pos

        self.position = [float(self.rect.center[0]), float(self.rect.center[1])]

        self.screen_position = [0, 0]
        self.screen_position[0] = self.position[0]
        self.screen_position[1] = self.position[1]
        self.old_facing_angle = 0

        self.update_screen_position(self.tiled_level.position_offset)

        self.change_direction_time = 5.0
        self.change_direction_accumulator = 0.0
      
        self.next_way_point = self.get_random_point_in_radius_of_point([500, 400], 96)

        x_dist = float(self.next_way_point[0]) - float(self.position[0])
        y_dist = float(self.next_way_point[1]) - float(self.position[1])
        self.distance_to_next_way_point = math.sqrt((x_dist ** 2) + (y_dist ** 2))
        self.current_vector = [x_dist / self.distance_to_next_way_point, y_dist / self.distance_to_next_way_point]

        self.rotate_sprite()
    
        self.should_die = False
        
        self.sprite_needs_update = True
        self.all_monster_sprites = all_monster_sprites
        self.all_monster_sprites.add(self)

        self.health = 100
        self.move_speed = 0

        self.slow_down_percentage = 1.0
        self.collide_radius = 20

        self.is_wandering_aimlessly = True
        self.random_target_change_time = random.uniform(3.0, 15.0)
        self.random_target_change_acc = 0.0

        self.time_to_home_in_on_player = False
        self.monster_home_on_target_time = random.uniform(0.3, 1.5)
        self.monster_home_on_target_acc = 0.0

        self.is_time_to_start_attack = True
        self.attack_time_acc = 0.0

        self.is_attacking = False
        self.should_do_attack_damage = False
        self.attack_anim_acc = 0.0
        self.attack_anim_total_time = 0.8

        self.per_bullet_damage = 15

        self.barrel_exit_pos = [0.0, 0.0]
        self.barrel_forward_offset = 32
        self.barrel_side_offset = 6

        self.sprite_flash_acc = 0.0
        self.sprite_flash_time = 0.15
        self.should_flash_sprite = False
        self.active_flash_sprite = False

        self.line_of_sight = None
        self.los_check_timer = 0.6
        self.los_check_acc = 0.4

        self.has_line_of_sight_to_player = False

    def update_sprite(self, time_delta, time_multiplier):
        if self.sprite_needs_update:
            self.sprite_needs_update = False

        if self.should_flash_sprite and not self.should_die:
            self.sprite_flash_acc += time_delta * time_multiplier
            if self.sprite_flash_acc > self.sprite_flash_time:
                self.sprite_flash_acc = 0.0
                self.should_flash_sprite = False
                
            else:
                lerp_value = self.sprite_flash_acc / self.sprite_flash_time
                flash_alpha = self.lerp(255, 0, lerp_value)
                flash_image = self.image.copy()
                flash_image.fill((0, 0, 0, flash_alpha), None, pygame.BLEND_RGBA_MULT)
                flash_image.fill((255, 255, 255, 0), None, pygame.BLEND_RGBA_ADD)
                self.flash_sprite.image = flash_image
                self.flash_sprite.rect = self.flash_sprite.image.get_rect()
                flash_sprite_x_pos = self.screen_position[0]
                flash_sprite_y_pos = self.screen_position[1] + self.sprite_rot_centre_offset[1]
                self.flash_sprite.rect.center = self.rot_point([flash_sprite_x_pos, flash_sprite_y_pos],
                                                               self.screen_position, -self.old_facing_angle)
                if not self.active_flash_sprite:
                    self.all_monster_sprites.add(self.flash_sprite)
                    self.active_flash_sprite = True

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0
        self.should_flash_sprite = True

    def update_movement_and_collision(self, time_delta, time_multiplier, player,
                                      new_explosions, tiled_level, projectiles, pick_up_spawner):

        for explosion in new_explosions:
            if self.test_explosion_collision(explosion):
                self.take_damage(explosion.damage.amount)
        if self.health <= 0:
            self.should_die = True

        distance_to_player = 100000000.0
        if not player.should_die:
            x_dist = float(player.position[0]) - float(self.position[0])
            y_dist = float(player.position[1]) - float(self.position[1])
            distance_to_player = math.sqrt((x_dist * x_dist) + (y_dist * y_dist))

        # idle AI state
            if self.is_wandering_aimlessly:
                # self.moveSpeed = self.idleMoveSpeed
                if distance_to_player < 512.0:
                    self.is_wandering_aimlessly = False
                elif self.random_target_change_acc < self.random_target_change_time:
                    self.random_target_change_acc += time_delta
                else:
                    self.random_target_change_acc = 0.0
                    self.random_target_change_time = random.uniform(3.0, 15.0)

                    self.next_way_point = self.get_random_point_on_screen()

                    x_dist = float(self.next_way_point[0]) - float(self.position[0])
                    y_dist = float(self.next_way_point[1]) - float(self.position[1])
                    # self.distance_to_next_way_point = math.sqrt((x_dist * x_dist) + (yDist * yDist))
                    self.current_vector = [x_dist / self.distance_to_next_way_point,
                                           y_dist / self.distance_to_next_way_point]

                    self.rotate_sprite()

        # preparing to shoot AI state
            if not self.is_wandering_aimlessly:
                if distance_to_player > 700.0:
                    self.is_wandering_aimlessly = True

                if distance_to_player > 0.0:
                    self.current_vector = [x_dist / distance_to_player,
                                           y_dist / distance_to_player]

                self.rotate_sprite()

                if self.attack_time_acc < self.attack_time_delay:
                    self.attack_time_acc += time_delta * time_multiplier
                else:
                    self.attack_time_acc = random.random() / 10.0  # add a small random amount to the reload delay
                    self.is_time_to_start_attack = True

                if self.is_time_to_start_attack and self.has_line_of_sight_to_player:
                    self.is_time_to_start_attack = False
                    self.is_attacking = True
                    if self.id == "rifle":
                        x_forward_offset = self.current_vector[0] * self.barrel_forward_offset
                        x_side_offset = self.current_vector[1] * self.barrel_side_offset
                        y_forward_offset = self.current_vector[1] * self.barrel_forward_offset
                        y_side_offset = self.current_vector[0] * self.barrel_side_offset
                        barrel_x_pos = self.position[0] + x_forward_offset - x_side_offset
                        barrel_y_pos = self.position[1] + y_forward_offset + y_side_offset
                        self.barrel_exit_pos = [barrel_x_pos, barrel_y_pos]
                        projectiles.append(Bullet(self.barrel_exit_pos, self.current_vector, self.per_bullet_damage,
                                                  self.explosions_sprite_sheet, True))
                    elif self.id == "shotgun":
                        barrel_forward_offset = 32
                        barrel_side_offset1 = 4
                        barrel_side_offset2 = 8

                        x_forward_offset = self.current_vector[0] * barrel_forward_offset
                        y_forward_offset = self.current_vector[1] * barrel_forward_offset
                        x_side_offset1 = self.current_vector[1] * barrel_side_offset1
                        y_side_offset1 = self.current_vector[0] * barrel_side_offset1
                        x_side_offset2 = self.current_vector[1] * barrel_side_offset2
                        y_side_offset2 = self.current_vector[0] * barrel_side_offset2

                        barrel1_x_pos = self.position[0] + x_forward_offset - x_side_offset1
                        barrel1_y_pos = self.position[1] + y_forward_offset + y_side_offset1
                        barrel1_exit_pos = [barrel1_x_pos, barrel1_y_pos]

                        barrel2_x_pos = self.position[0] + x_forward_offset - x_side_offset2
                        barrel2_y_pos = self.position[1] + y_forward_offset + y_side_offset2
                        barrel2_exit_pos = [barrel2_x_pos, barrel2_y_pos]

                        projectiles.append(Bullet(barrel1_exit_pos, self.current_vector, self.per_bullet_damage,
                                                  self.explosions_sprite_sheet, True))
                        projectiles.append(Bullet(barrel2_exit_pos, self.current_vector, self.per_bullet_damage,
                                                  self.explosions_sprite_sheet, True))
                    elif self.id == "launcher":
                        barrel_forward_offset = 28
                        barrel_side_offset = 11
                        missile_damage = 100
                        barrel_x_forward_vector = self.current_vector[0] * barrel_forward_offset
                        barrel_x_side_vector = self.current_vector[1] * barrel_side_offset
                        barrel_y_forward_vector = self.current_vector[1] * barrel_forward_offset
                        barrel_y_side_vector = self.current_vector[0] * barrel_side_offset
                        barrel_x_pos = self.position[0] + barrel_x_forward_vector - barrel_x_side_vector
                        barrel_y_pos = self.position[1] + barrel_y_forward_vector + barrel_y_side_vector
                        barrel_exit_pos = [barrel_x_pos, barrel_y_pos]
                        projectiles.append(Missile(barrel_exit_pos, self.current_vector,
                                                   missile_damage, self.explosions_sprite_sheet, True))

        # shooting/reloading
        if self.is_attacking:
            self.attack_anim_acc += time_delta * time_multiplier
            if self.attack_anim_acc > self.attack_anim_total_time:
                self.attack_anim_acc = 0.0
                self.is_attacking = False
            
        # time to check LOS to player?
        if self.los_check_acc >= self.los_check_timer:
            self.los_check_acc = 0.0
            self.has_line_of_sight_to_player = True
            if not player.should_die:
                if distance_to_player < 550.0:
                    self.line_of_sight = LOSLine(self.screen_position, player.screen_position)
                    for tile_x in range(tiled_level.zero_tile_x, tiled_level.end_tile_x):
                        if self.has_line_of_sight_to_player:
                            for tile_y in range(tiled_level.zero_tile_y, tiled_level.end_tile_y):
                                tile = tiled_level.tile_grid[tile_x][tile_y]
                                if self.has_line_of_sight_to_player:
                                    for collision_shape in tile.tile_data.collision_shapes:
                                        if collision_shape[0] == "circle":
                                            pass
                                        elif collision_shape[0] == "rect":
                                            rect = collision_shape[2]
                                            if self.line_of_sight.is_rect_collided(rect):
                                                self.has_line_of_sight_to_player = False
                                else:
                                    break
                        else:
                            break
                else:
                    self.line_of_sight = None
                    self.has_line_of_sight_to_player = False
        else:
            self.los_check_acc += time_delta * time_multiplier

        self.update_screen_position(self.tiled_level.position_offset)
        self.rect.center = self.screen_position

        if self.should_die:
            self.all_monster_sprites.remove(self)
            if self.active_flash_sprite:
                self.all_monster_sprites.remove(self.flash_sprite)
                self.active_flash_sprite = False
            self.try_pick_up_spawn(pick_up_spawner)

    def update_screen_position(self, world_offset):
        self.screen_position[0] = self.position[0] - world_offset[0]
        self.screen_position[1] = self.position[1] - world_offset[1]
            
    @staticmethod
    def get_random_point_in_radius_of_point(point, radius):
        t = 2*math.pi*random.random()
        u = random.random() + random.random()
        if u > 1:
            r = 2-u
        else:
            r = u
        return [point[0] + radius*r*math.cos(t), point[1] + radius*r*math.sin(t)]

    @staticmethod
    def test_point_in_explosion(point, explosion):
        return (point[0] - explosion.position[0])**2 + (point[1] - explosion.position[1])**2 < explosion.radius**2

    def test_projectile_collision(self, projectile_rect):
        collided = False
        if self.rect.colliderect(projectile_rect):
            if (self.test_point_in_circle(projectile_rect.topleft,
                                          self.screen_position,
                                          self.collide_radius)) or\
                    (self.test_point_in_circle(projectile_rect.topright,
                                               self.screen_position,
                                               self.collide_radius)) or\
                    (self.test_point_in_circle(projectile_rect.bottomleft,
                                               self.screen_position,
                                               self.collide_radius)) or\
                    (self.test_point_in_circle(projectile_rect.bottomright,
                                               self.screen_position,
                                               self.collide_radius)):
                collided = True
        return collided

    @staticmethod
    def test_point_in_circle(point, circle_pos, circle_radius):
        return (point[0] - circle_pos[0]) ** 2 + (point[1] - circle_pos[1]) ** 2 < circle_radius ** 2
    
    def test_monster_collision(self, temp_player_rect, monster):
        collided = False
        if temp_player_rect.colliderect(monster.sprite.rect):
            collided = self.is_intersecting(monster)
        return collided
    
    def test_tile_collision(self, temp_player_rect, tile):
        collided = False
        if temp_player_rect.colliderect(tile.sprite.rect):
            collided = self.is_intersecting_tile(tile)
        return collided

    # tiles positions are in screen space currently
    def is_intersecting_tile(self, c2):
        x_dist = (self.screen_position[0] - c2.position[0]) ** 2
        y_dist = (self.screen_position[1] - c2.position[1]) ** 2
        distance = math.sqrt(x_dist + y_dist)
        if abs((self.collide_radius - c2.collide_radius)) <= distance <= (self.collide_radius + c2.collide_radius):
            return True
        else:
            return False

    def is_intersecting(self, c2):
        distance = math.sqrt((self.position[0] - c2.position[0]) ** 2 + (self.position[1] - c2.position[1]) ** 2)
        if abs((self.collide_radius - c2.collide_radius)) <= distance <= (self.collide_radius + c2.collide_radius):
            return True
        else:
            return False

    def test_explosion_collision(self, explosion):
        collided = False
        if self.rect.colliderect(explosion.rect):
            collided = self.is_explosion_intersecting(explosion) or self.is_circle_inside(explosion)
        return collided
    
    def is_explosion_intersecting(self, c2):
        x_dist = (self.screen_position[0] - c2.position[0]) ** 2
        y_dist = (self.screen_position[1] - c2.position[1]) ** 2
        distance = math.sqrt(x_dist + y_dist)
        if abs((self.collide_radius - c2.collide_radius)) <= distance <= (self.collide_radius + c2.collide_radius):
            return True
        else:
            return False

    def is_circle_inside(self, c2):
        x_dist = (self.screen_position[0] - c2.position[0]) ** 2
        y_dist = (self.screen_position[1] - c2.position[1]) ** 2
        distance = math.sqrt(x_dist + y_dist)
        if self.collide_radius < c2.collide_radius:
            is_inside = distance + self.collide_radius <= c2.collide_radius
        else:
            is_inside = distance + c2.collide_radius <= self.collide_radius
        return is_inside

    def set_average_speed(self, average_speed):
        self.move_speed = random.randint(int(average_speed * 0.75), int(average_speed * 1.25))
        return self.move_speed

    def get_random_point_on_screen(self):
        random_x = random.randint(32, self.play_area[0] - 32)
        random_y = random.randint(32, self.play_area[1] - 32)
        return [random_x, random_y]

    def rotate_sprite(self):
        direction_magnitude = math.sqrt(self.current_vector[0] ** 2 + self.current_vector[1] ** 2)
        if direction_magnitude > 0.0:
            unit_dir_vector = [self.current_vector[0] / direction_magnitude,
                               self.current_vector[1] / direction_magnitude]
            self.old_facing_angle = math.atan2(-unit_dir_vector[0], -unit_dir_vector[1]) * 180 / math.pi
            monster_centre_position = self.rect.center
            self.image = pygame.transform.rotate(self.original_image, self.old_facing_angle)
            self.rect = self.image.get_rect()
            self.rect.center = monster_centre_position

    def try_pick_up_spawn(self, pickup_spawner):
        pickup_spawner.try_spawn(self.position)

    @staticmethod
    def rot_point(point, axis, ang):
        """ Orbit. calcs the new loc for a point that rotates a given num of degrees around an axis point,
        +clockwise, -anticlockwise -> tuple x,y
        """
        ang -= 90
        x, y = point[0] - axis[0], point[1] - axis[1]
        radius = math.sqrt(x*x + y*y)  # get the distance between points

        r_ang = math.radians(ang)       # convert ang to radians.

        h = axis[0] + (radius * math.cos(r_ang))
        v = axis[1] + (radius * math.sin(r_ang))

        return [h, v]

    @staticmethod
    def lerp(a, b, c):
        return (c * b) + ((1.0 - c) * a)
