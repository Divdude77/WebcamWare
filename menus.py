import pygame

from cv import *
from functions import draw_body_outline
from games.games import *
import random
from components import *


class Menu:
    def __init__(self, screen):
        self.screen = screen

    def draw(self):
        pass

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                exit()


class HomeMenu(Menu):
    def __init__(self, screen):
        super().__init__(screen)
        self.options = ["Start Game", "Options", "Quit"]
        self.selected_option = 0

    def draw(self):
        self.screen.fill((0, 0, 0))
        
        font = pygame.font.Font(None, 60)
        text = font.render("WebcamWare", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.screen.get_width() // 2, 80))
        self.screen.blit(text, text_rect)

        # Draw the menu options
        font = pygame.font.Font(None, 36)
        for i, option in enumerate(self.options):
            text = font.render(option, True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.screen.get_width() // 2, 200 + i * 30))
            self.screen.blit(text, text_rect)

            # Highlight the selected option
            if i == self.selected_option:
                pygame.draw.rect(self.screen, (255, 0, 0), text_rect, 2)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                if self.selected_option == 0:
                    return SetupMenu(self.screen)  # Return GameMenu instance if option 0 is selected
                elif self.selected_option == 2:
                    pygame.quit()
                    exit()


class GameMenu(Menu):
    def __init__(self, screen):
        super().__init__(screen)
        self.surface = pygame.Surface((20, 10))
        self.surface.fill((255, 255, 255))
        self.surface_coords = (0, 0)
        self.pose_estimator = PoseEstimator()
        self.web_cam = WebCam()
        self.web_cam.startWebcam()

    def draw(self):
        self.screen.fill((0, 0, 0))  # Fill the screen with black color

        font = pygame.font.Font(None, 36)
        text = font.render("Game Menu", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
        self.screen.blit(text, text_rect)
        
        wrist_landmark = self.pose_estimator.getPoints(self.web_cam.returnFrame(), [16])
        if wrist_landmark:
            wrist_landmark = wrist_landmark[16]
            if wrist_landmark.visibility > 0.5:
                self.screen.blit(self.surface, (int(wrist_landmark.x * self.screen.get_width()), int(wrist_landmark.y * self.screen.get_height())))


class SetupMenu(Menu):
    def __init__(self, screen):
        self.pose_estimator = PoseEstimator()
        self.hand_estimator = HandEstimator()
        self.web_cam = WebCam()
        self.web_cam.startWebcam()
        self.screen = screen
        self.body_visible = False
        self.hands_visible = False
    
    def draw(self):
        frame = self.web_cam.returnFrame()
        body_landmarks = self.pose_estimator.getPoints(frame, [0, 11, 12, 13, 14, 15, 16, 23, 24])
        hand_landmarks = self.hand_estimator.getPoints(frame, [12])

        self.screen.fill((0, 0, 0))

        if body_landmarks:
            if body_landmarks[11].visibility > 0.5 and body_landmarks[12].visibility > 0.5 and body_landmarks[13].visibility > 0.5 and body_landmarks[14].visibility > 0.5 and body_landmarks[15].visibility > 0.5 and body_landmarks[16].visibility > 0.5 and body_landmarks[23].visibility > 0.5 and body_landmarks[24].visibility > 0.5 and body_landmarks[0].visibility > 0.5:
                self.body_visible = True
                draw_body_outline(self.screen, body_landmarks, 0, 0, self.screen.get_width(), self.screen.get_height())

            else:
                self.body_visible = False
                font = pygame.font.Font(None, 36)
                text = font.render("Body not visible! Kindly move backwards.", True, (255, 255, 255))
                text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
                self.screen.blit(text, text_rect)
            
        else:
            self.body_visible = False
            font = pygame.font.Font(None, 36)
            text = font.render("No body detected.", True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
            self.screen.blit(text, text_rect)
        
        if hand_landmarks and self.body_visible:
            if len(hand_landmarks) == 2:
                self.hands_visible = True
            else:
                self.hands_visible = False
                font = pygame.font.Font(None, 36)
                text = font.render("Both hands not visible!", True, (255, 255, 255))
                text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
                self.screen.blit(text, text_rect)

        elif self.body_visible:
            self.hands_visible = False
            font = pygame.font.Font(None, 36)
            text = font.render("Both hands not visible!", True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
            self.screen.blit(text, text_rect)

        if self.body_visible and self.hands_visible:
            l_shoulder_angle, r_shoulder_angle = abs(self.pose_estimator.getAngle(body_landmarks, 13, 11, 23)), abs(self.pose_estimator.getAngle(body_landmarks, 14, 12, 24))
            l_elbow_angle, r_elbow_angle = abs(self.pose_estimator.getAngle(body_landmarks, 11, 13, 15)), abs(self.pose_estimator.getAngle(body_landmarks, 12, 14, 16))
            
            if  170 < l_shoulder_angle and l_shoulder_angle < 190 and 170 < r_shoulder_angle and r_shoulder_angle < 190 and \
                160 < l_elbow_angle and l_elbow_angle < 200 and 160 < r_elbow_angle and r_elbow_angle < 200:
                # Return GameRunner instance if all conditions are met
                pass

            else:
                font = pygame.font.Font(None, 36)
                text = font.render("Raise your hands above your head!", True, (255, 255, 255))
                text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
                self.screen.blit(text, text_rect)


class GameOverMenu(Menu):
    def __init__(self, screen):
        super().__init__(screen)
        self.text = AnimatedText("Game Over", self.screen.get_width() // 2, self.screen.get_height() // 2, self.screen, font_size=128, primary_color=(255, 255, 255), outline_color=(0, 0, 0), outline=5)
    
    def draw(self):
        self.screen.fill((255, 0, 0))
        self.text.draw()


class InterGameMenu(Menu):
    def __init__(self, screen):
        super().__init__(screen)
        self.lives = [120] * 3
        self.life = 2
        self.life_img = pygame.image.load("assets/img/lives/webcam.png").convert_alpha()
        self.background = pygame.transform.scale(pygame.image.load("assets/img/lives/background.png"), (self.screen.get_width(), self.screen.get_height()))
        self.frame = pygame.transform.scale(pygame.image.load("assets/img/lives/frame.png").convert_alpha(), (self.screen.get_width(), self.screen.get_height()))
        self.skull = pygame.image.load("assets/img/lives/skull.png").convert_alpha()
        self.timer = Timer(2, screen)
        self.life_lost = False
        self.font = pygame.font.Font("assets/fonts/easvhs.ttf", 108)

    def draw(self, game_won, snapshot):
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(snapshot, (self.screen.get_width() // 2.01 - snapshot.get_width() // 2, 5 * self.screen.get_height() // 6 - snapshot.get_height() // 2))
        self.screen.blit(self.frame, (0, 0))

        if self.life >= -1:
            text = self.font.render(str(self.life + 1), True, (0, 255, 0))
            if self.life == -1:
                text = self.font.render(str(self.life + 1), True, (255, 0, 0))
            text_rect = text.get_rect(center=(self.screen.get_width() // 1.13 , self.screen.get_height() // 5.7))
            self.screen.blit(text, text_rect)
        
        else:
            self.screen.blit(self.skull, (self.screen.get_width() // 1.13 - 60, self.screen.get_height() // 5.7 - 60))

        secs = self.timer.tick()

        if secs > 0.5:
            if not game_won and game_won is not None and not self.life_lost:
                if self.lives[self.life] > 0:
                    self.lives[self.life] -= 2
                
                else:
                    self.life -= 1
                    self.life_lost = True
                
        self.draw_lives()

        if secs >= self.timer.time:
            self.life_lost = False
            self.timer.reset()
            return True

    def draw_lives(self):
        if self.lives[0] != 0:
            if self.lives[0] < 120:
                self.screen.blit(pygame.transform.scale(self.life_img, (self.lives[0], self.lives[0])), (self.screen.get_width() // 2 - self.lives[0] // 2, self.screen.get_height() // 2 - self.lives[0] // 2))
            else:
                self.screen.blit(self.life_img, (self.screen.get_width() // 2 - 60, self.screen.get_height() // 2 - 60))
        
        if self.lives[1] != 0:
            if self.lives[1] < 120:
                self.screen.blit(pygame.transform.scale(self.life_img, (self.lives[1], self.lives[1])), (self.screen.get_width() // 4 - self.lives[1] // 2, self.screen.get_height() // 2 - self.lives[1] // 2))
            else:
                self.screen.blit(self.life_img, (self.screen.get_width() // 4 - 60, self.screen.get_height() // 2 - 60))

        if self.lives[2] != 0:
            if self.lives[2] < 120:
                self.screen.blit(pygame.transform.scale(self.life_img, (self.lives[2], self.lives[2])), (3 * self.screen.get_width() // 4 - self.lives[2] // 2, self.screen.get_height() // 2 - self.lives[2] // 2))
            else:
                self.screen.blit(self.life_img, (3 * self.screen.get_width() // 4 - 60, self.screen.get_height() // 2 - 60))


class GameRunner(Menu):
    def __init__(self, screen):
        super().__init__(screen)
        self.speed = 1
        self.games = [ClearTheFog]
        self.inter_game_menu = InterGameMenu(screen)
        self.current_game = None
        self.current_game_won = None
        self.snapshot = pygame.surface.Surface((self.screen.get_width() // 4, self.screen.get_height() // 4))
        self.snapshot.fill((255, 255, 255))

    def draw(self):
        if not self.current_game:
            if self.inter_game_menu.draw(self.current_game_won, self.snapshot):
                if self.inter_game_menu.life < -1:
                    return GameOverMenu(self.screen)
                
                self.current_game = self.games[random.randint(0, len(self.games)-1)](self.screen, self.speed)
                self.current_game_won = False

        elif self.current_game.draw():
            frame = cv2.rotate(cv2.cvtColor(self.current_game.snapshot, cv2.COLOR_BGR2RGB), cv2.ROTATE_90_COUNTERCLOCKWISE)
            self.snapshot = pygame.transform.scale(pygame.surfarray.make_surface(frame), (self.screen.get_width() // 4, self.screen.get_height() // 4))
            self.current_game_won = self.current_game.won
            self.current_game = None
