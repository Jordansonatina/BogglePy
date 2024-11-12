from dice import Dice
import random
import pygame
import enchant

class Boggle:
    def __init__(self):
        # pygame setup
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load('music.mp3')
        self.click_sound = pygame.mixer.Sound('click.mp3')
        self.correct_sound = pygame.mixer.Sound('correct.mp3')
        self.wrong_sound = pygame.mixer.Sound('wrong.mp3')
        self.click_sound.set_volume(0.25)
        self.correct_sound.set_volume(0.25)
        self.wrong_sound.set_volume(0.15)
        pygame.mixer.music.set_volume(.5)
        pygame.mixer.music.play(-1)
        self.board_width = 600
        self.board_height = 600
        self.window_width = self.board_width + 400
        self.window_height = self.board_height
        self.dim = 4
        self.tile_size = self.board_width // self.dim
        self.boggle_dice = {
            0: "AAEEGN",
            1: "ABBJOO",
            2: "ACHOPS",
            3: "AFFKPS",
            4: "AOOTTW",
            5: "CIMOTU",
            6: "DEILRX",
            7: "DELRVY",
            8: "DISTTY",
            9: "EEGHNW",
            10: "EEINSU",
            11: "EHRTVW",
            12: "EIOSST",
            13: "ELRTTY",
            14: "HIMNQU",
            15: "HLNNRZ"
        }
        self.die = [Dice() for i in range(self.dim*self.dim)]
        self.randomize_die()
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption('Boggle')
        self.clock = pygame.time.Clock()
        self.running = True
        self.font_size = self.tile_size
        self.font_size_messages = 25
        self.font = pygame.font.Font(None, self.font_size)
        self.font_messages = pygame.font.Font(None, self.font_size_messages)

        self.word = ''
        self.creating_word = False
        self.words = []
        self.points = 0
        self.dictionary = enchant.Dict('en_US')
        self.messages = []
        self.last_selected = ()
        self.using_mouse_controls = False
        self.mouse_pos = ()
        self.space_held_down = False

        # Colors
        self.background_color = (255, 255, 255)
        self.tile_color = (255, 255, 255)  # Light Gray
        self.tile_hovered_color = (255, 0, 0)
        self.tile_selected_color = (0, 255, 0)
        self.tile_last_selected_color = (255, 255, 0)
        self.text_color = (0, 0, 0)  # Black

        self.hovered_row = 0
        self.hovered_col = 0

        self.main_loop()

    def handle_events(self):
        self.mouse_pos = pygame.mouse.get_pos()
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.MOUSEMOTION:
                self.using_mouse_controls = True

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.tile_clicked_action()


            if event.type == pygame.KEYDOWN:
                self.using_mouse_controls = False

                if event.key == pygame.K_RIGHT:
                    if self.hovered_col < self.dim-1:
                        self.hovered_col += 1
                if event.key == pygame.K_LEFT:
                    if self.hovered_col > 0:
                        self.hovered_col -= 1
                if event.key == pygame.K_DOWN:
                    if self.hovered_row < self.dim-1:
                        self.hovered_row += 1
                if event.key == pygame.K_UP:
                    if self.hovered_row > 0:
                        self.hovered_row -= 1
                if event.key == pygame.K_SPACE:
                    self.tile_clicked_action()

    def tile_clicked_action(self):
        index = self.get_index_from_pos(self.hovered_row, self.hovered_col)

        if self.die[index].is_selected:
            if self.is_valid_word():
                self.correct_sound.play()
                self.words.append(self.word)
                print(self.word + ' was a word! You got ' + str(self.calculate_points()) + ' point(s).')
                self.messages.append(self.word + ' was a word! You got ' + str(self.calculate_points()) + ' point(s).')
                self.points += self.calculate_points()
                print('Your current score is ' + str(self.points))
                self.messages.append('Your current score is ' + str(self.points))
            else:
                self.wrong_sound.play()
            self.last_selected = (10, 10)
            self.creating_word = False
            self.word = ''
            self.reset_dice_selection()
        else:
            if self.creating_word is False:
                self.last_selected = (self.hovered_row, self.hovered_col)
            self.creating_word = True
            print(self.get_pos_from_index(index))
            print(self.last_selected)
            if self.is_streamed_letter(index):
                self.last_selected = (self.hovered_row, self.hovered_col)
                self.click_sound.play()
                self.word += self.die[index].letter
                self.die[index].is_selected = True

    def is_streamed_letter(self, index):
        pos = self.get_pos_from_index(index) # pos of selection
        if self.last_selected[0] - 1 <= pos[0] <= self.last_selected[0] + 1 and self.last_selected[1] - 1 <= pos[1] <= self.last_selected[1] + 1:
            return True
        return False

    def calculate_points(self):
        if 3 <= len(self.word) <= 4:
            return 1
        if len(self.word) == 5:
            return 2
        if len(self.word) == 6:
            return 3
        if len(self.word) == 7:
            return 5
        if len(self.word) >= 8:
            return 11


    def reset_dice_selection(self):
        for dice in self.die:
            dice.is_selected = False

    def is_valid_word(self):
        if len(self.word) < 3:
            print(self.word + ' had an insufficient amount of letters.')
            self.messages.append(self.word + ' had an insufficient amount of letters.')
            return False
        if self.word in self.words:
            print(self.word + ' was already used.')
            self.messages.append(self.word + ' was already used.')
            return False
        if not self.dictionary.check(self.word):
            print(self.word + ' is not a word.')
            self.messages.append(self.word + ' is not a word.')
            return False
        return True

    def render_graphics(self):
        # fill the screen with a color to wipe away anything from last frame
        self.screen.fill(self.background_color)
        self.draw_board()
        self.draw_messages()

        # do stuff then flip screen
        pygame.display.flip()

    def main_loop(self):
        while self.running:
            self.handle_events()
            self.render_graphics()

            if self.using_mouse_controls:
                self.hovered_row = self.mouse_pos[1] // self.tile_size
                self.hovered_col = self.mouse_pos[0] // self.tile_size

            for i in range(self.dim*self.dim):
                if self.get_pos_from_index(i)[0] == self.hovered_row and self.get_pos_from_index(i)[1] == self.hovered_col:
                    self.die[i].is_hovered = True
                else:
                    self.die[i].is_hovered = False

            self.clock.tick(60)  # limits FPS to 60
        pygame.quit()

    def randomize_die(self):
        for i in range(self.dim*self.dim):
            # choose random letter or 'face' of dice
            random_letter = random.choice(self.boggle_dice[i])
            random_die_index = random.randint(0, self.dim*self.dim-1)
            while not self.die[random_die_index].letter == '.':
                random_die_index = random.randint(0, self.dim * self.dim - 1)
            self.die[random_die_index].letter = random_letter

    def get_pos_from_index(self, index):
        return index // self.dim, index % self.dim

    def get_index_from_pos(self, row, col):
        return row * self.dim + col


    # Draw the board
    def draw_board(self):
        for i in range(len(self.die)):
            current_dice = self.die[i]
            row = i // self.dim
            col = i % self.dim

            x = col * self.tile_size
            y = row * self.tile_size

            # Draw the tile
            if current_dice.is_selected:
                if row == self.last_selected[0] and col == self.last_selected[1]:
                    pygame.draw.rect(self.screen, self.tile_last_selected_color, (x, y, self.tile_size, self.tile_size))
                else:
                    pygame.draw.rect(self.screen, self.tile_selected_color, (x, y, self.tile_size, self.tile_size))
            elif current_dice.is_hovered:
                pygame.draw.rect(self.screen, self.tile_hovered_color, (x, y, self.tile_size, self.tile_size))
            else:
                pygame.draw.rect(self.screen, self.tile_color, (x, y, self.tile_size, self.tile_size))
            pygame.draw.rect(self.screen, self.text_color, (x, y, self.tile_size, self.tile_size), 4)  # Outline

            # Render the letter text
            text_surface = self.font.render(current_dice.letter, True, self.text_color)
            text_rect = text_surface.get_rect(center=(x + self.tile_size // 2, y + self.tile_size // 2))

            # Draw the text on the tile
            self.screen.blit(text_surface, text_rect)

    # Draw message box
    def draw_messages(self):

        for i in range(len(self.messages)):
            box_rect = pygame.Rect(self.board_width, 0, self.window_width-self.board_width, self.window_height)
            text_surface = self.font_messages.render(self.messages[len(self.messages)-1-i], True, self.text_color)
            text_rect = text_surface.get_rect()
            text_rect.topleft = (box_rect.x, self.window_height - self.font_size_messages - i*self.font_size_messages)
            self.screen.blit(text_surface, text_rect)






