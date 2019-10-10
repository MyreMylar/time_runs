import pygame
from game.ui_text_button import UTTextButton


class MainMenu:

    def __init__(self, fonts):
        self.show_menu = True
        self.show_editor = False

        self.is_start_game_selected = True
        self.is_run_editor_selected = False
        self.start_game = False

        self.background_image = pygame.image.load("images/menu_background.png").convert()

        self.play_game_button = UTTextButton([437, 465, 150, 35], "Play Game", fonts, 1)
        self.edit_map_button = UTTextButton([437, 515, 150, 35], "Edit Map", fonts, 1)

    def run(self, screen, fonts, screen_data):
        is_main_menu_and_index = [0, 0]
        for event in pygame.event.get():
            self.play_game_button.handle_input_event(event)
            self.edit_map_button.handle_input_event(event)

        self.play_game_button.update()
        self.edit_map_button.update()

        if self.play_game_button.was_pressed():
            self.start_game = True
            self.show_menu = False

        if self.edit_map_button.was_pressed():
            self.show_editor = True
            self.show_menu = False
                    
        screen.blit(self.background_image, (0, 0))  # draw the background
        
        main_menu_title_string = "Time Runs"
        main_menu_title_text_render = fonts[2].render(main_menu_title_string, True, pygame.Color("#FFFFFF"))
        screen.blit(main_menu_title_text_render,
                    main_menu_title_text_render.get_rect(centerx=screen_data.screen_size[0] * 0.5,
                                                         centery=128))

        self.play_game_button.draw(screen)
        self.edit_map_button.draw(screen)

        if self.show_editor:
            is_main_menu_and_index[0] = 2

        elif self.start_game:
            is_main_menu_and_index[0] = 1
        else:
            is_main_menu_and_index[0] = 0

        return is_main_menu_and_index
