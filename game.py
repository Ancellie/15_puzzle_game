import random
from solver import Puzzle


class Game:
    def __init__(self, size=4, shuffle_steps=1000):
        self.size = size
        self.puzzle = read_board_from_file("board.txt", self.size)  # Ініціалізація головоломки з файлу "board.txt"
        if self.puzzle is None or not self.is_solvable(self.puzzle):
            self.puzzle = self.create_board()  # Якщо не вдалося зчитати з файлу, створити нову головоломку
        self.empty_row, self.empty_col = self.get_empty_position()  # Знайти позицію порожньої клітинки
        self.moves = 0
        self.shuffle_steps = shuffle_steps

    def is_solvable(self, puzzle):
        flatten_puzzle = [number for row in puzzle.board for number in row]  # Конвертуємо головоломку в список
        inversions = 0  # Кількість інверсій
        empty_row = 0  # Рядок порожньої плитки

        # Підраховуємо інверсії та знаходимо рядок порожньої плитки
        for i in range(len(flatten_puzzle)):
            if flatten_puzzle[i] == 0:  # Знаходимо порожню плитку
                empty_row = puzzle.width - i // puzzle.width  # Обчислюємо рядок порожньої плитки
                continue
            for j in range(i + 1, len(flatten_puzzle)):
                if flatten_puzzle[j] == 0:  # Пропускаємо порожню плитку
                    continue
                if flatten_puzzle[j] < flatten_puzzle[i]:
                    inversions += 1

        # Перевіряємо умову розв'язності на основі кількості інверсій та рядка порожньої плитки
        if puzzle.width % 2 == 1:  # Для головоломок з непарною шириною
            return inversions % 2 == 0
        else:  # Для головоломок з парною шириною
            if empty_row % 2 == 0:
                return inversions % 2 == 1
            else:
                return inversions % 2 == 0

    def create_board(self):
        board = []
        for i in range(self.size):
            row = []
            for j in range(self.size):
                row.append(i * self.size + j + 1)
            board.append(row)
        board[self.size - 1][self.size - 1] = 0  # Остання клітинка встановлюється як порожня
        return Puzzle(board)

    def get_empty_position(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.puzzle.board[i][j] == 0:
                    return i, j  # Повертає позицію порожньої клітинки

    def shuffle_board(self):
        for _ in range(self.shuffle_steps):
            moves = self.get_valid_moves()  # Отримати доступні ходи
            random_move = random.choice(moves)  # Випадково вибрати один з доступних ходів
            self.move(random_move)  # Виконати хід

    def get_valid_moves(self):
        moves = []
        if self.empty_row > 0:
            moves.append('up')  # Додати хід "вгору" якщо порожня клітинка не знаходиться на верхній межі
        if self.empty_row < self.size - 1:
            moves.append('down')  # Додати хід "вниз" якщо порожня клітинка не знаходиться на нижній межі
        if self.empty_col > 0:
            moves.append('left')  # Додати хід "вліво" якщо порожня клітинка не знаходиться на лівій межі
        if self.empty_col < self.size - 1:
            moves.append('right')  # Додати хід "вправо" якщо порожня клітинка не знаходиться на правій межі
        return moves

    def print_board(self):
        for row in self.puzzle.board:
            print(row)
        print("")

    def move(self, direction):
        if direction == "down":
            if self.empty_row == self.size - 1:
                return  # Якщо порожня клітинка знаходиться на нижній межі, нічого не робити
            self.puzzle.board[self.empty_row][self.empty_col], self.puzzle.board[self.empty_row + 1][self.empty_col] = \
                self.puzzle.board[self.empty_row + 1][self.empty_col], self.puzzle.board[self.empty_row][self.empty_col]
            self.empty_row += 1  # Порожня клітинка зміщується вниз
        elif direction == "up":
            if self.empty_row == 0:
                return  # Якщо порожня клітинка знаходиться на верхній межі, нічого не робити
            self.puzzle.board[self.empty_row][self.empty_col], self.puzzle.board[self.empty_row - 1][self.empty_col] = \
                self.puzzle.board[self.empty_row - 1][self.empty_col], self.puzzle.board[self.empty_row][self.empty_col]
            self.empty_row -= 1  # Порожня клітинка зміщується вгору
        elif direction == "right":
            if self.empty_col == self.size - 1:
                return  # Якщо порожня клітинка знаходиться на правій межі, нічого не робити
            self.puzzle.board[self.empty_row][self.empty_col], self.puzzle.board[self.empty_row][self.empty_col + 1] = \
                self.puzzle.board[self.empty_row][self.empty_col + 1], self.puzzle.board[self.empty_row][self.empty_col]
            self.empty_col += 1  # Порожня клітинка зміщується вправо
        elif direction == "left":
            if self.empty_col == 0:
                return  # Якщо порожня клітинка знаходиться на лівій межі, нічого не робити
            self.puzzle.board[self.empty_row][self.empty_col], self.puzzle.board[self.empty_row][self.empty_col - 1] = \
                self.puzzle.board[self.empty_row][self.empty_col - 1], self.puzzle.board[self.empty_row][self.empty_col]
            self.empty_col -= 1  # Порожня клітинка зміщується вліво

    def is_solved(self):
        flattened_board = [element for row in self.puzzle.board for element in row]
        return flattened_board == list(range(1, self.size ** 2)) + [0]  # Перевірити, чи відповідає головоломка розв'язку

    def get_state(self):
        return tuple(tuple(row) for row in self.puzzle.board)  # Повертає поточний стан головоломки

    def set_state(self, state):
        self.puzzle.board = [list(row) for row in state]  # Встановлює поточний стан головоломки з заданого стану
        self.empty_row, self.empty_col = self.get_empty_position()  # Оновлює позицію порожньої клітинки


def read_board_from_file(file_path, size):
    try:
        with open(file_path, 'r') as file:
            board_str = file.read()
            puzzle = Puzzle.from_string(board_str, size)  # Зчитує головоломку з рядка у файлі
            if puzzle is None or not is_valid_board(puzzle.board, size) :  # Перевіряє, чи є головоломка дійсною та допустимою
                return None
            return puzzle
    except IOError:
        return None


def save_board_to_file(board, file_path):
    try:
        with open(file_path, 'w') as file:
            for row in board.formatted_string():
                row_str = '\n'.join(str(num) for num in row)
                file.write(row_str)  # Зберігає головоломку до файлу
        print("Дошка успішно збережена у файлі", file_path)
    except IOError:
        print("Помилка: не вдалося зберегти дошку у файл.")


def is_valid_board(board, size):
    # Перевірка розміру дошки
    if len(board) != size or any(len(row) != size for row in board):
        return False

    # Створення множини чисел, які повинні бути на дошці
    numbers = set(range(0, size * size + 1))  # +1 для підтримки двозначних чисел

    # Перевірка наявності чисел на дошці без повторень
    found_numbers = set()
    for row in board:
        for num in row:
            if num in found_numbers or num not in numbers:
                return False
            found_numbers.add(num)
    return True
