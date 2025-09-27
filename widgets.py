import pygame
from datetime import datetime
white = (255,255,255)

class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, initial_val, percent=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.knob_radius = h // 2
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.initial_val = initial_val
        self.knob_x = self.get_knob_x_from_value(initial_val)
        self.dragging = False
        self.font = pygame.font.SysFont("consolas", 20)
        self.percent = percent
        self.time = 0

    def get_knob_x_from_value(self, value):
        return (self.rect.x + (value - self.min_val) / (self.max_val - self.min_val) * self.rect.w)

    def get_value_from_knob(self, knob_x):
        ratio = (knob_x - self.rect.x) / self.rect.w
        return (self.min_val + ratio * (self.max_val - self.min_val))

    def handle_event(self, event):
        if event == None:
            None
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if pygame.Rect(self.knob_x - self.knob_radius, self.rect.centery - self.knob_radius,
                           self.knob_radius*2, self.knob_radius*2).collidepoint(event.pos):
                self.dragging = True
            if datetime.now().timestamp()-self.time <= 0.5:
                self.value = self.initial_val
                self.knob_x = self.get_knob_x_from_value(self.initial_val)
                self.dragging = False
            self.time = datetime.now().timestamp()
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.knob_x = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.w))
            self.value = self.get_value_from_knob(self.knob_x)

    def draw(self, screen, track_color=(100,100,100), knob_color=(200,0,0)):
        pygame.draw.rect(screen, track_color, self.rect)
        pygame.draw.circle(screen, knob_color, (self.knob_x, self.rect.centery), self.knob_radius)
        value_text = str(round(self.value,3))
        if self.percent:
            value_text += "%"
        text_surf = self.font.render(value_text, True, white)
        text_rect = text_surf.get_rect(center=(self.knob_x, self.rect.centery))
        screen.blit(text_surf, text_rect)


class ToggleSwitch:
    def __init__(self, x, y, w, h, initial_state=False, label_default="OFF", label_secondary="ON"):
        self.rect = pygame.Rect(x, y, w, h)
        self.state = initial_state
        self.knob_radius = h // 2 - 2
        self.font = pygame.font.SysFont("consolas", 20)
        self.label_default = label_default
        self.label_secondary = label_secondary

    def handle_event(self, event):
        if event == None:
            None
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.state = not self.state

    def draw(self, screen, on_color=(200,0,0), off_color=(100,100,100), knob_color=(220,220,220)):
        color = on_color if self.state else off_color
        pygame.draw.rect(screen, color, self.rect, border_radius=self.rect.height//2)
        knob_x = self.rect.right - self.rect.height//2 if self.state else self.rect.left + self.rect.height//2
        knob_center = (knob_x, self.rect.centery)
        pygame.draw.circle(screen, knob_color, knob_center, self.knob_radius)
        label = self.label_secondary if self.state else self.label_default
        text_surf = self.font.render(label, True, white)
        text_rect = text_surf.get_rect(center=(self.rect.centerx, self.rect.centery))
        screen.blit(text_surf, text_rect)