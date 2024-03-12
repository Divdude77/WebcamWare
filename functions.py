import pygame

def draw_body_outline(screen, body_landmarks, x, y, w, h):
    if body_landmarks:
        pygame.draw.line(screen, (255, 0, 0), (int(body_landmarks[11].x * w) + x, int(body_landmarks[11].y * h) + y), (int(body_landmarks[12].x * w) + x, int(body_landmarks[12].y * h) + y))
        pygame.draw.line(screen, (255, 0, 0), (int(body_landmarks[11].x * w) + x, int(body_landmarks[11].y * h) + y), (int(body_landmarks[23].x * w) + x, int(body_landmarks[23].y * h) + y))
        pygame.draw.line(screen, (255, 0, 0), (int(body_landmarks[12].x * w) + x, int(body_landmarks[12].y * h) + y), (int(body_landmarks[24].x * w) + x, int(body_landmarks[24].y * h) + y))
        pygame.draw.line(screen, (255, 0, 0), (int(body_landmarks[23].x * w) + x, int(body_landmarks[23].y * h) + y), (int(body_landmarks[24].x * w) + x, int(body_landmarks[24].y * h) + y))
        pygame.draw.line(screen, (255, 0, 0), (int(body_landmarks[11].x * w) + x, int(body_landmarks[11].y * h) + y), (int(body_landmarks[13].x * w) + x, int(body_landmarks[13].y * h) + y))
        pygame.draw.line(screen, (255, 0, 0), (int(body_landmarks[12].x * w) + x, int(body_landmarks[12].y * h) + y), (int(body_landmarks[14].x * w) + x, int(body_landmarks[14].y * h) + y))
        pygame.draw.line(screen, (255, 0, 0), (int(body_landmarks[13].x * w) + x, int(body_landmarks[13].y * h) + y), (int(body_landmarks[15].x * w) + x, int(body_landmarks[15].y * h) + y))
        pygame.draw.line(screen, (255, 0, 0), (int(body_landmarks[14].x * w) + x, int(body_landmarks[14].y * h) + y), (int(body_landmarks[16].x * w) + x, int(body_landmarks[16].y * h) + y))

def clamp(n, smallest, largest): return max(smallest, min(n, largest))