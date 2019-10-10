import os
import pygame
from pygame.locals import *

from game.map_editor import MapEditor
from game.main_menu import MainMenu
from player import Player, Scheme
from game.player_health_bar import HealthBar
from game.player_guns_ui import GunsUI
from game.tiled_level import TiledLevel
from game.pick_up import PickUpSpawner
from game.hud_button import HUDButton

# ------------------------------------------------
# Open the map editor in the game for challenge 1!
# ------------------------------------------------

        
class ScreenData:
    def __init__(self, hud_size, editor_hud_size, screen_size):
        self.screen_size = screen_size
        self.hud_dimensions = hud_size
        self.editor_hud_dimensions = editor_hud_size
        self.play_area = [self.screen_size[0], self.screen_size[1] - self.hud_dimensions[1]]

    def set_editor_active(self):
        self.play_area = [self.screen_size[0], self.screen_size[1] - self.editor_hud_dimensions[1]]


def main():
    
    pygame.init()
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.key.set_repeat()
    pygame.display.set_caption('Time Runs')
    x_screen_size = 1024
    y_screen_size = 600
    screen_data = ScreenData([x_screen_size, 112], [x_screen_size, 184], [x_screen_size, y_screen_size])
    screen = pygame.display.set_mode(screen_data.screen_size)

    background = pygame.Surface(screen.get_size())
    background = background.convert(screen)
    background.fill((95, 140, 95))

    player_sprites = pygame.sprite.OrderedUpdates()
    all_tile_sprites = pygame.sprite.Group()
    all_top_tile_sprites = pygame.sprite.Group()
    all_monster_sprites = pygame.sprite.OrderedUpdates()
    all_pick_up_sprites = pygame.sprite.Group()
    all_explosion_sprites = pygame.sprite.Group()
    all_projectile_sprites = pygame.sprite.Group()
    hud_sprites = pygame.sprite.Group()

    fonts = []
    small_font = pygame.font.Font(None, 16)

    font = pygame.font.Font(None, 32)
    large_font = pygame.font.Font("data/HennyPenny-Regular.ttf", 90)

    fonts.append(small_font)
    fonts.append(font)
    fonts.append(large_font)
    
    explosions_sprite_sheet = pygame.image.load("images/explosions.png").convert_alpha()

    players = []
    monsters = []
    pick_ups = []
    projectiles = []
    explosions = []
    new_explosions = []
    hud_buttons = []

    tiled_level = TiledLevel([32, 64], all_tile_sprites, all_top_tile_sprites, all_monster_sprites,
                             monsters, screen_data, explosions_sprite_sheet)

    tiled_level.load_tiles()
    tiled_level.reset_guards()
    main_menu = MainMenu(fonts)
    
    hud_rect = pygame.Rect(0, screen_data.screen_size[1] - screen_data.hud_dimensions[1],
                           screen_data.hud_dimensions[0], screen_data.hud_dimensions[1])

    editor_hud_rect = pygame.Rect(0, screen_data.screen_size[1] - screen_data.editor_hud_dimensions[1],
                                  screen_data.editor_hud_dimensions[0], screen_data.editor_hud_dimensions[1])
    editor = MapEditor(tiled_level, editor_hud_rect, fonts)
    
    health_bar = HealthBar([screen_data.hud_dimensions[0] - (screen_data.hud_dimensions[0] * 0.20),
                            screen_data.screen_size[1] - (0.75 * screen_data.hud_dimensions[1])],
                           (screen_data.hud_dimensions[0] * 0.15), 16)
    guns_ui = GunsUI([screen_data.hud_dimensions[0] - (screen_data.hud_dimensions[0] * 0.20),
                      screen_data.screen_size[1] - (0.5 * screen_data.hud_dimensions[1])],
                     (screen_data.hud_dimensions[0] * 0.15), 16)
    
    rifle_button = HUDButton([48, screen_data.screen_size[1] - screen_data.hud_dimensions[1] + 48],
                             "rifle_icon", hud_sprites)
    shotgun_button = HUDButton([144, screen_data.screen_size[1] - screen_data.hud_dimensions[1] + 48],
                               "shotgun_icon", hud_sprites)
    launcher_button = HUDButton([240, screen_data.screen_size[1] - screen_data.hud_dimensions[1] + 48],
                                "launcher_icon", hud_sprites)
    hud_buttons.append(rifle_button)
    hud_buttons.append(shotgun_button)
    hud_buttons.append(launcher_button)

    pick_up_spawner = PickUpSpawner(pick_ups, all_pick_up_sprites)

    player = None
    
    clock = pygame.time.Clock()

    time_multiplier = 1.0
    running = True
    
    is_main_menu = True
    is_editor = False
    
    is_game_over = False
    restart_game = False
    win_message = ""

    while running:
        frame_time = clock.tick(60)
        time_delta = frame_time/1000.0

        if is_main_menu:
            is_main_menu_and_index = main_menu.run(screen, fonts, screen_data)
            if is_main_menu_and_index[0] == 0:
                is_main_menu = True
            elif is_main_menu_and_index[0] == 1:
                is_main_menu = False
            elif is_main_menu_and_index[0] == 2:
                is_main_menu = False
                is_editor = True

            if not is_main_menu and not is_editor:
                # spawn player
                default_scheme = Scheme()
                player = Player(tiled_level.find_player_start(), tiled_level, default_scheme,
                                explosions_sprite_sheet, hud_buttons)
                players.append(player)
                pygame.mouse.set_visible(False)
                pygame.event.set_grab(True)
                         
        elif is_editor:
            screen_data.set_editor_active()
            running = editor.run(screen, background, all_tile_sprites, editor_hud_rect, time_delta)

        else:
            if restart_game:
                restart_game = False

                # clear all stuff
                players[:] = []
                monsters[:] = []
                pick_ups[:] = []
                projectiles[:] = []
                explosions[:] = []
                new_explosions[:] = []
                all_monster_sprites.empty()
                all_pick_up_sprites.empty()

                is_game_over = False
                
                tiled_level.reset_guards()
                default_scheme = Scheme()
                player = Player(tiled_level.find_player_start(), tiled_level, default_scheme,
                                explosions_sprite_sheet, hud_buttons)
                players.append(player)
                  
            elif is_game_over:
                pass
            else:
                pass

            if player is not None and player.health <= 0:
                is_game_over = True
                win_message = "You have been defeated!"
            if len(monsters) == 0 and player.health > 0:
                is_game_over = True
                win_message = "You are victorious!"

            all_projectile_sprites.empty()
            all_explosion_sprites.empty()
            player_sprites.empty()
                   
            # handle UI and inout events
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    if is_game_over:
                        if event.key == K_y:
                            restart_game = True

                for player in players:
                    player.process_event(event)

            if player is not None:
                health_bar.update(player.health, player.max_health)
                if player.active_weapon is not None:
                    guns_ui.update(player.active_weapon.fire_rate_acc,
                                   player.active_weapon.fire_rate, player.active_weapon.ammo_count)

            tiled_level.update_offset_position(player.position, all_tile_sprites)

            for pick_up in pick_ups:
                pick_up.update_movement_and_collision(player, tiled_level)
            pick_ups[:] = [pick_up for pick_up in pick_ups if not pick_up.should_die]

            for player in players:
                player.update_movement_and_collision(time_delta, projectiles, tiled_level, monsters, new_explosions)
                player_sprites = player.update_sprite(player_sprites, time_delta)
                time_multiplier = player.calculate_time_multipliers()
            players[:] = [player for player in players if not player.should_die]

            for monster in monsters:
                monster.update_movement_and_collision(time_delta, time_multiplier, player,
                                                      new_explosions, tiled_level,
                                                      projectiles, pick_up_spawner)
                monster.update_sprite(time_delta, time_multiplier)
            monsters[:] = [monster for monster in monsters if not monster.should_die]
            new_explosions[:] = []

            for projectile in projectiles:
                projectile.update_movement_and_collision(tiled_level, tiled_level.collidable_tiles, players, monsters,
                                                         time_delta, time_multiplier, new_explosions, explosions)
                all_projectile_sprites = projectile.update_sprite(all_projectile_sprites)
            projectiles[:] = [projectile for projectile in projectiles if not projectile.should_die]

            for explosion in explosions:
                all_explosion_sprites = explosion.update_sprite(all_explosion_sprites, time_delta,
                                                                time_multiplier, tiled_level)
            explosions[:] = [explosion for explosion in explosions if not explosion.should_die]
            
            screen.blit(background, (0, 0))  # draw the background

            all_tile_sprites.draw(screen)
            all_pick_up_sprites.draw(screen)
            all_monster_sprites.draw(screen)
            player_sprites.draw(screen)
            all_explosion_sprites.draw(screen)
            all_projectile_sprites.draw(screen)

            # ------------------------------------
            # Uncomment For Collision shape debugging
            # -------------------------------------

            # tiled_level.draw_tile_collision_shapes(screen)

            # player.draw_radius_circle(screen)

            # noinspection PyArgumentList
            pygame.draw.rect(screen, pygame.Color("#888888"), hud_rect, 0)  # draw the hud
            hud_sprites.draw(screen)
            health_bar.draw(screen, small_font)
            guns_ui.draw(screen, small_font)

            if not player.should_die:
                for button in hud_buttons:
                    if button.button_image_name == "rifle_icon":
                        button.update_text_values(player.rifle_weapon.ammo_count)
                    elif button.button_image_name == "shotgun_icon":
                        button.update_text_values(player.shotgun_weapon.ammo_count)
                    elif button.button_image_name == "launcher_icon":
                        button.update_text_values(player.launcher_weapon.ammo_count)
                    button.draw_text(screen)

            for player in players:
                if player.time_crystal_active:
                    crystal_countdown = player.time_crystal_time - player.time_crystal_acc
                    time_stop_string = "Time Crystal Active: " + "{:.2f}".format(crystal_countdown)
                    time_stop_text_render = font.render(time_stop_string, True, pygame.Color("#FFFFFF"))
                    screen.blit(time_stop_text_render, time_stop_text_render.get_rect(x=32, centery=32))

            time_string = "Speed of time: " + str(int(time_multiplier/1.0 * 100.0)) + "%"
            time_text_render = small_font.render(time_string, True, pygame.Color("#FFFFFF"))
            time_text_x_pos = screen_data.hud_dimensions[0] * 0.85
            time_text_y_pos = screen_data.screen_size[1] - (screen_data.hud_dimensions[1] * 0.15)
            screen.blit(time_text_render,
                        time_text_render.get_rect(centerx=time_text_x_pos,
                                                  centery=time_text_y_pos))
            
            if time_delta > 0.0:
                fps_string = "FPS: " + "{:.2f}".format(1.0/time_delta)
                fps_text_render = font.render(fps_string, True, pygame.Color("#FFFFFF"))
                fps_text_x_pos = screen_data.hud_dimensions[0] * 0.9
                fps_text_y_pos = screen_data.screen_size[1] - (screen_data.screen_size[1] * 0.95)
                screen.blit(fps_text_render,
                            fps_text_render.get_rect(centerx=fps_text_x_pos,
                                                     centery=fps_text_y_pos))
            
            if is_game_over:
                win_message_text_render = large_font.render(win_message, True, pygame.Color("#FFFFFF"))
                win_message_text_render_rect = win_message_text_render.get_rect(centerx=x_screen_size/2,
                                                                                centery=(y_screen_size/2)-128)
                play_again_text_render = font.render("Play Again? Press 'Y' to restart", True, pygame.Color("#FFFFFF"))
                play_again_text_render_rect = play_again_text_render.get_rect(centerx=x_screen_size/2,
                                                                              centery=(y_screen_size/2)-64)
                screen.blit(win_message_text_render, win_message_text_render_rect)
                screen.blit(play_again_text_render, play_again_text_render_rect)

        pygame.display.flip()  # flip all our drawn stuff onto the screen

    pygame.quit()  # exited game loop so quit pygame


if __name__ == '__main__':
    main()
