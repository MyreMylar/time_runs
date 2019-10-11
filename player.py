import math
import pygame
from pygame.locals import *

from game.rifle_weapon import RifleWeapon
from game.shotgun_weapon import ShotgunWeapon
from game.launcher_weapon import LauncherWeapon


# -----------------------------------------------------------------------
# Use the Scheme class below to set the keys for controlling the player
# -----------------------------------------------------------------------
# - K_RIGHT, K_LEFT, K_UP and K_DOWN are the codes for the
#   arrow keys if you prefer those
# - These keys are used in challenge 2
#
# SCROLL DOWN TO LINE 140 FOR CHALLENGE 2!
# -----------------------------------------------------------------------
class Scheme:
    def __init__(self):
        self.rifle = K_1
        self.shotgun = K_2
        self.missile_launcher = K_3

        self.move_forwards = K_w
        self.move_backwards = K_s
        self.move_left = K_a
        self.move_right = K_d


class Player(pygame.sprite.Sprite):
    def __init__(self, start_pos, tiled_level, control_scheme, explosions_sprite_sheet, hud_buttons, *groups):

        super().__init__(*groups)
        self.scheme = control_scheme
        self.image_name = "images/player.png"
        self.explosions_sprite_sheet = explosions_sprite_sheet
        self.original_image = pygame.image.load(self.image_name).convert_alpha()
        self.sprite_sheet = self.original_image.copy()

        self.hud_buttons = hud_buttons

        self.rifle_weapon = RifleWeapon(self.sprite_sheet, self.explosions_sprite_sheet)
        self.shotgun_weapon = ShotgunWeapon(self.sprite_sheet, self.explosions_sprite_sheet)
        self.launcher_weapon = LauncherWeapon(self.sprite_sheet, self.explosions_sprite_sheet)
        self.active_weapon = self.rifle_weapon

        for button in self.hud_buttons:
            if button.button_image_name == "rifle_icon":
                button.set_selected()
            else:
                button.clear_selected()

        self.test_collision_sprite = pygame.sprite.Sprite()
        self.flash_sprite = pygame.sprite.Sprite()
        self.image = self.active_weapon.anim_set.stand
        self.rect = self.active_weapon.anim_set.stand.get_rect()
        self.rect.center = start_pos
        self.sprite_rot_centre_offset = [0.0, 11.0]

        self.acceleration = 200.0
        self.speed = 0.0
        self.max_speed = 250.0
        self.max_reverse_speed = -125.0
        self.strafe_speed = 0.0
        self.strafe_acceleration = 150.0
        self.max_strafe_speed = 200.0
        self.total_speed = 0.0
        self.rotate_speed = 0.5

        self.collide_radius = 18

        self.max_health = 100
        self.health = self.max_health
        self.should_die = False

        self.move_accumulator = 0.0

        self.position = [float(self.rect.center[0]), float(self.rect.center[1])]
        self.player_move_target = self.position
        self.distance_to_move_target = 0.0
        self.current_vector = [0.0, -1.0]
        self.new_facing_angle = 0

        self.screen_position = [0, 0]
        self.screen_position[0] = self.position[0]
        self.screen_position[1] = self.position[1]

        self.update_screen_position(tiled_level.position_offset)

        direction_magnitude = math.sqrt(self.current_vector[0] ** 2 + self.current_vector[1] ** 2)
        if direction_magnitude > 0.0:
            unit_dir_vector = [self.current_vector[0] / direction_magnitude,
                               self.current_vector[1] / direction_magnitude]
            self.new_facing_angle = math.atan2(-unit_dir_vector[0],
                                               -unit_dir_vector[1]) * 180 / math.pi

        self.old_facing_angle = self.new_facing_angle

        self.rect.center = self.rot_point([self.screen_position[0],
                                           self.screen_position[1] + self.sprite_rot_centre_offset[1]],
                                          self.screen_position, -self.new_facing_angle)

        self.left_mouse_held = False
        self.right_mouse_held = False

        self.move_forwards = False
        self.move_backwards = False
        self.move_left = False
        self.move_right = False

        self.per_bullet_damage = 25

        self.player_fire_target = [10000, 10000]

        self.switch_to_rifle = False
        self.switch_to_shotgun = False
        self.switch_to_missile_launcher = False

        self.sprite_flash_acc = 0.0
        self.sprite_flash_time = 0.15
        self.should_flash_sprite = False

        self.is_collided = False

        self.time_crystal_active = False
        self.time_crystal_acc = 0.0
        self.time_crystal_time = 4.0

        self.time_min_speed = 0.05
        self.time_max_speed = 1.0
        self.time_multiplier = self.calculate_time_multipliers()
        self.player_time_multiplier = self.time_multiplier

        self.should_draw_collision_obj = False
        self.collision_obj_rects = []
        self.collision_obj_rect = pygame.Rect(0.0, 0.0, 2.0, 2.0)

    # ------------------------------------------------------------------
    # Challenge 2
    # ----------------------------
    #
    # Make the player 'strafe' i.e. move left and right when the
    # appropriate keys are pressed.
    #
    # - To do this we need to handle the events generated when the
    #   move_left and move_right keys are pressed and released.
    #
    # - Look at how the move_forwards and move_backwards key events
    #   are being handled below. You will need to do the same for
    #   move_left and move_right. Don't forget to handle the KEYUP case
    #   or you will strafe forever.
    #
    # - you will use the variables:
    #       - self.scheme.move_left
    #       - self.scheme.move_right
    #       - self.move_left
    #       - self.move_right
    #
    # - If you want to change which keys control the player's movement
    #   the Scheme class used in process_event is at the top of this file.
    #
    # ----------------------------------------
    # SCROLL DOWN TO LINE 203 FOR CHALLENGE 3!
    # --------------------------------------------------------------------
    def process_event(self, event):

        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                self.left_mouse_held = True
            if event.button == 3:
                self.right_mouse_held = True

        if event.type == MOUSEBUTTONUP:
            if event.button == 1:
                self.left_mouse_held = False
            if event.button == 3:
                self.right_mouse_held = False

        if event.type == KEYDOWN:  # key pressed
            # movement key events
            if event.key == self.scheme.move_forwards:
                self.move_forwards = True
            if event.key == self.scheme.move_backwards:
                self.move_backwards = True

            # switch weapon key events
            if event.key == self.scheme.rifle:
                self.switch_to_rifle = True
            if event.key == self.scheme.shotgun:
                self.switch_to_shotgun = True
            if event.key == self.scheme.missile_launcher:
                self.switch_to_missile_launcher = True

        if event.type == KEYUP:  # key released
            # movement key events
            if event.key == self.scheme.move_forwards:
                self.move_forwards = False
            if event.key == self.scheme.move_backwards:
                self.move_backwards = False

    # -----------------------------------------------------------------------------------------------------
    # Challenge 3
    # ----------------------
    #
    # Make the 'time crystal' power-up slow time for your enemies, but not for your player. You can achieve
    # this by modifying the calculate_time_multipliers function below.
    #
    # TIPS
    # ------
    # - You can test if the time crystal is active with the Boolean variable; 'self.time_crystal_active'
    # - The player's time multiplier is self.player_time_multiplier, everyone else uses self.time_multiplier
    # - Time runs normally at a value of 1.0
    # - Make sure you still run the normal case, where everyone's time is linked to the player's run speed,
    #   when the time crystal is not active.
    #
    # - NOTE: Even the powers of the time crystal cannot help your bullets.
    # -----------------------------------------------------------------------------------------------------
    def calculate_time_multipliers(self):
        # calculate the speed of time based on the speed the player is moving.
        # Lerp is a goofy shorthand word for 'linear interpolation', which just means that we calculate a value between
        # a minimum and a maximum value based on the percentage. So 0% would just return the minimum, 100% would be the
        # maximum and 50% would be halfway between them.
        time_multiplier_lerp = min(1.0, abs(self.total_speed) / self.max_speed)  # percentage of maximum move speed
        self.time_multiplier = self.lerp(self.time_min_speed, self.time_max_speed, time_multiplier_lerp)

        self.player_time_multiplier = self.time_multiplier

        return self.time_multiplier

    def activate_time_crystal(self):
        self.time_crystal_active = True

    @staticmethod
    def get_world_position_from_screen_pos(screen_pos, world_offset):
        world_pos = [0, 0]
        world_pos[0] = screen_pos[0] + world_offset[0]
        world_pos[1] = screen_pos[1] + world_offset[1]

        return world_pos

    def update_screen_position(self, world_offset):
        self.screen_position[0] = self.position[0] - world_offset[0]
        self.screen_position[1] = self.position[1] - world_offset[1]

    def update_sprite(self, all_sprites, time_delta):
        all_sprites.add(self)

        if self.should_flash_sprite:
            self.sprite_flash_acc += time_delta
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
                sprite_x_pos = self.screen_position[0]
                sprite_y_pos = self.screen_position[1] + self.sprite_rot_centre_offset[1]
                self.flash_sprite.rect.center = self.rot_point([sprite_x_pos,
                                                                sprite_y_pos],
                                                               self.screen_position, -self.new_facing_angle)
                all_sprites.add(self.flash_sprite)
        return all_sprites

    def update_movement_and_collision(self, time_delta, projectiles, tiled_level, monsters, new_explosions):
        if self.time_crystal_active:
            self.time_crystal_acc += time_delta
            if self.time_crystal_acc >= self.time_crystal_time:
                self.time_crystal_acc = 0.0
                self.time_crystal_active = False

        for explosion in new_explosions:
            if self.test_explosion_collision(explosion):
                self.take_damage(explosion.damage.amount)

        if self.health == 0:
            self.should_die = True

        if self.switch_to_rifle:
            self.switch_to_rifle = False
            self.active_weapon = self.rifle_weapon

            for button in self.hud_buttons:
                if button.button_image_name == "rifle_icon":
                    button.set_selected()
                else:
                    button.clear_selected()

            self.image = pygame.transform.rotate(self.active_weapon.anim_set.stand, self.new_facing_angle)
            self.rect = self.image.get_rect()
            self.rect.center = self.rot_point([self.screen_position[0],
                                               self.screen_position[1] + self.sprite_rot_centre_offset[1]],
                                              self.screen_position, -self.new_facing_angle)

        if self.switch_to_shotgun:
            self.switch_to_shotgun = False
            self.active_weapon = self.shotgun_weapon

            for button in self.hud_buttons:
                if button.button_image_name == "shotgun_icon":
                    button.set_selected()
                else:
                    button.clear_selected()

            self.image = pygame.transform.rotate(self.active_weapon.anim_set.stand, self.new_facing_angle)
            self.rect = self.image.get_rect()
            self.rect.center = self.rot_point([self.screen_position[0],
                                               self.screen_position[1] + self.sprite_rot_centre_offset[1]],
                                              self.screen_position, -self.new_facing_angle)

        if self.switch_to_missile_launcher:
            self.switch_to_missile_launcher = False
            self.active_weapon = self.launcher_weapon

            for button in self.hud_buttons:
                if button.button_image_name == "launcher_icon":
                    button.set_selected()
                else:
                    button.clear_selected()

            self.image = pygame.transform.rotate(self.active_weapon.anim_set.stand, self.new_facing_angle)
            self.rect = self.image.get_rect()
            self.rect.center = self.rot_point([self.screen_position[0],
                                               self.screen_position[1] + self.sprite_rot_centre_offset[1]],
                                              self.screen_position, -self.new_facing_angle)

        fire_this_update = False

        if self.active_weapon.can_fire and (self.left_mouse_held or self.right_mouse_held):
            fire_this_update = True
            self.active_weapon.fire_rate_acc = 0.0
            self.active_weapon.can_fire = False

        self.active_weapon.update(time_delta, self.player_time_multiplier, self.position, self.current_vector)

        if fire_this_update:
            self.active_weapon.fire(projectiles)

        mouse_rel_move = pygame.mouse.get_rel()
        self.new_facing_angle = self.new_facing_angle - (mouse_rel_move[0] * self.rotate_speed)
        if self.new_facing_angle > 360:
            self.new_facing_angle = -360
        elif self.new_facing_angle < -360:
            self.new_facing_angle = 360
        self.current_vector = [-math.sin(self.new_facing_angle * math.pi / 180),
                               -math.cos(self.new_facing_angle * math.pi / 180)]

        if self.move_forwards or self.move_backwards or self.move_right or self.move_left:
            self.collision_obj_rects[:] = []
            if self.move_forwards:
                self.speed += self.acceleration * time_delta
                if self.speed > self.max_speed:
                    self.speed = self.max_speed

            elif self.move_backwards:
                self.speed -= self.acceleration * time_delta
                if self.speed < self.max_reverse_speed:
                    self.speed = self.max_reverse_speed

            if self.move_right:
                self.strafe_speed -= self.strafe_acceleration * time_delta
                if abs(self.strafe_speed) > self.max_strafe_speed:
                    self.strafe_speed = -self.max_strafe_speed

            elif self.move_left:
                self.strafe_speed += self.strafe_acceleration * time_delta
                if abs(self.strafe_speed) > self.max_strafe_speed:
                    self.strafe_speed = self.max_strafe_speed

            self.total_speed = math.sqrt(self.strafe_speed * self.strafe_speed + self.speed * self.speed)

            test_move_position = [0, 0]
            test_move_position[0] = self.position[0]
            test_move_position[1] = self.position[1]
            forward_x_movement = self.current_vector[0] * time_delta * self.speed
            sideways_x_movement = self.current_vector[1] * self.strafe_speed * time_delta
            forward_y_movement = self.current_vector[1] * time_delta * self.speed
            sideways_y_movement = self.current_vector[0] * self.strafe_speed * time_delta
            test_move_position[0] += forward_x_movement + sideways_x_movement
            test_move_position[1] += forward_y_movement - sideways_y_movement

            test_screen_position = [0, 0]
            test_screen_position[0] = test_move_position[0] - tiled_level.position_offset[0]
            test_screen_position[1] = test_move_position[1] - tiled_level.position_offset[1]

            self.test_collision_sprite.image = pygame.transform.rotate(self.original_image, self.new_facing_angle)
            self.test_collision_sprite.rect = self.image.get_rect()
            test_coll_sprite_x_pos = test_screen_position[0]
            test_coll_sprite_y_pos = test_screen_position[1] + self.sprite_rot_centre_offset[1]
            self.test_collision_sprite.rect.center = self.rot_point([test_coll_sprite_x_pos,
                                                                     test_coll_sprite_y_pos],
                                                                    test_screen_position, -self.new_facing_angle)
            collided = False
            collided_obj_pos = [0, 0]

            for tile_x in range(tiled_level.zero_tile_x, tiled_level.end_tile_x):
                for tile_y in range(tiled_level.zero_tile_y, tiled_level.end_tile_y):
                    tile = tiled_level.tile_grid[tile_x][tile_y]
                    collision_data = self.test_tile_collision(self.test_collision_sprite.rect,
                                                              test_screen_position, tile)
                    if collision_data[0]:
                        collided = True
                        if len(collision_data[1]) > 0:
                            collided_obj_pos[0] = collision_data[1][0][0] + tiled_level.position_offset[0]
                            collided_obj_pos[1] = collision_data[1][0][1] + tiled_level.position_offset[1]

                        for col_point in collision_data[1]:
                            collision_obj_rect = pygame.Rect(0.0, 0.0, 2.0, 2.0)
                            collision_obj_rect.center = col_point
                            self.collision_obj_rects.append(collision_obj_rect)

            for monster in monsters:
                if self.test_monster_collision(self.test_collision_sprite.rect, monster):
                    collided = True

            if collided:
                self.should_draw_collision_obj = True

                test_move_position = self.handle_collision(self.collision_obj_rects, test_move_position,
                                                           tiled_level, monsters)

                self.position[0] = test_move_position[0]
                self.position[1] = test_move_position[1]

                self.move_accumulator += self.total_speed * time_delta
            else:
                self.should_draw_collision_obj = False
                self.collision_obj_rects[:] = []
                forward_x_movement = self.current_vector[0] * time_delta * self.speed
                sideways_x_movement = self.current_vector[1] * self.strafe_speed * time_delta
                forward_y_movement = self.current_vector[1] * time_delta * self.speed
                sideways_y_movement = self.current_vector[0] * self.strafe_speed * time_delta
                self.position[0] += forward_x_movement + sideways_x_movement
                self.position[1] += forward_y_movement - sideways_y_movement
                self.move_accumulator += self.total_speed * time_delta

            self.update_screen_position(tiled_level.position_offset)

            if abs(self.move_accumulator) > 64.0:
                self.image = pygame.transform.rotate(self.active_weapon.anim_set.stand, self.new_facing_angle)
                self.rect = self.image.get_rect()
                self.rect.center = self.rot_point([self.screen_position[0],
                                                   self.screen_position[1] + self.sprite_rot_centre_offset[1]],
                                                  self.screen_position, -self.new_facing_angle)
                self.move_accumulator = 0.0
            elif abs(self.move_accumulator) > 48.0:
                self.image = pygame.transform.rotate(self.active_weapon.anim_set.step_left,
                                                     self.new_facing_angle)
                self.rect = self.image.get_rect()
                self.rect.center = self.rot_point([self.screen_position[0],
                                                   self.screen_position[1] + self.sprite_rot_centre_offset[1]],
                                                  self.screen_position, -self.new_facing_angle)
            elif abs(self.move_accumulator) > 32.0:
                self.image = pygame.transform.rotate(self.active_weapon.anim_set.stand, self.new_facing_angle)
                self.rect = self.image.get_rect()
                self.rect.center = self.rot_point([self.screen_position[0],
                                                   self.screen_position[1] + self.sprite_rot_centre_offset[1]],
                                                  self.screen_position, -self.new_facing_angle)
            elif abs(self.move_accumulator) > 16.0:
                self.image = pygame.transform.rotate(self.active_weapon.anim_set.step_right,
                                                     self.new_facing_angle)
                self.rect = self.image.get_rect()
                self.rect.center = self.rot_point([self.screen_position[0],
                                                   self.screen_position[1] + self.sprite_rot_centre_offset[1]],
                                                  self.screen_position, -self.new_facing_angle)
            else:
                self.image = pygame.transform.rotate(self.active_weapon.anim_set.stand, self.new_facing_angle)
                self.rect = self.image.get_rect()
                self.rect.center = self.rot_point([self.screen_position[0],
                                                   self.screen_position[1] + self.sprite_rot_centre_offset[1]],
                                                  self.screen_position, -self.new_facing_angle)

        else:
            self.update_screen_position(tiled_level.position_offset)
            self.speed = 0.0
            self.strafe_speed = 0.0
            self.total_speed = 0.0
            self.image = pygame.transform.rotate(self.active_weapon.anim_set.stand, self.new_facing_angle)
            self.rect = self.image.get_rect()
            self.rect.center = self.rot_point([self.screen_position[0],
                                               self.screen_position[1] + self.sprite_rot_centre_offset[1]],
                                              self.screen_position, -self.new_facing_angle)

    def handle_collision(self, collision_obj_rects, test_move_position, tiled_level, monsters):
        test_move_position = test_move_position
        if len(collision_obj_rects) > 0:
            collision_vec = [self.screen_position[0] - collision_obj_rects[0][0],
                             self.screen_position[1] - collision_obj_rects[0][1]]
            collision_vec_len = math.sqrt((collision_vec[0] * collision_vec[0]) + (collision_vec[1] * collision_vec[1]))
            normal_collision_vec = [collision_vec[0] / collision_vec_len, collision_vec[1] / collision_vec_len]

            collision_overlap = max(0.3, (self.collide_radius - collision_vec_len))

            normal_collision_vec[0] *= collision_overlap
            normal_collision_vec[1] *= collision_overlap

            test_move_position[0] += normal_collision_vec[0]
            test_move_position[1] += normal_collision_vec[1]

            test_screen_position = [0, 0]
            test_screen_position[0] = test_move_position[0] - tiled_level.position_offset[0]
            test_screen_position[1] = test_move_position[1] - tiled_level.position_offset[1]

            self.test_collision_sprite.image = pygame.transform.rotate(self.original_image, self.new_facing_angle)
            self.test_collision_sprite.rect = self.image.get_rect()
            test_sprite_x_pos = test_screen_position[0]
            test_sprite_y_pos = test_screen_position[1] + self.sprite_rot_centre_offset[1]
            self.test_collision_sprite.rect.center = self.rot_point([test_sprite_x_pos,
                                                                     test_sprite_y_pos],
                                                                    test_screen_position, -self.new_facing_angle)

            collided_obj_pos = [0, 0]
            collision_obj_rects[:] = []

            for tileX in range(tiled_level.zero_tile_x, tiled_level.end_tile_x):
                for tileY in range(tiled_level.zero_tile_y, tiled_level.end_tile_y):
                    tile = tiled_level.tile_grid[tileX][tileY]
                    collision_data = self.test_tile_collision(self.test_collision_sprite.rect,
                                                              test_screen_position, tile)
                    if collision_data[0]:
                        if len(collision_data[1]) > 0:
                            collided_obj_pos[0] = collision_data[1][0][0] + tiled_level.position_offset[0]
                            collided_obj_pos[1] = collision_data[1][0][1] + tiled_level.position_offset[1]

                        for colPoint in collision_data[1]:
                            collision_obj_rect = pygame.Rect(0.0, 0.0, 2.0, 2.0)
                            collision_obj_rect.center = colPoint
                            collision_obj_rects.append(collision_obj_rect)
            for monster in monsters:
                self.test_monster_collision(self.test_collision_sprite.rect, monster)

            test_move_position = self.handle_collision(collision_obj_rects, test_move_position, tiled_level, monsters)

        return test_move_position

    def add_health(self, health):
        self.health += health
        if self.health > self.max_health:
            self.health = self.max_health

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0
        self.should_flash_sprite = True

    def test_monster_collision(self, temp_player_rect, monster):
        collided = False
        if temp_player_rect.colliderect(monster.rect):
            collided = self.is_intersecting(monster)
        return collided

    def test_tile_collision(self, temp_player_rect, test_screen_position, tile):
        collided = (False, [])
        if temp_player_rect.colliderect(tile.rect):
            collided = self.is_intersecting_tile(tile, test_screen_position)
        return collided

    def test_projectile_collision(self, projectile_rect):
        collided = False
        if self.rect.colliderect(projectile_rect):
            if (self.test_point_in_circle(projectile_rect.topleft,
                                          self.screen_position,
                                          self.collide_radius)) or \
                    (self.test_point_in_circle(projectile_rect.topright,
                                               self.screen_position,
                                               self.collide_radius)) or \
                    (self.test_point_in_circle(projectile_rect.bottomleft,
                                               self.screen_position,
                                               self.collide_radius)) or \
                    (self.test_point_in_circle(projectile_rect.bottomright,
                                               self.screen_position,
                                               self.collide_radius)):
                collided = True
        return collided

    def test_pick_up_collision(self, pick_up_rect):
        collided = False
        if self.rect.colliderect(pick_up_rect):
            if (self.test_point_in_circle(pick_up_rect.topleft,
                                          self.screen_position,
                                          self.collide_radius)) or \
                    (self.test_point_in_circle(pick_up_rect.topright,
                                               self.screen_position,
                                               self.collide_radius)) or \
                    (self.test_point_in_circle(pick_up_rect.bottomleft,
                                               self.screen_position,
                                               self.collide_radius)) or \
                    (self.test_point_in_circle(pick_up_rect.bottomright,
                                               self.screen_position,
                                               self.collide_radius)):
                collided = True
        return collided

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

    @staticmethod
    def test_point_in_circle(point, circle_pos, circle_radius):
        return (point[0] - circle_pos[0]) ** 2 + (point[1] - circle_pos[1]) ** 2 < circle_radius ** 2

    # tiles positions are in screen space currently
    def is_intersecting_tile(self, tile, test_screen_position):
        collided = False
        collision_positions = []
        for collisionShape in tile.tile_data.collision_shapes:
            if collisionShape[0] == "circle":
                x_dist = (test_screen_position[0] - collisionShape[2][0]) ** 2
                y_dist = (test_screen_position[1] - collisionShape[2][1]) ** 2
                distance = math.sqrt(x_dist + y_dist)
                low_collide_bound = abs((self.collide_radius - collisionShape[3]))
                upper_collide_bound = (self.collide_radius + collisionShape[3])
                if low_collide_bound <= distance <= upper_collide_bound:
                    collided = True
                    shape_centre = [0.0, 0.0]
                    shape_centre[0] = collisionShape[2][0]
                    shape_centre[1] = collisionShape[2][1]
                    collision_positions.append(shape_centre)
            elif collisionShape[0] == "rect":
                result = self.test_rect_in_circle(collisionShape[2], test_screen_position, self.collide_radius)
                if result[0]:
                    collided = True

                    if len(result[1]) > 0:
                        for point in result[1]:
                            collision_positions.append(point)
                    else:
                        shape_centre = [0.0, 0.0]
                        shape_centre[0] = collisionShape[2].centerx
                        shape_centre[1] = collisionShape[2].centery
                        collision_positions.append(shape_centre)

        return collided, collision_positions

    def test_rect_in_circle(self, rect, circle_position, circle_radius):
        centre_in = self.test_point_in_circle(rect.center, circle_position, circle_radius)
        top_in = self.line_intersect_circle(circle_position, circle_radius, rect.topleft, rect.topright)
        bottom_in = self.line_intersect_circle(circle_position, circle_radius, rect.bottomleft, rect.bottomright)
        left_in = self.line_intersect_circle(circle_position, circle_radius, rect.topleft, rect.bottomleft)
        right_in = self.line_intersect_circle(circle_position, circle_radius, rect.topright, rect.bottomright)

        collision_points = []
        if top_in[0]:
            collision_points.append(top_in[1])
        if bottom_in[0]:
            collision_points.append(bottom_in[1])
        if left_in[0]:
            collision_points.append(left_in[1])
        if right_in[0]:
            collision_points.append(right_in[1])

        return centre_in or top_in[0] or bottom_in[0] or left_in[0] or right_in[0], collision_points

    # noinspection PyArgumentList
    @staticmethod
    def line_intersect_circle(circle_centre, circle_radius, line_start, line_end):
        intersects = False
        circle_centre_vec = pygame.math.Vector2(circle_centre)
        line_start_vec = pygame.math.Vector2(line_start)
        line_end_vec = pygame.math.Vector2(line_end)
        q = circle_centre_vec  # Centre of circle
        r = circle_radius  # Radius of circle
        p1 = line_start_vec  # Start of line segment
        v = line_end_vec - p1  # Vector along line segment

        a = v.dot(v)
        b = 2 * v.dot(p1 - q)
        c = p1.dot(p1) + q.dot(q) - 2 * p1.dot(q) - r ** 2

        disc = b ** 2 - 4 * a * c
        if disc < 0:
            return intersects, [0.0, 0.0]  # False

        sqrt_disc = math.sqrt(disc)
        t1 = (-b + sqrt_disc) / (2 * a)
        t2 = (-b - sqrt_disc) / (2 * a)

        if not (0 <= t1 <= 1 or 0 <= t2 <= 1):
            return intersects, [0.0, 0.0]  # False

        t = max(0, min(1, - b / (2 * a)))
        intersects = True
        intersection_vec = p1 + t * v
        return intersects, [intersection_vec.x, intersection_vec.y]

    def is_intersecting(self, c2):
        x_dist = (self.position[0] - c2.position[0]) ** 2
        y_dist = (self.position[1] - c2.position[1]) ** 2
        distance = math.sqrt(x_dist + y_dist)
        if abs((self.collide_radius - c2.collide_radius)) <= distance <= (self.collide_radius + c2.collide_radius):
            return True
        else:
            return False

    def draw_radius_circle(self, screen):
        ck = (127, 33, 33)
        int_position = [0, 0]
        int_position[0] = int(self.screen_position[0] - self.collide_radius)
        int_position[1] = int(self.screen_position[1] - self.collide_radius)
        s = pygame.Surface((self.collide_radius * 2, self.collide_radius * 2))

        # first, "erase" the surface by filling it with a color and
        # setting this color as colorkey, so the surface is empty
        s.fill(ck)
        s.set_colorkey(ck)

        pygame.draw.circle(s, pygame.Color("8888FF"), (self.collide_radius, self.collide_radius), self.collide_radius)

        # after drawing the circle, we can set the
        # alpha value (transparency) of the surface
        s.set_alpha(180)
        screen.blit(s, int_position)

        if self.should_draw_collision_obj:
            for col_obj_rect in self.collision_obj_rects:
                # print("Collide pos: " + str(col_obj_rect[0]) + ", " + str(col_obj_rect[1]))
                pygame.draw.rect(screen, pygame.Color("#FF0000"), col_obj_rect)

    @staticmethod
    def distance_from_line(point, line):

        x1 = line[0][0]
        y1 = line[0][1]
        x2 = line[1][0]
        y2 = line[1][1]
        x3 = point[0]
        y3 = point[1]

        px = x2 - x1
        py = y2 - y1

        something = px * px + py * py

        u = ((x3 - x1) * px + (y3 - y1) * py) / float(something)

        if u > 1:
            u = 1
        elif u < 0:
            u = 0

        x = x1 + u * px
        y = y1 + u * py

        dx = x - x3
        dy = y - y3

        # Note: If the actual distance does not matter,
        # if you only want to compare what this function
        # returns to other results of this function, you
        # can just return the squared distance instead
        # (i.e. remove the sqrt) to gain a little performance

        dist = math.sqrt(dx * dx + dy * dy)

        return dist

    @staticmethod
    def rot_point(point, axis, ang):
        """ Orbit. calculates the new loc for a point that rotates a given num of degrees around an axis point,
        +clockwise, -anticlockwise -> tuple x,y
        """
        ang -= 90
        x, y = point[0] - axis[0], point[1] - axis[1]
        radius = math.sqrt(x * x + y * y)  # get the distance between points

        r_ang = math.radians(ang)  # convert ang to radians.

        h = axis[0] + (radius * math.cos(r_ang))
        v = axis[1] + (radius * math.sin(r_ang))

        return [h, v]

    @staticmethod
    def lerp(a, b, c):
        return (c * b) + ((1.0 - c) * a)


class RespawnPlayer:
    def __init__(self, player):
        self.control_scheme = player.scheme

        self.respawn_timer = 2.0
        self.time_to_spawn = False
        self.has_respawned = False

    def update(self, frame_time_ms):
        self.respawn_timer -= (frame_time_ms / 1000.0)
        if self.respawn_timer < 0.0:
            self.time_to_spawn = True


class PlayerScore:
    def __init__(self, screen_position):
        self.screen_position = screen_position
        self.score = 0
