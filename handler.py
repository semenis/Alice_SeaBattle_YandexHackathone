#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RU:
Это основная чать логики навыка Алисы "Морской бой"
Написана Сайдумаровым Семеном и Елизарововой Анастасией
Переписана и избавлена от костылей(но это не точно) Дином Дмитрием
EN:
This is main logic of Alice skill "Sea battle"
Writing by Saidumarov Semen and Elizarova Anastasiya
Rewriting and removing crutches (But it is not exactly) by Din Dmitriy
"""

from __future__ import unicode_literals
from json import dump
from random import randint, choice
from copy import deepcopy
from re import findall, match
import logging

logging.basicConfig(level=logging.DEBUG)


class NoCellsError(Exception):
    pass


class WinnerError(Exception):
    pass


class ShipBattle:
    def __init__(self):
        # Ключи - буквы, значения - индексы
        self.reversed_alphabet = {j: i for i, j in enumerate(ALPHABET)}
        # Генерируем поле
        self.field = [[0 for _ in range(10)] for _ in range(10)]

    # Вспомогательная функция для проверки на пересечения
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
            "Target": [],
            "Alices_matrix": ship_battle.field,
            "users_matrix": [[0 for _ in range(10)] for _ in range(10)],
            "cheating_stage": 0,
            "last_turn": None,
            "free_cells": [(0, 1), (1, 0), (-1, 0), (0, -1)]

        }

        # Приветствие
        response.set_text('Привет! Играем в морской бой. Каждая клетка обозначается алфавитной буквой по горизонтали '
                          '(от "А" до "К", исключая "Ё" и "Й", слева направо) и цифрой по вертикали '
                          '(от 1 до 10 сверху вниз). Мои корабли уже расставлены. По вашей готовности атакуйте. Чтобы '
                          'провести атаку скажите или введите координаты.')
        # Выходим из функции и ждем ответа
        return response, user_storage

    # Обрабатываем ответ пользователя.
    user_message = request.command.lower().strip().replace(' ', '')

    # Пробуем перевести в координаты (между if и elif нельзя)
    try_to_make_coor = ''.join(findall(r'\w+', user_message))
    matched = match('\w\d0*', try_to_make_coor)

    try:
        # Проверка слова в допустимых словах
        if user_message in ALL_WORDS:

            # Если ходит Алиса
            if not user_storage["humans_turn"]:

                # Проверка наличия слова в словах о потоплении
                if user_message in KILLED_WORDS:
                    alice_answer = alice_fires(user_storage, "убил")  # TODO Все испраивть
                    response.set_text(alice_answer)

                # Проверка наличия слова в словах о попадании
                elif user_message in INJURED_WORDS:
                    alice_answer = alice_fires(user_storage, "ранил")
                    response.set_text(alice_answer)

                # Проверка наличия слова в словах о промахе
                elif user_message in MISSED_WORDS:
                    alice_answer = alice_fires(user_storage, "мимо")
                    response.set_text(alice_answer)

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
                        alice_answer = alice_fires(user_storage, "remember")
                        response.set_text('Мимо. Я хожу. ' + alice_answer)
                    else:
                        user_storage["life"] -= 1
                        response.set_text(result_of_fire)

                # Если не корректный ввод
                else:
                    response.set_text(
                        "Координаты клетки обозначаются буквой (от А до К, исключая Ё и Й) "
                        "и числом (от 1 до 10) для поля 10 на 10 клеток. Пример - А1.")

            # Если ход Алисы
            else:
                response.set_text(choice(PHRASES_FOR_ALICES_TURN))

        # Если ничему не соответствует
        else:
            response.set_text("Простите, но я вас не поняла.")

    # Выходы из рекурсии
    except NoCellsError:
        response.set_text("Я простреляла все клетки, так что считайте, что я победила.")
        response.end()

    except WinnerError:
        response.set_text("Я выиграла, спасибо за игру!")
        response.end()

    # В любом случае
    return response, user_storage


# Функция, отвечающая за стрельбу Алисы
def alice_fires(user_data, happened):

    # Рандомный выстрел
    def random_fire():
        cells_for_fire = []  # Список доступных клеток
        for _y in range(10):  # Поле 10 на 10
            for _x in range(10):
                # Пустая ли клетка
                if user_data["users_matrix"][_y][_x] == 0:
                    cells_for_fire.append((_x, _y))  # Добавляем в список возможных клеток
        # Проверка, на то, что еще остались пустые клетки
        if len(cells_for_fire) == 0:
            raise NoCellsError

        turn = choice(cells_for_fire)  # Рандомно берем
        user_data["last_turn"] = turn
        return "{}{}".format(ALPHABET[turn[0]].upper(), turn[1] + 1)  # Формируем ответ

    # Умный выстрел (с учетом предыдущих выстрелов для подбитого корабля)
    def clever_fire():  # TODO Доделать
        if len(user_data["Target"]) > 1:
            cell_1 = user_data["Target"][0]
            cell_2 = user_data["Target"][1]
            if cell_1[0] == cell_2[0]:
                for i in range(len(user_data["free_cells"])):
                    if user_data[i] == (0, 1) or user_data[i] == (0, -1):
                        user_data["free_cells"].pop(i)

            elif cell_1[1] == cell_2[1]:
                for i in range(len(user_data["free_cells"])):
                    if user_data[i] == (1, 0) or user_data[i] == (-1, 0):
                        user_data["free_cells"].pop(i)

        for _cell in user_data["Target"]:
            indexes_to_pop = []
            for index in range(len(user_data["free_cells"])):

                _x = user_data["free_cells"][index][0]
                _y = user_data["free_cells"][index][1]

                # Проверка на попадание в поле
                if 0 <= _x + _cell[0] <= 9 and 0 <= _y + _cell[1] <= 9:

                    # Если клетка стрелянная удаляем из возможных в конце цикла
                    if user_data["users_matrix"][_y][_x] == 2:
                        indexes_to_pop.append(index)

                    # Если клетка не стрелянная стреляем
                    elif user_data["users_matrix"][_y][_x] == 0:
                        user_data["last_turn"] = (_x, _y)
                        return "{}{}".format(ALPHABET[_x].upper(), _y + 1)

                # Если клетка не попадает в поле удаляем из возможных в конце цикла
                else:
                    indexes_to_pop.append(index)

            # Цикл для удаления возможных клеток
            for index_to_pop in indexes_to_pop:
                user_data["free_cells"].pop(index_to_pop)

        user_data["free_cells"] = [(0, 1), (1, 0), (-1, 0), (0, -1)]
        try_fire = random_fire()
        return "Судя по всему, корабль уже потоплен. " + try_fire

    answer = ''
    if happened == "убил" or happened == "ранил":
        user_data["life"] -= 1
        if user_data["life"] < 1:
            raise WinnerError

    if happened == "убил":
        user_data["cheating_stage"] = 0  # Обнуляем уровень жулика
        user_data["Target"].append(user_data["last_turn"])  # Добавим клетку, чтобы в цикле она тоже отметилась
        user_data["free_cells"] = [(0, 1), (1, 0), (-1, 0), (0, -1)]  # Обновляем возможные клетки
        for cell in user_data["Target"]:  # Проходим по клеткам корабля и отмечаем клетки в округе
            x, y = cell  # Достаем координаты

            # Возможные клетки
            possible_cells = [(1, 1), (-1, -1), (0, 1), (1, 0), (-1, 0), (0, -1), (-1, 1), (1, -1), (0, 0)]
            for possible in possible_cells:
                # Проверка на вхождение в поле
                if -1 < x + possible[0] < 10 and -1 < y + possible[1] < 10:
                    # Отмечаем данную клетку
                    user_data["users_matrix"][y + possible[1]][x + possible[0]] = 2

        # Опустошаем спискок, отвечающего за подбитый корабль
        user_data["Target"] = []
        return random_fire()

    elif happened == "ранил":
        user_data["cheating_stage"] = 0  # Обнуляем уровень жулика

        # Добаляем клетку в список корабля
        user_data["Target"].append(user_data["last_turn"])
        clever_fire()

    elif happened == "remember":
        if user_data["Target"]:
            return clever_fire()
        else:
            return random_fire()

    else:

        # Переключаем на ход игрока
        user_data["humans_turn"] = True

        # Выставление стрелянной клетки на поле
        x, y = user_data["last_turn"]
        user_data["users_matrix"][y][x] = 2

        # Инкримент к жульничеству
        user_data["cheating_stage"] += 1

        answer = 'Ваш ход.'
        # Замечания для жуликов
        if user_data["cheating_stage"] == 10:
            answer = 'Что-то мне не везет. Ваш ход.'
        elif user_data["cheating_stage"] == 20:
            answer = 'По теории вероятности я уже должна была попасть хотя бы раз. Ваш ход.'
        elif user_data["cheating_stage"] == 40:
            answer = 'Мне кажется, что вы играете не совсем честно.'
        elif user_data["cheating_stage"] == 60:
            answer = 'Моя гипотеза подтверждается с каждым моим промахом.'
        elif user_data["cheating_stage"] == 80:
            answer = 'Роботы в отличае от людей не умеют обманывать.'
        elif user_data["cheating_stage"] == 97:
            answer = 'Надеюсь, такая простая победа принесет вам хотя бы каплю удовольствия, ' \
                     'ведь моя задача заключается в том чтобы радовать людей и упрощать их жизнь'

    return answer


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

            # Плюс, потому что корабли в виде линий
            possible_cells = [(0, 1), (1, 0), (-1, 0), (0, -1)]

            # Проходим по возможным клеткам
            for possible in possible_cells:
                # Попадают ли клетка в поле
                if -1 < x + possible[0] < 10 and -1 < y + possible[1] < 10:

                    # Проходилась ли клетка
                    if (x + possible[0], y + possible[1]) not in was:

                        # Если в клетке 3
                        if matrix[y + possible[1]][x + possible[0]] == 3:
                            ship.append((x + possible[0], y + possible[1]))

                        # Если в клетке 1
                        elif matrix[y + possible[1]][x + possible[0]] == 1:
                            sinking = False
                            break

            if sinking:
                for cell in was:  # Проходимся по клеткам корабля
                    matrix[cell[1]][cell[0]] = 2
                output = 'Потоплен'
            else:
                output = 'Ранен'

    return output
