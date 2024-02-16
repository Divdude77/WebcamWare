import pygame


class Timer:
    def __init__(self, time, screen=None):
        self.screen = screen
        self.time = time
        self.start_time = None
        self.clocks = [
            pygame.transform.scale(pygame.image.load("assets/img/clock/clock0.png").convert_alpha(), (75, 75)),
            pygame.transform.scale(pygame.image.load("assets/img/clock/clock1.png").convert_alpha(), (75, 75)),
            pygame.transform.scale(pygame.image.load("assets/img/clock/clock2.png").convert_alpha(), (75, 75)),
            pygame.transform.scale(pygame.image.load("assets/img/clock/clock3.png").convert_alpha(), (75, 75)),
            pygame.transform.scale(pygame.image.load("assets/img/clock/clock4.png").convert_alpha(), (75, 75)),
            pygame.transform.scale(pygame.image.load("assets/img/clock/clock5.png").convert_alpha(), (75, 75)),
            pygame.transform.scale(pygame.image.load("assets/img/clock/clock6.png").convert_alpha(), (75, 75)),
            pygame.transform.scale(pygame.image.load("assets/img/clock/clock7.png").convert_alpha(), (75, 75)),
                       ]
        self.clock = 0

    def tick(self):
        if not self.start_time:
            self.start_time = pygame.time.get_ticks()

        return (pygame.time.get_ticks() - self.start_time) / 1000
    
    def reset(self):
        self.start_time = None
    
    def draw_clock(self, inc):
        self.screen.blit(self.clocks[self.clock // 5], (5, self.screen.get_height()-75))
        self.clock += inc
        if self.clock >= len(self.clocks) * 5:
            self.clock = 0
        
    def draw(self):
        seconds = self.tick()

        if seconds >= self.time:
            pygame.draw.rect(self.screen, (0, 0, 0), (10, self.screen.get_height()-60, self.screen.get_width()-20, 50), 2, border_radius=20)
            self.draw_clock(0)
            return True

        pygame.draw.rect(self.screen, (255, 0, 0), (10, self.screen.get_height()-60, (self.screen.get_width()-20) * (1 - (seconds / self.time)), 50), border_radius=20)
        pygame.draw.rect(self.screen, (0, 0, 0), (10, self.screen.get_height()-60, self.screen.get_width()-20, 50), 2, border_radius=20)
        self.draw_clock(1)

    def get_ratio(self):
        if self.start_time:
            return (pygame.time.get_ticks()-self.start_time)/1000 / self.time

        return 0


class AnimatedText:
    def __init__(self, text, x, y, screen, font_size=36, primary_color=(255,255,255), outline_color=None, outline=None, duration=None):
        self.text = text
        self.x = x
        self.y = y
        self.base_x = x
        self.base_y = y
        self.inc_x = 0.25
        self.inc_y = 0.5
        self.screen = screen
        self.font_size = 0
        self.base_font_size = font_size
        self.primary_color = primary_color
        self.outline_color = outline_color
        self.outline = outline
        self.timer = Timer(duration) if duration else None
    
    def draw_text(self, x, y, color):
        font = pygame.font.Font("assets/fonts/easvhs.ttf", self.font_size)

        text = font.render(self.text, True, color)
        text_rect = text.get_rect(center=(x, y))
        self.screen.blit(text, text_rect)

    def draw(self):
        if self.font_size < self.base_font_size:
            self.font_size += 5

        else:
            if self.timer:
                if self.timer.tick() >= self.timer.time:
                    return True
            self.move()
        
        if self.outline:
            self.draw_text(self.x - self.outline, self.y - self.outline, self.outline_color)
            self.draw_text(self.x + self.outline, self.y - self.outline, self.outline_color)
            self.draw_text(self.x - self.outline, self.y + self.outline, self.outline_color)
            self.draw_text(self.x + self.outline, self.y + self.outline, self.outline_color)
        self.draw_text(self.x, self.y, self.primary_color)
        
    def move(self):
        self.y += self.inc_y
        self.x -= self.inc_x
        if self.y < self.base_y - 15 or self.y > self.base_y + 15:
            self.inc_y = -self.inc_y
        if self.x < self.base_x - 20 or self.x > self.base_x + 20:
            self.inc_x = -self.inc_x