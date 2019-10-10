import pygame


class GunsUI:
    def __init__(self, start_pos, width, height):
        
        self.width = width
        self.height = height

        self.position = [start_pos[0], start_pos[1]]

        self.base_rect = pygame.Rect(self.position[0], self.position[1], self.width, self.height)
        self.power_rect = pygame.Rect(self.position[0] + 1, self.position[1] + 1, 1, self.height - 2)
        self.reload_rect = None
        self.reload_percentage = 1.0

        self.ammo_count = -1

    def update(self, reload_counter, reload_time, ammo_count):
        self.ammo_count = ammo_count

        reload_width = 0
        if self.ammo_count != 0:
            self.reload_percentage = reload_counter / reload_time
            if self.reload_percentage < 0.0:
                self.reload_percentage = 0.0
            reload_width = self.lerp(0.0, self.width - 2.0, self.reload_percentage)
        self.reload_rect = pygame.Rect(self.position[0] + 1, self.position[1] + 1, int(reload_width), self.height - 2)

    def draw(self, screen, small_font):
        cannon_label_text_render = small_font.render("Guns:", True, pygame.Color("#FFFFFF"))
        text_rect = cannon_label_text_render.get_rect()
        screen.blit(cannon_label_text_render,
                    cannon_label_text_render.get_rect(centerx=self.position[0]-text_rect.width+12,
                                                      centery=self.position[1]+text_rect.height-3))
        # noinspection PyArgumentList
        pygame.draw.rect(screen, pygame.Color("#000000"), self.base_rect, 0)
        # noinspection PyArgumentList
        pygame.draw.rect(screen, pygame.Color("#777777"), self.reload_rect, 0)

        reloading_string = "Ready!"
        if self.reload_percentage < 1.0:
            reloading_string = "Reloading..."
        if self.ammo_count == 0:
            reloading_string = "Out of Ammo"
            
        reloading_text_render = small_font.render(reloading_string, True, pygame.Color("#FFFFFF"))
        screen.blit(reloading_text_render,
                    reloading_text_render.get_rect(x=self.position[0]+12,
                                                   centery=self.position[1]+text_rect.height-3))

    @staticmethod
    def lerp(a, b, c):
        return (c * b) + ((1.0 - c) * a)
