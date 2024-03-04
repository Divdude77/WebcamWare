import pygame

from cv import *
from draw import draw_body_outline
from components import *
import random


class Game:
    def __init__(self, screen, speed):
        self.screen = screen
        self.speed = speed
        self.won = False
        self.snapshot = None
        
        self.game_over_symbol = GameFinishSymbol(self.screen)

    def draw(self):
        pass

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                exit()

class HoleInTheWall(Game):
    def __init__(self, screen, speed):
        super().__init__(screen, speed)
        self.pose_estimator = PoseEstimator()
        self.web_cam = WebCam()
        self.web_cam.startWebcam()
        self.timer = Timer(5, screen)

        self.angles = [[90, 270, 90, 270], [90, 270, 180, 180], [180, 180, 180, 180], [180, 270, 180, 180], [90, 180, 180, 180]] # Left shoulder, Right shoulder, Left elbow, Right elbow
        self.walls = [pygame.image.load("assets/img/games/holeinthewall/walls/wall1.png").convert_alpha(), pygame.image.load("assets/img/games/holeinthewall/walls/wall2.png").convert_alpha(), pygame.image.load("assets/img/games/holeinthewall/walls/wall3.png").convert_alpha(), pygame.image.load("assets/img/games/holeinthewall/walls/wall4.png").convert_alpha(), pygame.image.load("assets/img/games/holeinthewall/walls/wall5.png").convert_alpha()]
        self.background = pygame.transform.scale(pygame.image.load("assets/img/games/holeinthewall/walls/background.png"), (self.screen.get_width(), self.screen.get_height()))
        self.wall = random.randint(0, 4)   
        self.wall_scale = 0.3

        self.shoulders_locked = False
        self.elbows_locked = False
        self.running = True
        
        self.entry_text = AnimatedText("Dodge!", self.screen.get_width() // 2, self.screen.get_height() // 2, self.screen, 72, (0, 0, 0), (255, 255, 255), 3, 0.5)

        self.head = pygame.image.load("assets/img/games/holeinthewall/body/head.png").convert_alpha()
        self.back = pygame.image.load("assets/img/games/holeinthewall/body/back.png").convert_alpha()
        self.upper_arm = pygame.image.load("assets/img/games/holeinthewall/body/upperarm.png").convert_alpha()
        self.lower_arm = pygame.image.load("assets/img/games/holeinthewall/body/lowerarm.png").convert_alpha()

    def rotate(self, surface, angle, pivot):
        offset = pygame.math.Vector2(0, surface.get_height() // 2)
        rotated_image = pygame.transform.rotozoom(surface, -angle, 1)
        rotated_offset = offset.rotate(angle)  
        rect = rotated_image.get_rect(center=pivot+rotated_offset)
        return rotated_image, rect
    
    def find_elbow(self, shoulder_coords, angle, distance):
        if angle == 180:
            return shoulder_coords[0], shoulder_coords[1] - distance
        
        if angle <= 180:
            distance = -distance

        angle_rad = math.radians(90 - angle)     # (90 - angle) is angle between arm and ground (x-axis).
        m = math.tan(angle_rad)    # Get slope of line

        x1, y1 = shoulder_coords
        x2 = (distance / math.sqrt(1 + m ** 2)) + x1       # Formula derived from distance formula and slope formula
        y2 = -(m * (x2 - x1)) + y1
        return x2, y2

    def draw(self):
        self.screen.blit(self.background, (0, 0))

        body_landmarks = self.pose_estimator.getPoints(self.web_cam.returnFrame(), [11, 12, 13, 14, 15, 16, 23, 24])

        if self.wall_scale <= 1:
            self.draw_wall()
            self.draw_body(body_landmarks)

        if self.wall_scale > 1:
            if self.wall_scale < 1.05: self.won = self.shoulders_locked and self.elbows_locked and self.running
    
            if self.won:
                self.draw_body(body_landmarks)
                self.draw_wall()
            
            else:
                self.running = False
                self.draw_wall(True)
                self.draw_body(body_landmarks)

        if self.entry_text.draw():
            if self.timer.draw():
                if self.snapshot is None:
                    self.snapshot = self.web_cam.returnFrame()

                self.game_over_symbol.draw(self.won)
                if self.timer.tick() - self.timer.time >= 1.5:
                    return True

        draw_body_outline(self.screen, body_landmarks, 25, 25, 100, 75)

    def draw_body(self, body_landmarks):
        # Create body
        body_coords = (self.screen.get_width() // 2 - self.back.get_width() // 2, self.screen.get_height() // 1.5) 

        # Draw shoulders
        surface_shoulers = ((body_coords[0] + 40, self.screen.get_height() // 1.5 + 40), (body_coords[0] + self.back.get_width() - 40, self.screen.get_height() // 1.5 + 40))  # 40 -> offset into body

        # Draw upper arms
        l_shoulder_angle = self.pose_estimator.getAngle(body_landmarks, 23, 11, 13) or 0
        if abs(l_shoulder_angle - self.angles[self.wall][0]) < 15:
            l_shoulder_angle = self.angles[self.wall][0]
        
        r_shoulder_angle = self.pose_estimator.getAngle(body_landmarks, 24, 12, 14) or 0
        if abs(r_shoulder_angle - self.angles[self.wall][1]) < 15:
            r_shoulder_angle = self.angles[self.wall][1]

        self.shoulders_locked = l_shoulder_angle == self.angles[self.wall][0] and r_shoulder_angle == self.angles[self.wall][1]
    
        self.draw_upper_arms(l_shoulder_angle, r_shoulder_angle, surface_shoulers)

        # Draw lower arms
        self.draw_lower_arms(body_landmarks, surface_shoulers, l_shoulder_angle, r_shoulder_angle)

        # Draw body
        self.screen.blit(self.back, (self.screen.get_width() // 2 - self.back.get_width() // 2, self.screen.get_height() // 1.5))   

        # Draw head
        self.screen.blit(self.head, (self.screen.get_width() // 2 - self.head.get_width() // 2, self.screen.get_height() // 1.5 - self.head.get_height() + 30))

    def draw_upper_arms(self, l_shoulder_angle, r_shoulder_angle, surface_shoulers):
        # Left
        u_l_arm = self.upper_arm
        rot_surf, rot_rect = self.rotate(u_l_arm, l_shoulder_angle, surface_shoulers[0])
        self.screen.blit(rot_surf, rot_rect)

        # Right
        u_r_arm = pygame.transform.flip(self.upper_arm, True, False)
        rot_surf, rot_rect = self.rotate(u_r_arm, r_shoulder_angle, surface_shoulers[1])
        self.screen.blit(rot_surf, rot_rect)

    def draw_lower_arms(self, body_landmarks, surface_shoulers, l_shoulder_angle, r_shoulder_angle):
        # Left
        l_elbow_angle = self.pose_estimator.getAngle(body_landmarks, 15, 13, 11) or 0
        l_elbow_locked = False
        if abs(l_elbow_angle - self.angles[self.wall][2]) < 15 and self.shoulders_locked:
            l_elbow_angle = self.angles[self.wall][2]
            l_elbow_locked = True

        l_l_arm = self.lower_arm
        if l_shoulder_angle > 180:
            l_elbow_angle -= (l_shoulder_angle - 180)
        else:
            l_elbow_angle = l_elbow_angle + 180 - l_shoulder_angle

        elbow_coords = self.find_elbow(surface_shoulers[0], l_shoulder_angle, 200)
        rot_surf, rot_rect = self.rotate(l_l_arm, -l_elbow_angle, elbow_coords)
        pygame.draw.circle(self.screen, (166, 166, 166), elbow_coords, 30)
        self.screen.blit(rot_surf, rot_rect)

        # Right
        r_elbow_angle = self.pose_estimator.getAngle(body_landmarks, 16, 14, 12) or 0
        r_elbow_locked = False

        if abs(r_elbow_angle - self.angles[self.wall][3]) < 15 and self.shoulders_locked:
            r_elbow_angle = self.angles[self.wall][3]
            r_elbow_locked = True

        r_l_arm = pygame.transform.flip(self.lower_arm, True, False)
        if r_shoulder_angle > 180:
            r_elbow_angle -= (r_shoulder_angle - 180)
        else:
            r_elbow_angle = r_elbow_angle + 180 - r_shoulder_angle
        
        self.elbows_locked = l_elbow_locked and r_elbow_locked

        elbow_coords = self.find_elbow(surface_shoulers[1], r_shoulder_angle, 200)
        rot_surf, rot_rect = self.rotate(r_l_arm, -r_elbow_angle, elbow_coords)
        pygame.draw.circle(self.screen, (166, 166, 166), elbow_coords, 30)
        self.screen.blit(rot_surf, rot_rect)

    def draw_wall(self, stop=False):
        w, h = self.screen.get_width(), self.screen.get_height()
        
        if not stop:
            self.wall_scale = self.timer.get_ratio() * 0.75 + 0.3

        if self.wall_scale >= 1.05:
            return

        self.screen.blit(pygame.transform.scale(self.walls[self.wall], (int(w * self.wall_scale), int(h * self.wall_scale))).convert_alpha(), ((1-self.wall_scale)/2 * w, (1-self.wall_scale)/2 * h))


class ClearTheFog(Game):
    def __init__(self, screen, speed):
        super().__init__(screen, speed)
        self.pose_estimator = PoseEstimator()
        self.web_cam = WebCam()
        self.web_cam.startWebcam()
        self.timer = Timer(10, screen)

        self.background = pygame.transform.scale(pygame.image.load("assets/img/games/clearthefog/background.png"), (self.screen.get_width(), self.screen.get_height()))
        self.hand_l = pygame.transform.scale(pygame.image.load("assets/img/games/clearthefog/hand_l.png").convert_alpha(), (75, 100))
        self.hand_r = pygame.transform.scale(pygame.image.load("assets/img/games/clearthefog/hand_r.png").convert_alpha(), (75, 100))
        self.fog = pygame.transform.scale(pygame.image.load("assets/img/games/clearthefog/fog.png").convert_alpha(), (200, 200))

        self.prev_l = None
        self.prev_r = None

        self.fogs = {}
        self.grid_size = self.screen.get_width() // 10
        grid = [(i,j) for i in range(0, self.screen.get_width()-self.grid_size, self.grid_size) for j in range(0, self.screen.get_height()-self.grid_size, self.grid_size)]

        while grid:
            i = random.choice(grid)
            grid.remove(i)
            if random.choice([0, 1, 1]):
                self.fogs[i] = [i[0] + self.grid_size // 2 - self.fog.get_width() // 2, i[1] + self.grid_size // 2 - self.fog.get_height() // 2, 200]

        self.entry_text = AnimatedText("Clear!", self.screen.get_width() // 2, self.screen.get_height() // 2, self.screen, 72, (0, 0, 0), (255, 255, 255), 3, 0.5)
        self.win_time = None

    def get_adjusted_landmarks(self, body_landmarks):
        if not body_landmarks: return None, None

        l_x = (2 * min(max(body_landmarks[15].x, 0.25), 0.75) - 0.5) * self.screen.get_width() - self.hand_l.get_width() // 2
        l_y = (2 * min(max(body_landmarks[15].y, 0.5), 1) - 1) * self.screen.get_height() - self.hand_l.get_height() // 2
        r_x = (2 * min(max(body_landmarks[16].x, 0.25), 0.75) - 0.5) * self.screen.get_width() - self.hand_r.get_width() // 2
        r_y = (2 * min(max(body_landmarks[16].y, 0.5), 1) - 1) * self.screen.get_height() - self.hand_r.get_height() // 2

        return (l_x, l_y), (r_x, r_y)

    def draw(self):
        body_landmarks = self.pose_estimator.getPoints(self.web_cam.returnFrame(), [11, 12, 13, 14, 15, 16, 23, 24])
        adjusted_body_landmarks = self.get_adjusted_landmarks(body_landmarks)

        self.screen.blit(self.background, (0, 0))
        self.draw_fog()
        self.draw_hand(adjusted_body_landmarks)

        if self.entry_text.draw():
            if self.timer.draw() or self.won:
                if self.snapshot is None:
                    self.snapshot = self.web_cam.returnFrame()
                self.game_over_symbol.draw(self.won)

                if not self.win_time: self.win_time = self.timer.tick()

                if self.timer.tick() - self.win_time >= 1.5:
                    return True
            
            else:
                if all(adjusted_body_landmarks):
                    l, r = adjusted_body_landmarks
                    hand_l = (l[0] // self.grid_size * self.grid_size, l[1] // self.grid_size * self.grid_size)
                    hand_r = (r[0] // self.grid_size * self.grid_size, r[1] // self.grid_size * self.grid_size)
    
                    if hand_l != self.prev_l:
                        self.prev_l = hand_l
                        if hand_l in self.fogs:
                            if self.fogs[hand_l][2] > 0:
                                self.fogs[hand_l][2] -= 200
                                if self.fogs[hand_l][2] == 0:
                                    del self.fogs[hand_l]
                    
                    if hand_r != self.prev_r:
                        self.prev_r = hand_r
                        if hand_r in self.fogs:
                            if self.fogs[hand_r][2] > 0:
                                self.fogs[hand_r][2] -= 200
                                if self.fogs[hand_r][2] == 0:
                                    del self.fogs[hand_r]

        draw_body_outline(self.screen, body_landmarks, 25, 25, 100, 75)

        if not self.fogs and not self.won:
            self.won = True
            self.win_time = self.timer.tick()

    def draw_fog(self):
        for i in self.fogs:
            self.fog.set_alpha(self.fogs[i][2])
            self.screen.blit(self.fog, self.fogs[i][:2])
            # pygame.draw.rect(self.screen, (255, 0, 0), (i[0], i[1], self.grid_size, self.grid_size), 2)      # Grid

    def draw_hand(self, adjusted_body_landmarks):
        hand_l_coords, hand_r_coords = adjusted_body_landmarks
        
        if not all(adjusted_body_landmarks):
            return

        self.screen.blit(self.hand_l, hand_l_coords)
        self.screen.blit(self.hand_r, hand_r_coords)