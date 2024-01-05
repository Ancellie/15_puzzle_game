import itertools
from heapq import heappop, heappush


class Node:
    #Клас, що представляє вузол розв'язувача
    #- 'puzzle' - це екземпляр класу Puzzle
    #- 'parent' - попередній вузол, створений розв'язувачем, якщо є
    #- 'action' - дія, виконана для отримання головоломки, якщо є

    def __init__(self, puzzle, parent=None, action=None):
        self.puzzle = puzzle
        self.parent = parent
        self.action = action
        if self.parent is not None:
            self.g = parent.g + 1
        else:
            self.g = 0

    @property
    def score(self):
        return self.g + self.h

    @property
    def state(self):
        #Повертає хешований представлення self
        return str(self)

    @property
    def path(self):
        #Відновлює шлях від кореня 'parent'

        node, p = self, []
        while node:
            p.append(node)
            node = node.parent
        yield from reversed(p)

    @property
    def solved(self):
        #Обгортка для перевірки, чи головоломка 'puzzle' розв'язана
        return self.puzzle.solved

    @property
    def actions(self):
        #Обгортка для 'actions', доступних в поточному стані
        return self.puzzle.actions

    @property
    def h(self):
        return self.puzzle.manhattan

    def __str__(self):
        return str(self.puzzle)

    def __lt__(self, other):
        return self.score < other.score

    def __gt__(self, other):
        return self.score > other.score

    def __le__(self, other):
        return self.score <= other.score

    def __ge__(self, other):
        return self.score >= other.score

    def __eq__(self, other):
        return self.score == other.score

    def __ne__(self, other):
        return self.score != other.score


class Solver:
    #Розв'язувач головоломки "8-пазл"
    #- 'start' - екземпляр класу Puzzle

    def __init__(self, start):
        self.start = start

    def solve(self):
        #Виконати пошук А* і повернути шлях до розв'язку, якщо він існує


        if not self.start.solved:  # Перевіряємо, чи початкова дошка вже розв'язана
            start_node = Node(self.start)
            open_list = [(start_node.score, start_node)]
            seen = set()
            seen.add(start_node.state)

            while open_list:
                _, node = heappop(open_list)

                if node.solved:
                    return node.path

                for move, action in node.actions:
                    child = Node(move(), node, action)

                    if child.state not in seen:
                        heappush(open_list, (child.score, child))
                        seen.add(child.state)

        return None  # Повертає None, якщо початкова дошка вже розв'язана


class Puzzle:
    #Клас, що представляє "8-пазл".
    #'board' - квадратний список списків з цілими числами 0...ширина^2 - 1
    # наприклад, [[1,2,3],[4,0,6],[7,5,8]]

    def __init__(self, board):
        self.width = len(board[0])
        self.board = board

    @staticmethod
    def from_string(board_str, size):
        board = []
        numbers = board_str.split()
        if len(numbers) != size * size:
            return None

        for i in range(0, len(numbers), size):
            row = list(map(int, numbers[i:i + size]))
            board.append(row)

        return Puzzle(board)

    @property
    def solved(self):
        #Головоломка розв'язана, якщо числа у сплющеній дошці знаходяться в
        #зростаючому порядку зліва направо, а тайл '0' знаходиться на
        #останній позиції на дошці

        solved_config = [[(i * self.width) + j + 1 for j in range(self.width)] for i in range(self.width)]
        solved_config[self.width - 1][self.width - 1] = 0
        return self.board == solved_config

    @property
    def actions(self):
        #Повертає список пар 'move', 'action'. 'move' можна викликати,
        #щоб отримати нову головоломку, яка виникає в результаті зсуву тайлу '0'
        #в напрямку 'action'.

        def create_move(at, to):
            return lambda: self._move(at, to)

        moves = []
        for i, j in itertools.product(range(self.width), range(self.width)):
            direcs = {'right': (i, j - 1),
                      'left': (i, j + 1),
                      'down': (i - 1, j),
                      'up': (i + 1, j)}

            for action, (r, c) in direcs.items():
                if 0 <= r < self.width and 0 <= c < self.width and self.board[r][c] == 0:
                    move = create_move((i, j), (r, c)), action
                    moves.append(move)
        return moves

    @property
    def manhattan(self):
        distance = 0
        for i in range(self.width):
            for j in range(self.width):
                if self.board[i][j] != 0:
                    x, y = divmod(self.board[i][j] - 1, self.width)
                    distance += abs(x - i) + abs(y - j)
        return distance

    def copy(self):
        #Повертає нову головоломку з тією самою дошкою, що і 'self'

        board = []
        for row in self.board:
            board.append([x for x in row])
        return Puzzle(board)

    def _move(self, at, to):
        #Повертає нову головоломку, в якій тайли 'at' і 'to' були обміняні місцями.
        #ЗАМІТКА: всі ходи повинні бути 'actions', що були виконані

        copy = self.copy()
        i, j = at
        r, c = to
        copy.board[i][j], copy.board[r][c] = copy.board[r][c], copy.board[i][j]
        return copy

    def pprint(self):
        for row in self.board:
            print(row)
        print()

    def formatted_string(self):
        return '\n'.join(' '.join(map(str, row)) for row in self.board)

    def __str__(self):
        return str(self.board)

    def __iter__(self):
        for row in self.board:
            yield from row
