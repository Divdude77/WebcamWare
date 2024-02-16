import pygame

from cv import *
from draw import draw_body_outline
from components import *
import random


class Game:
    def __init__(self, screen, speed):
        self.screen = screen
        self.speed = speed

    def draw(self):
        pass

    def handle_event(self, event):
        pass

class HoleInTheWall(Game):
    def __init__(self, screen, speed):
        super().__init__(screen, speed)
        self.pose_estimator = PoseEstimator()
        self.web_cam = WebCam()
        self.web_cam.startWebcam()
        self.timer = Timer(5, screen)

        self.angles = [[90, 270, 90, 270], [90, 270, 180, 180]]
        self.walls = [pygame.image.load("assets/img/walls/wall1.png").convert_alpha(), pygame.image.load("assets/img/walls/wall2.png").convert_alpha(), pygame.image.load("assets/img/walls/wall3.png").convert_alpha()]
        self.background = pygame.transform.scale(pygame.image.load("assets/img/walls/background.png"), (self.screen.get_width(), self.screen.get_height()))
        self.wall = random.randint(0, 1)   
        self.wall_scale = 0.3

        self.shoulders_locked = False
        self.elbows_locked = False
        self.won = False
        self.running = True
        
        self.entry_text = AnimatedText("Dodge!", self.screen.get_width() // 2, self.screen.get_height() // 2, self.screen, 72, (0, 0, 0), (255, 255, 255), 3, 0.5)

        self.back = pygame.transform.scale(pygame.image.load("assets/img/body/back.png").convert_alpha(), (250, 300))
        self.upper_arm = pygame.transform.scale(pygame.image.load("assets/img/body/upperarm.png").convert_alpha(), (200, 200))
        self.lower_arm = pygame.transform.scale(pygame.image.load("assets/img/body/lowerarm.png").convert_alpha(), (200, 200))

    def rotate(self, surface, angle, pivot):
        offset = pygame.math.Vector2(0, surface.get_height() // 2)
        rotated_image = pygame.transform.rotozoom(surface, -angle, 1)
        rotated_offset = offset.rotate(angle)  
        rect = rotated_image.get_rect(center=pivot+rotated_offset)
        return rotated_image, rect
    
    def find_elbow(self, shoulder_coords, angle, distance):
        if angle < 180:
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
                if self.won:
                    font = pygame.font.Font(None, 36)
                    text = font.render("You won!", True, (0, 0, 0))
                    text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
                    self.screen.blit(text, text_rect)
                    if self.timer.tick() - self.timer.time >= 1.5:
                        return True
                
                else:
                    font = pygame.font.Font(None, 36)
                    text = font.render("You lost.", True, (0, 0, 0))
                    text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
                    self.screen.blit(text, text_rect)
                    if self.timer.tick() - self.timer.time >= 1.5:
                        return True

        draw_body_outline(self.screen, body_landmarks, 25, 25, 100, 75)

    def draw_body(self, body_landmarks):
        # Create body
        body_coords = (self.screen.get_width() // 2 - self.back.get_width() // 2, self.screen.get_height() // 1.5) 

        # Draw head
        pygame.draw.circle(self.screen, (0, 0, 0), (self.screen.get_width() // 2, self.screen.get_height() // 1.75), 50)

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
