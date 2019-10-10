import pygame


class HealthBar:
    def __init__(self, start_pos, width, height):
        
        self.width = width
        self.height = height

        self.position = [start_pos[0], start_pos[1]]

        self.baseRect = pygame.Rect(self.position[0], self.position[1], self.width, self.height)
        self.powerRect = pygame.Rect(self.position[0]+1, self.position[1]+1, 1, self.height-2)
        self.health_rect = None

    def update(self, health, max_health):
        health_percentage = health / max_health
        if health_percentage < 0.0:
            health_percentage = 0.0
        health_width = self.lerp(0.0, self.width-2.0, health_percentage)
        self.health_rect = pygame.Rect(self.position[0] + 1, self.position[1] + 1, int(health_width), self.height - 2)

    def draw(self, screen, small_font):
        health_label_text_render = small_font.render("Health:", True, pygame.Color("#FFFFFF"))
        text_rect = health_label_text_render.get_rect()
        screen.blit(health_label_text_render,
                    health_label_text_render.get_rect(centerx=self.position[0]-text_rect.width+12,
                                                      centery=self.position[1]+text_rect.height-3))
        # noinspection PyArgumentList
        pygame.draw.rect(screen, pygame.Color("#000000"), self.baseRect, 0)
        # noinspection PyArgumentList
        pygame.draw.rect(screen, pygame.Color("#770000"), self.health_rect, 0)

    @staticmethod
    def lerp(a, b, c):
        return (c * b) + ((1.0 - c) * a)
