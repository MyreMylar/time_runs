from game.base_weapon import BaseWeapon
from game.bullet import Bullet


class RifleWeapon(BaseWeapon):
    def __init__(self, sprite_sheet, explosion_sprite_sheet):
        player_sprite_y_offset = 0
        super().__init__(sprite_sheet, player_sprite_y_offset, explosion_sprite_sheet)

        self.fire_rate = 0.15
        self.per_bullet_damage = 50

        # set the offset position where the projectiles should leave the weapon
        # (this is from the centre of the player sprite)
        self.barrel_forward_offset = 32
        self.barrel_side_offset = 6
        
        self.fire_rate_acc = self.fire_rate

    def fire(self, projectiles):
        # infinite bullets so don't track ammo
        projectiles.append(Bullet(self.barrel_exit_pos, self.current_aim_vector, self.per_bullet_damage,
                                  self.explosion_sprite_sheet))
