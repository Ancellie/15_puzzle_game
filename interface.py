import pygame
import time
from pygame.locals import *
from game import Game, save_board_to_file
from solver import Solver
import threading


class Button:
    def __init__(self, text, rect, font, fg_color, bg_color, callback):
        self.text = text  # Текст кнопки
        self.rect = rect  # Прямокутник, який представляє кнопку
        self.font = font  # Шрифт кнопки
        self.fg_color = fg_color  # Колір тексту кнопки
        self.bg_color = bg_color  # Колір фону кнопки
        self.callback = callback  # Функція зворотного виклику, яка виконується при натисканні кнопки
        self.running = True  # Прапорець, що вказує, чи триває робота кнопки

    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect)  # Відображення фону кнопки
        text_surface = self.font.render(self.text, True, self.fg_color)  # Створення поверхні з текстом кнопки
        text_rect = text_surface.get_rect(center=self.rect.center)  # Вирівнювання тексту кнопки по центру прямокутника кнопки
        surface.blit(text_surface, text_rect)  # Відображення тексту кнопки на екрані

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:  # Перевірка на натискання кнопки мишею
            if self.rect.collidepoint(event.pos):  # Перевірка, чи позиція натискання знаходиться в межах прямокутника кнопки
                self.callback()  # Виклик функції
                return True
        return False


class GameWindow:
    TILE_SIZE = 100  # Розмір одного пазла
    BOARD_SIZE = TILE_SIZE * 4 + 10  # Розмір дошки
    WINDOW_SIZE = (BOARD_SIZE + 120, BOARD_SIZE + 220)  # Розмір вікна
    FPS = 60  # Кількість кадрів на секунду для оновлення графіки

    def create_tiles(self, board):
        tiles = []
        for row in range(len(board.board)):
            for col in range(len(board.board[row])):
                tile_rect = pygame.Rect(
                    col * (self.TILE_SIZE + 7) + 50 + (self.BOARD_SIZE - self.TILE_SIZE  * self.game.size) // 1.5,
                    row * (self.TILE_SIZE + 7) + 10 + (self.BOARD_SIZE - self.TILE_SIZE  * self.game.size) // 1.5,
                    self.TILE_SIZE,
                    self.TILE_SIZE
                )

                if board.board[row][col] != 0:
                    tile_surface = pygame.font.Font(None, 36).render(str(board.board[row][col]), True, (255, 255, 255))
                    tile_color = (255, 178, 102)
                else:
                    tile_surface = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE))
                    tile_surface.fill((128, 128, 128))
                    tile_color = (0, 0, 0)
                tiles.append((tile_surface, tile_rect, tile_color))
        return tiles

    def __init__(self):
        self.game = Game(size=4)  # Створення об'єкту гри
        self.board = self.game.puzzle  # Отримання початкової дошки гри
        self.empty_row = self.game.empty_row  # Рядок порожньої плитки
        self.empty_col = self.game.empty_col  # Стовпець порожньої плитки
        self.font = pygame.font.SysFont('arial', 40)  # Шрифт для тексту на плитках
        self.tiles = self.create_tiles(self.board)  # Створення плиток для відображення на дошці
        self.window = pygame.display.set_mode(self.WINDOW_SIZE)  # Створення вікна гри
        pygame.display.set_caption("15 Puzzle")  # Встановлення заголовку вікна
        self.buttons = self.create_buttons()  # Створення кнопок
        self.running = True  # Прапорець, що вказує, чи триває гра
        self.solve_running = False  # Прапорець, що вказує, чи триває робота алгоритму розв'язку

    def new_game(self):
        self.game = Game(size=4, shuffle_steps=40)  # Створення нової гри з перемішаними пазлами
        self.game.shuffle_board()  # Перемішування пазлів на дошці
        self.board = self.game.puzzle  # Отримання нової дошки гри
        self.empty_row = self.game.empty_row  # Оновлення рядка порожньої плитки
        self.empty_col = self.game.empty_col  # Оновлення стовпця порожньої плитки
        self.tiles = self.create_tiles(self.board)  # Створення плиток для відображення на дошці
        self.draw_board()  # Оновлення відображення дошки

    def solve_game(self):
        if self.solve_running or self.game.is_solved():  # Перевірка, чи алгоритм розв'язку вже працює
            return

        def solve_algorithm():
            self.solve_running = True  # Встановлення прапорця, що вказує на роботу алгоритму розв'язку

            tic = time.perf_counter()  # Початок відліку часу
            p = Solver(self.board).solve()  # Запуск алгоритму розв'язку
            toc = time.perf_counter()  # Кінець відліку часу

            steps = 0
            for node in p:
                print(node.action)  # Виведення дії, зробленої алгоритмом
                node.puzzle.pprint()  # Виведення поточного стану дошки
                steps += 1

                self.game.move(node.action)  # Застосування дії до гри
                pygame.display.update()  # Оновлення відображення дошки
                self.update_tiles()  # Оновлення плиток на дошці
                pygame.time.wait(100)  # Затримка для плавності відображення

            print("Загальна кількість кроків: " + str(steps))
            print("Загальний час пошуку: " + str(toc - tic) + " секунд(и)")

            self.solve_running = False  # Скидання прапорця, коли алгоритм розв'язку закінчує роботу

        solve_thread = threading.Thread(target=solve_algorithm)  # Створення потоку для алгоритму розв'язку
        solve_thread.start()  # Запуск потоку

    def quit_game(self):
        self.running = False  # Зупинка гри

    def update_tiles(self):
        self.board = self.game.puzzle  # Оновлення дошки гри
        self.tiles = self.create_tiles(self.board)  # Оновлення плиток на дошці
        self.empty_row = self.game.empty_row  # Оновлення рядка порожньої плитки
        self.empty_col = self.game.empty_col  # Оновлення стовпця порожньої плитки
        self.draw_board()  # Оновлення відображення дошки
        pygame.display.update()  # Оновлення вікна

    def animate_solution(self, solution):
        for move in solution:
            self.game.move(move)  # Застосування дії до гри
            self.update_tiles()  # Оновлення плиток на дошці
            pygame.time.wait(500)  # Затримка для плавності відображення

    def draw_board(self):
        self.window.fill((0, 150, 150))  # Заповнення вікна світло-синім кольором
        for tile in self.tiles:
            pygame.draw.rect(self.window, tile[2], tile[1])
            text_rect = tile[0].get_rect(center=tile[1].center)
            self.window.blit(tile[0], text_rect)  # Відображення тексту на плитці

    def moving(self, event):
        if event.key == K_UP and not self.solve_running:
            self.game.move("up")
        elif event.key == K_DOWN and not self.solve_running:
            self.game.move("down")
        elif event.key == K_LEFT and not self.solve_running:
            self.game.move("left")
        elif event.key == K_RIGHT and not self.solve_running:
            self.game.move("right")

    def create_buttons(self):
        buttons = []
        button_width = 150
        button_height = 50
        button_spacing = 60

        new_game_button_rect = pygame.Rect(10, self.BOARD_SIZE + button_spacing, button_width, button_height)
        new_game_button = Button("New Game", new_game_button_rect, pygame.font.Font(None, 24), (255, 255, 255), (0, 51, 102),
                                 self.new_game)
        buttons.append(new_game_button)

        quit_button_rect = pygame.Rect(10 + (button_width + button_spacing - 30) * 2, self.BOARD_SIZE + button_spacing,
                                       button_width, button_height)
        quit_button = Button("Quit", quit_button_rect, pygame.font.Font(None, 24), (255, 255, 255), (102, 0, 0), self.quit_game)
        buttons.append(quit_button)

        solve_button_rect = pygame.Rect(10 + (button_width + button_spacing - 30), self.BOARD_SIZE + button_spacing,
                                        button_width, button_height)
        solve_button = Button("Solve", solve_button_rect, pygame.font.Font(None, 24), (255, 255, 255), (0, 102, 51), self.solve_game)
        buttons.append(solve_button)

        return buttons

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:  # Перевірка на вихід з програми
                    self.running = False
                if event.type == KEYDOWN:
                    self.moving(event)
                    self.empty_row = self.game.empty_row
                    self.empty_col = self.game.empty_col
                    self.board = self.game.puzzle
                    self.tiles = self.create_tiles(self.board)
                if not self.solve_running:  # Перевірка, чи алгоритм розв'язку не працює
                    for button in self.buttons:
                        button.handle_event(event)  # Обробка подій
            self.draw_board()  # Оновлення відображення
            for button in self.buttons:
                button.draw(self.window)
            if self.solve_running:
                if not self.game.is_solved():
                    message = pygame.font.Font(None, 48).render("Waiting...", True, (0, 0, 0))
                    message_rect = message.get_rect(center=(self.BOARD_SIZE // 1.5, self.BOARD_SIZE + 170))
                    self.window.blit(message, message_rect)
            if self.game.is_solved() and not self.solve_running:
                message = pygame.font.Font(None, 48).render("You solved the puzzle!", True, (0, 0, 0))
                message_rect = message.get_rect(center=(self.BOARD_SIZE // 1.5, self.BOARD_SIZE + 170))
                self.window.blit(message, message_rect)
            pygame.display.update()
            clock.tick(self.FPS)  # Затримка, щоб обмежити FPS
        save_board_to_file(self.board, "board.txt")
        pygame.quit()  # Завершення роботи pygame