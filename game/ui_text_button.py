import pygame
from pygame.locals import *


class UTTextButton:
    def __init__(self, rect, button_text, fonts, font_size):
        self.fonts = fonts
        self.button_text = button_text
        self.rect = rect
        self.clicked_button = False
        self.is_hovered = True
        self.font_size = font_size

        self.is_enabled = True

        self.button_colour = pygame.Color("#444444")
        self.text_colour = pygame.Color("#FFFFFF")

        self.button_text_render = self.fonts[self.font_size].render(self.button_text, True, self.text_colour)

    def handle_input_event(self, event):
        if self.is_enabled and self.is_inside(pygame.mouse.get_pos()):
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.clicked_button = True
                    
    def disable(self):
        self.is_enabled = False
        self.button_colour = pygame.Color("#333333")
        self.text_colour = pygame.Color("#000000")

    def enable(self):
        self.is_enabled = True
        self.button_colour = pygame.Color("#444444")
        self.text_colour = pygame.Color("#FFFFFF")

    def was_pressed(self):
        was_pressed = self.clicked_button
        self.clicked_button = False
        return was_pressed

    def set_text(self, text):
        self.button_text = text
        self.button_text_render = self.fonts[self.font_size].render(self.button_text, True, self.text_colour)
    
    def update(self):
        if self.is_enabled and self.is_inside(pygame.mouse.get_pos()):
            self.is_hovered = True
            self.button_colour = pygame.Color("#666666")
        elif self.is_enabled:
            self.is_hovered = False
            self.button_colour = pygame.Color("#444444")

    def is_inside(self, screen_pos):
        is_inside = False
        if self.rect[0] <= screen_pos[0] <= self.rect[0]+self.rect[2]:
            if self.rect[1] <= screen_pos[1] <= self.rect[1]+self.rect[3]:
                is_inside = True
        return is_inside

    def draw(self, screen):
        # noinspection PyArgumentList
        pygame.draw.rect(screen, self.button_colour, pygame.Rect(self.rect[0], self.rect[1],
                                                                 self.rect[2], self.rect[3]), 0)
        screen.blit(self.button_text_render,
                    self.button_text_render.get_rect(centerx=self.rect[0] + self.rect[2] * 0.5,
                                                     centery=self.rect[1] + self.rect[3] * 0.5))
