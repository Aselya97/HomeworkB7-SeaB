#импортируем генерацию случайных чисел
from random import randint

from random import randint
#создаем внутреннюю логику игры и классы

class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "это за границами игрового поля "


class BoardOldException(BoardException):
    def __str__(self):
        return "эта клетка уже была выбрана"


class BoardOtherShipException(BoardException):
    pass


#реализуем класс точек на поле
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

#метод,чтобы точки можно было проверять на равенство
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"

#создаем класс корабля: точку ,где размещен нос корабля; направление корабля,длину и количество жизней
class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l
# реализуем метод dots, который возвращает список всех точек корабля
    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots

#создаем класс игровой доски и его параметры
class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0

        self.field = [["O"] * size for _ in range(size)]

        self.busy = []
        self.ships = []
#реализуем метод , который ставит корабль на доску
    def add_ship(self, ship):

        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardOtherShipException()
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)
#Метод contour, который обводит корабль по контуру
    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)
#выводим корабли на доску
    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")
        return res
#ограничение выстрелов в пределах игрового поля
    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))
#стрельба по доске
    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardOldException()

        self.busy.append(d)

        for ship in self.ships:
            if ship.shoot(d):
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("корабль убит")
                    return False
                else:
                    print("корабль ранен")
                    return True

        self.field[d.x][d.y] = "."
        print("мимо")
        return False

    def begin(self):
        self.busy = []

    def defeat(self):
        return self.count == len(self.ships)

#создаем класс игрока
class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy
#метод, который спрашивает игрока, в какую клетку он делает выстре
    def ask(self):
        raise NotImplementedError()

    def move(self):  # осуществление выстрела
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

#класс противника
class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            print("введите координаты через пробел:")
            print("  - номер строки  ")
            print("  - номер столбца ")
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:  # Проверка количества введенных координат
                print(" нужно ввести 2 координаты ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" введите числа ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)

#создаём  главный класс и описываем его параметры
class Game:
    def __init__(self, size=6):
        self.size = size
        self.lens = [3, 2, 2, 1, 1, 1, 1]
        pl = self.random_board()  #
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)
#реализуем метод ,который генерирует случайную доску
    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def try_board(self):
        board = Board(size=self.size)
        attempts = 0
        for l in self.lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardOtherShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print("********************")
        print("    WELCOME  ")
        print("    TO THE      ")
        print("  SEA BATTLE    ")
        print("********************")

    def print_board(self):
        print("-" * 20)
        print("Доска игрока:")
        print(self.us.board)
        print("-" * 20)
        print("Доска компьютера:")
        print(self.ai.board)

    # метод с самим игровым циклом
    def loop(self):
        num = 0
        while True:
            self.print_board()
            if num % 2 == 0:
                print("-" * 20)
                print("ход игрока")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("ход компьютера")
                repeat = self.ai.move()
            if repeat:
                num -= 1
            # если  у противника не осталось целых кораблей
            if self.ai.board.defeat():
                self.print_board()
                print("-" * 20)
                print("победа за игроком")
                break
            # если  у игрока не осталось целых кораблей
            if self.us.board.defeat():
                self.print_board()
                print("-" * 20)
                print("победа за компьютером")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()