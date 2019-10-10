from game.base_weapon import BaseWeapon
from game.bullet import Bullet


class ShotgunWeapon(BaseWeapon):
    def __init__(self, sprite_sheet, explosion_sprite_sheet):
        player_sprite_y_offset = 64
        super().__init__(sprite_sheet, player_sprite_y_offset, explosion_sprite_sheet)

        self.starting_ammo = 24
        self.ammo_count = self.starting_ammo
        self.fire_rate = 0.4
        self.per_bullet_damage = 50

        self.barrel_forward_offset = 32
        self.barrel_side_offset_1 = 4
        self.barrel_side_offset_2 = 8
        self.barrel_1_exit_pos = [0, 0]
        self.barrel_2_exit_pos = [0, 0]

        self.fire_rate_acc = self.fire_rate

    def update(self, time_delta, time_multiplier, player_position, current_aim_vector):
        super().update(time_delta, time_multiplier, player_position, current_aim_vector)

        barrel_1_x_forward = (self.current_aim_vector[0] * self.barrel_forward_offset)
        barrel_1_x_sideways = (self.current_aim_vector[1] * self.barrel_side_offset_1)
        barrel_1_y_forward = (self.current_aim_vector[1] * self.barrel_forward_offset)
        barrel_1_y_sideways = (self.current_aim_vector[0] * self.barrel_side_offset_1)
        barrel_1_x_pos = self.player_position[0] + barrel_1_x_forward - barrel_1_x_sideways
        barrel_1_y_pos = self.player_position[1] + barrel_1_y_forward + barrel_1_y_sideways
        self.barrel_1_exit_pos = [barrel_1_x_pos, barrel_1_y_pos]

        barrel_2_x_forward = (self.current_aim_vector[0] * self.barrel_forward_offset)
        barrel_2_x_sideways = (self.current_aim_vector[1] * self.barrel_side_offset_2)
        barrel_2_y_forward = (self.current_aim_vector[1] * self.barrel_forward_offset)
        barrel_2_y_sideways = (self.current_aim_vector[0] * self.barrel_side_offset_2)
        barrel_2_x_pos = self.player_position[0] + barrel_2_x_forward - barrel_2_x_sideways
        barrel_2_y_pos = self.player_position[1] + barrel_2_y_forward + barrel_2_y_sideways
        self.barrel_2_exit_pos = [barrel_2_x_pos, barrel_2_y_pos]

    def fire(self, projectiles):
        if self.ammo_count > 0:
            self.ammo_count -= 1
        projectiles.append(Bullet(self.barrel_1_exit_pos, self.current_aim_vector,
                                  self.per_bullet_damage, self.explosion_sprite_sheet))
        projectiles.append(Bullet(self.barrel_2_exit_pos, self.current_aim_vector,
                                  self.per_bullet_damage, self.explosion_sprite_sheet))
