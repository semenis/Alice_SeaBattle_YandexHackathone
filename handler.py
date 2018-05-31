#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RU:
Это основная чать логики навыка Алисы Морской бой
Написана Сайдумаровым Семеном и Елизарововой Анастасией
Переписана и избавлена от костылей(но это не точно) Дином Дмитрием
EN:
This is main logic of Alice skill 'Sea war'
Writing by Saidumarov Semen and Elizarova Anastasiya
Rewriting and removing crutches (But it is not exactly) by Din Dmitiy
"""

from __future__ import unicode_literals
from json import dump
from random import randint, choice
from copy import deepcopy
from re import findall, match


class ShipBattle:
    def __init__(self):
        # Ключи - буквы, значения - индексы
        self.reversed_alphabet = {j: i for i, j in enumerate(ALPHABET)}
        # Генерируем поле
        self.field = [[0 for _ in range(10)] for _ in range(10)]

    # Вспомогательная фунция для проверки на пересечения
    def check_cell(self, cell, first_cell=False):
        x, y = cell
        count = 0
        possible_cells = [(1, 1), (-1, -1), (0, 1), (1, 0), (-1, 0), (0, -1), (-1, 1), (1, -1)]
        for possible in possible_cells:
            if -1 < x + possible[0] < 10 and -1 < y + possible[1] < 10:
                if self.field[y + possible[1]][x + possible[0]] == 1:
                    count += 1

        if (count < 2 and not first_cell) or (first_cell and count == 0):
            return True
        return False

    # Метод расстановки кораблей на поле
    def place_ships(self):
        for ship in SHIPS:
            while True:
                new_field = deepcopy(self.field)
                intersection = False
                direction = choice([True, False])

                if direction:  # по горизонтали
                    random_coors = (randint(0, 10 - ship), randint(0, 9))
                    for x in range(random_coors[0], random_coors[0] + ship):
                        if x == random_coors[0]:
                            passed_cell = self.check_cell((x, random_coors[1]), True)
                        else:
                            passed_cell = self.check_cell((x, random_coors[1]), False)

                        if not passed_cell:
                            intersection = True
                            break
                        else:
                            new_field[random_coors[1]][x] = 1

                else:  # по вертикали
                    random_coors = (randint(0, 9), randint(0, 10 - ship))
                    for y in range(random_coors[1], random_coors[1] + ship):
                        if y == random_coors[1]:
                            passed_cell = self.check_cell((random_coors[0], y), True)
                        else:
                            passed_cell = self.check_cell((random_coors[0], y), False)

                        if not passed_cell:
                            intersection = True
                            break
                        else:
                            new_field[y][random_coors[0]] = 1

                if not intersection:
                    self.field = deepcopy(new_field)
                    break

    def save_to_map_json(self):
        with open('map.json', 'w', encoding='utf8') as file:
            dump({"maps": self.field}, file)


SHIPS = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
ALPHABET = ['а', 'б', 'в', 'г', 'д', 'е', 'ж', 'з', 'и', 'к']

KILLED_WORDS = ['убила', 'убил', 'потопила', 'потоплен', 'потопил']
INJURED_WORDS = ['попала', 'попал', 'попадание', 'ранил', 'ранила']
MISSED_WORDS = ['мимо', 'промах', 'промазала', 'промазал']

ALL_WORDS = ['убила', 'убил', 'потопила', 'потопил', 'потоплен',
             'попала', 'попал', 'попадание', 'ранил', 'ранила',
             'мимо', 'промах', 'промазала', 'промазал']

PHRASES_FOR_ALICES_TURN = ['Пожалуйста, не жульничайте, я контролирую игру.', 'Помоему, сейчас не ваш ход.',
                           'Со мной такое не прокатит. Сейчас мой ход.', 'Может вы не будете меня обманывать?',
                           'Давайте я забуду это, а вы ответите еще раз.']

PHRASES_FOR_USERS_TURN = ['Сейчас ваш ход, не надо поддаваться.',
                          'Может вы что-то перепутали? Сейчас вы атакуете.',
                          'Я конечно не против, но давайте играть по правилам', 'Не люблю лёгкие победы...']


# Функция для непосредственной обработки диалога.
def handle_dialog(request, response, user_storage):
    # response.user_id
    if request.is_new_session:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.
        ship_battle = ShipBattle()
        ship_battle.place_ships()
        
        user_storage = {
            "user_id": request.user_id,
            "humans_turn": True,
            "life": sum(SHIPS),
            "AliceTurns": [],
            "Alices_matrix": ship_battle.field,
            "users_matrix": [[0 for _ in range(10)] for _ in range(10)],
            "sinked_ship": [],
            "cheating_stage": 0
        }

        # buttons, user_storage = get_suggests(user_storage)
        response.set_text('Привет! Играем в морской бой. Каждая клетка обозначается алфавитной буквой по горизонтали '
                          '(от "А" до "К", исключая "Ё" и "Й", слева направо) и цифрой по вертикали (от 1 до 10 сверху вниз). Мои корабли '
                          'уже расставлены. По вашей готовности атакуйте. Чтобы провести атаку скажите или введите'
                          ' координаты.')

        # response.set_buttons(buttons)
        return response, user_storage        
    
    ###DEBUG
    print(user_storage)
    if user_storage == None:
        user_storage = {
            "user_id": request.user_id,
            "humans_turn": True,
            "life": sum(SHIPS),
            "AliceTurns": [],
            "Alices_matrix": ship_battle.field,
            "users_matrix": [[0 for _ in range(10)] for _ in range(10)],
            "sinked_ship": [],
            "cheating_stage": 0
        }
    ###DEBUG_END
    
    
    
    
    # Обрабатываем ответ пользователя.
    user_message = request.command.lower().strip().replace(' ', '')

    # Пробуем перевести в координаты (между if и elif нельзя)
    try_to_make_coor = ''.join(findall(r'\w+', user_message))
    matched = match('\w\d0*', try_to_make_coor)

    # Проверка слова в допустимых словах
    if user_message in ALL_WORDS:

        # Если ходит Алиса
        if not user_storage["humans_turn"]:

            # Проверка наличия слова в словах о потоплении
            if user_message in KILLED_WORDS:
                user_storage["humans_turn"] = False
                response.set_text(alice_fires(user_storage["users_matrix"], killed=True))

            # Проверка наличия слова в словах о попадании
            elif user_message in INJURED_WORDS:
                user_storage["humans_turn"] = False
                response.set_text(alice_fires(user_storage["users_matrix"], killed=False))

            # Проверка наличия слова в словах о промахе
            elif user_message in MISSED_WORDS:
                user_storage["humans_turn"] = True
                response.set_text('Ваш ход.')

        # Если игрок сказал не в свой ход
        else:
            response.set_text(choice(PHRASES_FOR_USERS_TURN))

    # Проверка на присутствие шаблона re
    elif matched is not None:

        # Проверка, что сейчас ход игрока
        if user_storage["humans_turn"]:
            letter = matched.group(0)[0]
            number = int(matched.group(0)[1:])

            # Проверка корректности шаблона
            if 0 < number < 11 and letter in ALPHABET:
                result_of_fire = user_fires(user_storage["Alices_matrix"], (ALPHABET.index(letter), number - 1))

                # Анализ результата выстрела
                if result_of_fire == 'Мимо':
                    user_storage["humans_turn"] = False
                    response.set_text('Мимо. Я хожу. ' + alice_fires(user_storage['users_matrix'], killed=False))
                else:
                    user_storage["humans_turn"] = True
                    user_storage["life"] -= 1
                    response.set_text(result_of_fire)

            # Если не корректный ввод
            else:
                response.set_text("Координаты клетки обозначаются буквой (от А до К, исключая Ё и Й) и числом (от 1 до 10) для поля "
                                  "10 на 10 клеток. Пример - А1.")

        # Если ход Алисы
        else:
            response.set_text(choice(PHRASES_FOR_ALICES_TURN))

    # Если ничему не соответствует
    else:
        response.set_text("Простите, но я вас не поняла.")

    # В любом случае
    return response, user_storage


# Алгоритмический интеллект Алисы TODO
def alice_fires(matrix, killed=False):
    # TODO сделать обработку убил\ранил
    i = 0
    turn = [randint(0, 9), randint(0, 9)]
    while matrix[turn[1]][turn[0]] != 0:
        i += 1
        turn = [randint(0, 9), randint(0, 9)]
        if i >= 120:
            turn = [-1, -1]
    matrix[turn[1]][turn[0]] = 1

    return "{}{}".format(ALPHABET[turn[0]].upper(), turn[1] + 1)


# Обработка огня игрока
# 1 - клетки кораблей, 2 - клетки, куда стреляли, 3 - подбитые клетки корабля
def user_fires(matrix, coord):
    x, y = coord
    output = 'Вы уже стреляли сюда'

    if matrix[y][x] == 0:
        output = 'Мимо'
        matrix[y][x] = 2

    elif matrix[y][x] == 1:
        matrix[y][x] = 3

        # Волновой
        ship = [(x, y)]
        was = []
        while len(ship) > 0:
            sinking = True
            x, y = ship.pop(0)
            was.append((x, y))
            possible_cells = [(0, 1), (1, 0), (-1, 0), (0, -1)]

            for possible in possible_cells:
                if -1 < x + possible[0] < 10 and -1 < y + possible[1] < 10:
                    if (x + possible[0], y + possible[1]) not in was:
                        if matrix[y + possible[1]][x + possible[0]] == 3:
                            ship.append((x + possible[0], y + possible[1]))
                        elif matrix[y + possible[1]][x + possible[0]] == 1:
                            sinking = False
                            break
            if sinking:
                for cell in was:
                    matrix[cell[1]][cell[0]] = 2
                output = 'Потоплен'
            else:
                output = 'Ранен'

    return output
