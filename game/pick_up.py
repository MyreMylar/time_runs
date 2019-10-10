import pygame
import random


class PickUpSpawner:
    def __init__(self, pick_ups, all_pick_up_sprites):
        self.pick_ups = pick_ups
        self.allPickUpSprites = all_pick_up_sprites
        self.shotgun_ammo_image = pygame.image.load("images/pick_ups/shotgun_ammo.png")
        self.launcher_ammo_image = pygame.image.load("images/pick_ups/launcher_ammo.png")
        self.health_image = pygame.image.load("images/pick_ups/health.png")
        self.time_crystal = pygame.image.load("images/pick_ups/time_crystal.png")

    def try_spawn(self, spawn_position):
        random_roll = random.randint(0, 100)
        if random_roll < 10:
            self.pick_ups.append(PickUp(spawn_position, self.health_image,
                                        "health", self.allPickUpSprites))
        elif 10 < random_roll <= 20:
            self.pick_ups.append(PickUp(spawn_position, self.shotgun_ammo_image,
                                        "shotgun_ammo", self.allPickUpSprites))
        elif 20 < random_roll <= 25:
            self.pick_ups.append(PickUp(spawn_position, self.launcher_ammo_image,
                                        "launcher_ammo", self.allPickUpSprites))
        elif random_roll <= 50:
            self.pick_ups.append(PickUp(spawn_position, self.time_crystal,
                                        "time_crystal", self.allPickUpSprites))
            

class PickUp(pygame.sprite.Sprite):
    def __init__(self, start_pos, image, type_name, all_pick_up_sprites, *groups):
        super().__init__(*groups)
        self.world_position = [start_pos[0], start_pos[1]]
        self.type_name = type_name
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = start_pos

        self.position = [float(self.rect.center[0]), float(self.rect.center[1])]

        self.all_pick_up_sprites = all_pick_up_sprites
        self.all_pick_up_sprites.add(self)
        self.should_die = False

    def update_movement_and_collision(self, player, tiled_level):
        
        self.position[0] = self.world_position[0] - tiled_level.position_offset[0]
        self.position[1] = self.world_position[1] - tiled_level.position_offset[1]
        self.rect.center = self.position
        
        if player.test_pick_up_collision(self.rect):
            self.should_die = True
            if self.type_name == "health":
                player.add_health(25)
            elif self.type_name == "shotgun_ammo":
                player.shotgun_weapon.ammo_count += 12
            elif self.type_name == "launcher_ammo":
                player.launcher_weapon.ammo_count += 1
            elif self.type_name == "time_crystal":
                player.activate_time_crystal()

            self.all_pick_up_sprites.remove(self)
