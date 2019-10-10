import pygame


class WeaponAnimation:
    def __init__(self, sprite_sheet, y_start):
        self.step_left = sprite_sheet.subsurface(pygame.Rect(0, y_start, 48, 64))
        self.stand = sprite_sheet.subsurface(pygame.Rect(48, y_start, 48, 64))
        self.step_right = sprite_sheet.subsurface(pygame.Rect(96, y_start, 48, 64))


class BaseWeapon:
    def __init__(self, sprite_sheet, y_sheet_start, explosion_sprite_sheet):
        self.anim_set = WeaponAnimation(sprite_sheet, y_sheet_start)

        self.fire_rate_acc = 0.0
        self.fire_rate = 1.0
        self.can_fire = True

        self.player_position = [0, 0]
        self.current_aim_vector = [0, 0]
        self.explosion_sprite_sheet = explosion_sprite_sheet

        self.barrel_forward_offset = 32
        self.barrel_side_offset = 6
        barrel_x_pos = self.player_position[0] + (self.current_aim_vector[0] * self.barrel_forward_offset) - (
                    self.current_aim_vector[1] * self.barrel_side_offset)
        barrel_y_pos = self.player_position[1] + (self.current_aim_vector[1] * self.barrel_forward_offset) + (
                    self.current_aim_vector[0] * self.barrel_side_offset)
        self.barrel_exit_pos = [barrel_x_pos, barrel_y_pos]

        self.ammo_count = -1

    def update(self, time_delta, time_multiplier, player_position, current_aim_vector):
        if self.fire_rate_acc < self.fire_rate:
            self.fire_rate_acc += time_delta * time_multiplier
        else:
            if self.ammo_count != 0:
                self.can_fire = True

        self.player_position = player_position
        self.current_aim_vector = current_aim_vector

        # calculate the position where the projectiles should leave the weapon

        barrel_x_pos = self.player_position[0] + (self.current_aim_vector[0] * self.barrel_forward_offset) - (
                self.current_aim_vector[1] * self.barrel_side_offset)
        barrel_y_pos = self.player_position[1] + (self.current_aim_vector[1] * self.barrel_forward_offset) + (
                self.current_aim_vector[0] * self.barrel_side_offset)
        self.barrel_exit_pos = [barrel_x_pos, barrel_y_pos]

    def fire(self, projectiles):
        pass
