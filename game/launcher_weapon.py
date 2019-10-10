from game.base_weapon import BaseWeapon
from game.missile import Missile


class LauncherWeapon(BaseWeapon):
    def __init__(self, sprite_sheet, explosion_sprite_sheet):

        player_sprite_y_offset = 128
        super().__init__(sprite_sheet, player_sprite_y_offset, explosion_sprite_sheet)

        self.starting_ammo = 3
        self.ammo_count = self.starting_ammo
        self.fire_rate = 1.5

        self.barrel_forward_offset = 28
        self.barrel_side_offset = 11

        self.missile_damage = 100

        self.fire_rate_acc = self.fire_rate
        
    def fire(self, projectiles):
        self.ammo_count -= 1
        projectiles.append(Missile(self.barrel_exit_pos, self.current_aim_vector,
                                   self.missile_damage, self.explosion_sprite_sheet))
