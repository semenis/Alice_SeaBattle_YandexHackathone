# coding: utf-8
from __future__ import unicode_literals
import json
import random

# Функция для непосредственной обработки диалога.
def handle_dialog(request, response, user_storage):
    # response.user_id
    if request.is_new_session:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.
        b = Battle_ships()
        b.place_ships()
        b.save_to_map_json()
        with open('map.json') as maps:
            my_map = json.load(maps)["maps"]
        user_storage = {
            "user_id": request.user_id,
            "maps": my_map,
            "human": 1,
            "AliceTurns": [],
            "userMatrix": [],
            "sinked_ship": [],
            "cheating_stage": 0
            # TODO map generate

        }

        # buttons, user_storage = get_suggests(user_storage)
        response.set_text('Привет! Играем в морской бой. Для атаки введите координаты ввиде (А1)!')
        # response.set_buttons(buttons)

        return response, user_storage

    # Обрабатываем ответ пользователя.
    if request.command.lower() in ['убил', 'ранил', 'попал', 'мимо']:
        if request.command.lower() == 'убил':
            if ifend(user_storage["maps"]):
                # print(user_storage)
                if user_storage["human"] == 1:
                    response.set_text('Конец игры. Человек победил.')

                else:
                    response.set_text('Конец игры. Алиса победила.')
            else:
                a = ''
                # response.set_text('Я хожу')
                alph = 'абвгдежзийкл'
                user_storage["human"] = 0
                c = AliceTurn(user_storage)

                a = a + ' Я хожу ' + alph[c[0]].upper() + str(c[1] + 1)
                response.set_text(a)
        if request.command.lower() in ['ранил', 'попал']:
            user_storage["human"] = 0
            t = AliceTurn(user_storage)
            alph = 'абвгдежзийкл'
            a = '\nЯ хожу ' + alph[t[0]].upper() + str(t[1] + 1)
            response.set_text(a)

        if request.command.lower() == 'мимо':
            # print(user_storage)
            response.set_text('Ваш ход')
            user_storage["human"] = 1
        return response, user_storage
    elif request.command.lower()[0] in 'абвгдежзийкл' and request.command.lower()[1:] in '12345678910' and user_storage[
        "human"] == 1 and int(request.command.lower()[1:]) < 10:

        a = vustrel(user_storage["maps"], request.command.lower())
        if a == 'мимо':
            alph = 'абвгдежзийкл'
            user_storage["human"] = 0
            c = AliceTurn(user_storage)

            a = a + ' \nЯ хожу ' + alph[c[0]].upper() + str(c[1] + 1)
        else:
            user_storage["human"] = 1
        response.set_text(a)

        return response, user_storage
    elif user_storage["human"] == 0:
        t = AliceTurn(user_storage)
        alph = 'абвгдежзийкл'
        a = '\nЯ хожу ' + alph[t[0]].upper() + str(t[1] + 1)
        response.set_text(a)

        user_storage["human"] = 1
        return response, user_storage
    else:
        response.set_text("Некорректная команда")
        return response, user_storage


def AliceTurn(user_storage):
    if user_storage["userMatrix"] == []:  # sinked_ship, cheating_stage
        user_storage["userMatrix"] = [[0 for j in range(10)] for i in range(10)]
    #
    # if len(user_storage["sinked_ship"]) == 0:
    #     possible_cells = []
    #     for y in range(10):
    #         for x in range(10):
    #             if user_storage["userMatrix"][y][x] == 0:
    #                 pass
    #
    #     possible_cells = list(filter(lambda x,y: user_storage["userMatrix"][y][x] == 0, []))
    #     turn = [random.randint(0, 9), random.randint(0, 9)]
    # else:
    #     pass
    i = 0
    turn = [random.randint(0, 9), random.randint(0, 9)]
    while user_storage["userMatrix"][turn[0]][turn[1]] != 0:
        i += 1
        turn = [random.randint(0, 9), random.randint(0, 9)]
        if i == 100:
            turn = [-1, -1]
    user_storage["userMatrix"][turn[0]][turn[1]] = 2
    return turn


def ifend(matrix):
    end = True
    for i in matrix:
        if 1 in i:
            end = False
            return end
    return end


def vustrel(matrix, coord):
    k = 0
    alph = 'абвгдежзийкл'
    output = None
    list_ship = []
    for j in range(len(alph)):
        if coord[0] == alph[j]:
            k = j

    ind = int(coord[1]) - 1
    if matrix[ind][k] == 2:
        output = 'Вы уже стреляли сюда'
    elif matrix[ind][k] == 0:
        output = 'Мимо'
    elif matrix[ind][k] == 1:
        matrix[ind][k] = 2

        if matrix[ind][k + 1] == 0 and matrix[ind][k - 1] == 0 and matrix[ind + 1][k] == 0 and matrix[ind - 1][k] == 0:
            output = 'Убит'
        elif matrix[ind][k + 1] == 0 and matrix[ind][k - 1] == 0:
            for j in range(4):
                if 0 <= j <= 9:
                    if matrix[ind + j][k] == 0:
                        break
                    else:
                        list_ship.append(matrix[ind + j][k])
            for j in range(1, 5):
                if 0 <= j <= 9:
                    if matrix[ind - j][k] == 0:
                        break
                    else:
                        list_ship.append(matrix[ind - j][k])
        elif matrix[ind + 1][k] == 0 and matrix[ind - 1][j] == 0:
            for j in range(1, 5):
                if 0 <= j <= 9:
                    if matrix[ind][k + j] == 0:
                        break
                    else:
                        list_ship.append(matrix[ind][k + j])
            for j in range(1, 5):
                if 0 <= j <= 9:
                    if matrix[ind][k - j] == 0:
                        break
                    else:
                        list_ship.append(matrix[ind][k - j])

        if 1 in list_ship:
            output = 'Ранен'
        else:
            output = 'Убит'
    return output


from json import dump
from random import randint, choice
from copy import deepcopy


class Battle_ships:
    def __init__(self):
        self.alphabet = [i for i in 'aбвгдеёжзийклмнопкрстуфкцчшщъыьэюя']
        self.reversed_alphabet = {j: i for i, j in enumerate(self.alphabet)}
        self.field = [[0 for i in range(10)] for i in range(10)]

    def check_cell(self, cell, first_cell=False):
        x, y = cell
        count = 0
        possibleCells = [(1, 1), (-1, -1), (0, 1), (1, 0), (-1, 0), (0, -1), (-1, 1), (1, -1)]
        for possible in possibleCells:
            if -1 < x + possible[0] < 10 and -1 < y + possible[1] < 10:
                if self.field[y + possible[1]][x + possible[0]] == 1:
                    count += 1

        if (count < 2 and not first_cell) or (first_cell and count == 0):
            return True
        return False

    def place_ships(self):
        ships = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        for ship in ships:
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
                # print(ship)
                # for i in new_field:
                # print(i)
                if not intersection:
                    self.field = deepcopy(new_field)
                    break

    def save_to_map_json(self):
        with open('map.json', 'w', encoding='utf8') as file:
            dump({"maps": self.field}, file)

