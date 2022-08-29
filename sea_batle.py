from random import randrange, choice


class BoardOutException(Exception):
    pass


class FieldNotEmptyException(Exception):
    pass


class DirectionException(Exception):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f'{self.x} {self.y}'


class Ship:
    def __init__(self, length, bow, direct):
        self.life = length
        self.dots = [bow]
        for i in range(1, length):
            if direct == 'H':
                self.dots.append(Dot(bow.x, bow.y + i))
            elif direct == 'V':
                self.dots.append(Dot(bow.x + i, bow.y))
            else:
                raise DirectionException("Неправильное направление, разрешены 'H' и 'V ")


class Board:
    def __init__(self, name, hid=True):
        self.name = name.center(15)
        self.table = []
        for i in range(6):
            self.table.append([' '] * 6)
        self.ship_list = []
        self.hid = hid
        self.life = 0

    def add_ship(self, ship):
        contour = self.contour()
        if not all([dot not in contour for dot in ship.dots]):
            raise FieldNotEmptyException('Поле корабля недоступно для записи')
        elif not all([0 <= dot.x < 6 and 0 <= dot.y < 6 for dot in ship.dots]):
            raise BoardOutException('корабль вышел за границы поля')
        else:
            self.ship_list.append(ship)
            self.life += 1
            for dot in ship.dots:
                self.table[dot.x][dot.y] = '\u2586'

    def contour(self):
        res = []
        for ship in self.ship_list:
            for dot in ship.dots:
                for i in [-1, 0, 1]:
                    for j in [-1, 0, 1]:
                        if Dot(dot.x + i, dot.y + j) not in res:
                            res.append(Dot(dot.x + i, dot.y + j))
        return res

    def show(self):
        res = f'{self.name}\n'
        res += ' |'
        res += '|'.join(map (str, range(1, 7))) + '|\n'
        for i in range(6):
            if self.hid:
                res += f'{i + 1}|'
                res += '|'.join([self.table[i][j] if self.table[i][j] != '\u2586' else ' '
                                for j in range(6)]) + '|\n'
            else:
                res += f'{i + 1}|'
                res += '|'.join([self.table[i][j] for j in range(6)]) + '|\n'
        res += ' ' * 15 + '\n'
        res += ' ' * 15 + '\n'
        return res

    def shot(self, dot):
        if 0 <= dot.x < 6 and 0 <= dot.y < 6:
            if self.table[dot.x][dot.y] == '\u2586':
                self.table[dot.x][dot.y] = 'X'
                for ship in self.ship_list:
                    if dot in ship.dots:
                        ship.life -= 1
                        if ship.life == 0:
                            self.life -= 1
                return True
            elif self.table[dot.x][dot.y] == ' ':
                self.table[dot.x][dot.y] = 'T'
                return False
            else:
                raise FieldNotEmptyException('В клетку уже был выстрел')
        else:
            raise BoardOutException('Выстрел за пределы поля')

    def clear(self):
        self.table = []
        for i in range(6):
            self.table.append([' '] * 6)
        self.ship_list = []
        self.life = 0

    def random_board(self):
        self.clear()
        ll = 0
        len_list = [3, 2, 2, 1, 1, 1, 1]
        while ll < 7:
            free = [Dot(x, y) for x in range(6) for y in range(6) if Dot(x, y) not in self.contour()]
            if free:
                dot = choice(free)
                direct = choice('HV')
                try:
                    self.add_ship(Ship(len_list[ll], dot, direct))
                    ll += 1
                except BoardOutException:
                    pass
                except FieldNotEmptyException:
                    pass
            else:
                self.clear()
                ll = 0


class Player:
    def __init__(self, board):
        self.board = board

    def ask(self):
        pass

    def move(self):
        while True:
            return self.board.shot(self.ask())


class User(Player):
    def ask(self):
        while True:
            st = input('Ваш ход?\n')
            if not len(st) == 2 or st[0] not in '123456' or st[1] not in '123456':
                raise BoardOutException('Неправильный ход')
            elif self.board.table[int(st[0])-1][int(st[1])-1] in ('X', 'T'):
                raise FieldNotEmptyException('В эту клетку уже ходили')
            else:
                return Dot(int(st[0])-1, int(st[1])-1)


class AI(Player):
    def ask(self):
        while True:
            x, y = randrange(6), randrange(6)
            if self.board.table[x][y] not in ('X', 'T'):
                return Dot(x, y)


class Game:
    def __init__(self):
        self.legend = '''Обозначение полей и формат ввода:
' ' : пустое поле
'X' : попал
'T' : мимо
'▆' : Ваш корабль
'21': Строка 2, столбец 1, ENTER для ввода
---------------------------------------------
'''
        self.move_result = ''
        self.game_result = ''
        self.user = User(Board('Ваша доска'))
        self.user.board.random_board()
        self.ai = AI(Board('Доска AI', hid=False))
        self.ai.board.random_board()
        self.my_board = self.user.board
        self.enemy_board = self.ai.board
        self.player = self.user

    def info(self):
        res = self.legend
        res += f'{self.move_result}\n'
        res += f'{self.game_result}\n'
        return res

    def loop(self):
        gamer = self.user
        print(join_text(self.my_board.show(), self.enemy_board.show(), self.info()))
        while True:
            res = True
            try:
                move = gamer.ask()
                res = gamer.board.shot(move)
                if res:
                    self.move_result = 'Попал. Повтор хода'
                else:
                    self.move_result = 'Промах. Передача хода'
            except BoardOutException as exc:
                print(exc)
            except FieldNotEmptyException as exc:
                print(exc)
            if gamer.board.life == 0:
                if gamer == self.user:
                    self.game_result = 'Вы выиграли'
                else:
                    self.game_result = 'Компьютер выиграл'
                print(join_text(self.my_board.show(), self.enemy_board.show(), self.info()))
                break
            if not res:
                gamer.board.show()
                gamer = self.player_change(gamer)
                self.player = gamer
            print(join_text(self.my_board.show(), self.enemy_board.show(), self.info()))

    def player_change(self, gamer):
        if gamer == self.user:
            return self.ai
        else:
            return self.user


def join_text(*args, connector=' '*10):
    return '\n'.join([connector.join(tpl) for tpl in zip(*[arg.split('\n') for arg in args])])


game = Game()
game.loop()

