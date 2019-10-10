from game.base_monster import BaseMonster


class StandardMonster(BaseMonster):
    def __init__(self, type_id, start_pos, sprite_map, all_monster_sprites,
                 play_area, tiled_level, explosions_sprite_sheet):
        super().__init__(type_id, start_pos, sprite_map, all_monster_sprites,
                         play_area, tiled_level, explosions_sprite_sheet)

        self.cash_value = 30
        self.idle_move_speed = self.set_average_speed(35)
        self.attack_move_speed = self.set_average_speed(75)
        self.move_speed = self.idle_move_speed
        self.health = 95
