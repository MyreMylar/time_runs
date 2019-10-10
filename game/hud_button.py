import pygame


class HUDButton:
    def __init__(self, start_pos, button_image_name, hud_sprites):
        self.clicked = False
        self.button_image_name = button_image_name
        self.image = pygame.image.load("images/hud_icons/" + self.button_image_name + "_unselected.png").convert()
        self.img_selected = pygame.image.load("images/hud_icons/" + self.button_image_name + "_selected.png").convert()
        self.sprite = pygame.sprite.Sprite()      
        self.sprite.image = self.image
        self.sprite.rect = self.image.get_rect()  
        self.sprite.rect.center = start_pos
        hud_sprites.add(self.sprite)

        # value text
        self.text_value = 0
        self.font = pygame.font.Font(None, 16)
        cost_string = "{:,}".format(self.text_value)
        self.cost_text_render = self.font.render(cost_string, True, pygame.Color("#FFFFFF"))
        self.text_pos = [start_pos[0], start_pos[1] + 42]

        self.selected = False

    def update_text_values(self, value):
        self.text_value = value
        cost_string = ""
        text_colour = pygame.Color("#FFFFFF")
        if self.text_value > 0:
            cost_string = "{:,}".format(self.text_value)
        elif self.text_value == 0:
            cost_string = "{:,}".format(self.text_value)
            text_colour = pygame.Color("#EE3333")
        elif self.text_value == -1:
            cost_string = "infinite"
        self.cost_text_render = self.font.render(cost_string, True, text_colour)
        
    def set_selected(self):
        self.selected = True
        self.sprite.image = self.img_selected

    def clear_selected(self):
        self.selected = False
        self.sprite.image = self.image

    def draw_text(self, screen):
        screen.blit(self.cost_text_render,
                    self.cost_text_render.get_rect(centerx=self.text_pos[0],
                                                   centery=self.text_pos[1]))
