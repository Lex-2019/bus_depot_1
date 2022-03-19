import psycopg
from psycopg import Error
# import os module
from os import system, name
# sleep module to display output for some time period
from time import sleep

cursor = None
connection = None
global_marker = True

# работа с запросами:
record_search = ""   # проверка наличия записи в БД
data_search = ""     # вытягиваем данные из БД для дальнейших вычислений
create_id = ""       # создание идентификатора
data_insertion = ""  # вставка данных в БД
data_update = ""     # обновление данных в БД

# основные данные по смене, рейсу, выходу...
wd_date = ""
shift = 0
route = ""
sh_round = None
comment = None
current_year = None
current_month = None
# придумать отдельное правило для 21 и 52 маршрутов (те, что без выходов)...

# информация с БУЛа / график по плану:
shrr_id = 0
week_id = 0
proceeds = 0.0
number_of_flights = ""
waybill = 0
modified_plan = None
first_shift = []       # время первой смены / пика
second_rush_hour = []  # время второго пика
shift_or_rush_hour = 0

# плановые задания:
work_days = []
work_days_new = []
someday_ru = ["план на БУДНИЙ ДЕНЬ",
              "план на субботу",
              "план на воскресенье"]
someday_en = ["plan_weekday",
              "plan_saturday",
              "plan_sunday"]

# дополнительные маршруты:
flight = ""
local_plan = 0.0
local_number_of_flights = 1


# функция ввода цифрового значения при выборе:
def get_input(digit, message):
    ret = ""

    # выполнять, пока Символ ПУСТОЙ или символа НЕТ в СТРОКЕ digit:
    while ret == "" or ret not in digit:
        ret = input(message)
    return ret
    # пример вызова функции:
    # print(" Ставлю на...")
    # print("    1. Чётное")
    # print("    2. Нечётное")
    # print("    0. Возврат в предыдущее меню")
    # x = get_input("012", "    Ваш выбор? ")


# ожидаем ответ 'Yes' или 'No':
def yes_no_input(message):
    print(message)

    user = ""
    local_marker = True  # маркер цикла

    while (local_marker
           and user.upper() not in ("YES", "Y", "НУЫ", "Н", "NO", "N", "ТЩ", "Т")):
        user = input("\nВаш ответ? ")

        # если ДА:
        if user.upper() in ("YES", "Y", "НУЫ", "Н"):
            user = "1"
            local_marker = False

        # если НЕТ
        elif user.upper() in ("NO", "N", "ТЩ", "Т"):
            user = "0"
            local_marker = False

        # проверка на ввод числа:
        elif user.isdigit():
            print("\nПожалуйста, будьте внимательныю Введите 'yes' или 'no'. ")

    return user
    # примерный вызов функции:
    # yes_no_input("Пожалуйста введите \'yes\' или \'no\'. ")


# определение функции очистки экрана (консоли)
def clear():
    # for windows
    if name == 'nt':
        _ = system('cls')

    # for mac and linux (here, os.name is 'posix')
    else:
        _ = system('clear')
    # Примечание. Используется переменная подчеркивания,
    # потому что оболочка Python всегда сохраняет свой последний вывод в подчеркивании.


# меню выбора ввода данных
def main_menu():
    global global_marker

    while global_marker:
        print("  Что вы желаете ввести:\n")
        print("    1. Выручка за смену")
        print("    2. Резерв")
        print("    3. Больничный")
        print("    0. Выход из программы")

        x = get_input("0123", "\n    Твой выбор: ")

        if x == "0":  # преобразование в цифру будет в функции get_input
            clear()
            global_marker = False
        elif x == "1":
            clear()
            connect_postgres()
        elif x == "2":
            clear()
            reserve_time()
        elif x == "3":
            clear()
            data_from_sick_leave()


# ввод данных "с путевого листа о рейсе" в случае необходимости:
def insert_my_date():
    global wd_date, shift, route, sh_round, proceeds, number_of_flights, waybill, modified_plan,\
        first_shift, second_rush_hour, shift_or_rush_hour, \
        record_search, create_id, data_search

    local_marker = True  # маркер цикла

    while local_marker:
        wd_date = str(input("Введите дату выхода на рейс (пример: 2020-09-31): "))

        shift = int(input("Введите номер смены: "))
        route = str(input("""Введите номер маршрута
(буквенные маршруты дописывать кирилицей, в нижнем регистре): """))
        sh_round = int(input("Введите номер выхода: "))

        # подумать о сокращённом варианте ввода. пример: 21-11-14
        proceeds = float(input("Введите сумму выручки: "))
        number_of_flights = str(input("Введите количество выполненных рейсов (пример: 9+1): "))
        waybill = int(input("Введите номер путевого листа: "))

        print("\nБыл ли в этот день изменён план (сход машины, замена в резерве и пр.)?")
        x = yes_no_input("  введите \'Yes\' или \'No\'. ")

        if x == "1":
            modified_plan = float(input("Введите изменённый (модифицированный) план: "))
        elif x == "0":
            modified_plan = "NULL"

        print("\nДанный график \"1\" - сменный или \"2\" - пиковой?")
        shift_or_rush_hour = get_input("12", "  Ваш выбор?\n")

        if shift_or_rush_hour == "1":
            first_shift.append(str(input("Введите время начала рейса по факту (пример: 14:10): ")))
            first_shift.append(str(input("Введите время окончания рейса по факту (пример: 23:45): ")))
            first_shift.append(str(input("Введите фактическую продолжительность рейса (пример: 8:10): ")))
            print(f"""\n    Давайте проверим введенные данные.
Ваша смена - {shift}, маршрут номер "{route}", выход - {sh_round}.
Дата рейса - {wd_date}.
Выручка составила {proceeds} рублей, количество рейсов - "{number_of_flights}", путевой лист номер 00{waybill}.
Начало рейса в "{first_shift[0]}", окончание в "{first_shift[1]}", продолжительность рейса "{first_shift[2]}".
""")
        elif shift_or_rush_hour == "2":
            first_shift.append(str(input("Введите время начала рейса 1-го пика (пример: 05:10): ")))
            first_shift.append(str(input("Введите время окончания рейса 1-го пика (пример: 10:45): ")))
            first_shift.append(str(input("Введите фактическую продолжительность рейса 1-го пика (пример: 2:10): ")))
            second_rush_hour.append(str(input("Введите время начала рейса 2-го пика (пример: 14:25): ")))
            second_rush_hour.append(str(input("Введите время окончания рейса 2-го пика (пример: 20:20): ")))
            second_rush_hour.append(
                str(input("Введите фактическую продолжительность рейса 2-го пика (пример: 4:35): ")))

            print(f"""\n    Давайте проверим введенные данные.
Ваша смена - {shift}, маршрут номер "{route}", выход - {sh_round}.
Дата рейса - {wd_date}.
Выручка составила {proceeds} рублей, количество рейсов - "{number_of_flights}", путевой лист номер 0{waybill}.
Начало 1-го пика в "{first_shift[0]}", окончание в "{first_shift[1]}", продолжительность пика "{first_shift[2]}".
Начало 2-го пика в "{second_rush_hour[0]}", окончание в "{second_rush_hour[1]}", \
продолжительность пика "{second_rush_hour[2]}".
""")
        print("Правильно ли введены данные?\n")
        # Выбор пункта меню:
        x = yes_no_input("  введите \'Yes\' или \'No\'. ")

        if x == "1":
            # проверяем наличие id смены/маршрута/выхода:
            record_search = f"""
SELECT COUNT(shrr_id) FROM shift_route_round
WHERE shift = {shift} AND route = '{route}' AND round = {sh_round};
"""
            # если нет, добавляем:
            create_id = f"""
INSERT INTO shift_route_round (shift, route, round)
VALUES ({shift}, '{route}', {sh_round});
"""
            # вывод id смены/маршрута/выхода:
            data_search = f"""
SELECT shrr_id FROM shift_route_round
WHERE shift = {shift} AND route = '{route}' AND round = {sh_round};
"""
            input("\nНажми Enter для продолжения...\n")
            local_marker = False
        elif x == "0":
            print("\n Введите данные заново, и будьте внимательней: \n")
            first_shift.clear()
            second_rush_hour.clear()


# ввод заметки / коментария:
def insert_note():
    global comment, data_insertion

    comment = str(input("Введите заметку к данному рейсу:\n"))
    data_insertion = f"""
UPDATE working_date
    SET note = '{comment}'
    WHERE wd_date = '{wd_date}' AND shrr_id = {shrr_id};
"""


# данные для ввода проданных проездных:
def insert_my_ticket():
    global data_insertion

    ticket_name = ["декадные билеты на автобус",
                   "общие декадные билеты",
                   "месячные билеты на автобус",
                   "общие месячные билеты"]
    number_of_tickets = []

    print(f"Напоминаем, мы вносим данные на {wd_date} число.")

    for i in ticket_name:
        x = yes_no_input(f"""\nБыли ли проданы {i}? """)
        if x == "1":
            j = float(input("Введите количество: "))
            number_of_tickets.append(j)
        else:
            number_of_tickets.append("NULL")

    data_insertion = f"""
INSERT INTO ticket VALUES ('{wd_date}',
                           {number_of_tickets[0]}, {number_of_tickets[1]},
                           {number_of_tickets[2]}, {number_of_tickets[3]});
"""
    number_of_tickets.clear()


# плановые задания по выручке:
def insert_plan():
    global work_days, someday_ru, data_insertion,\
        current_year, current_month

    print(f"Напоминаю, что мы вносим данные на {wd_date} число.")

    for i in someday_ru:
        x = yes_no_input(f"\nНадо ли внести {i}? ")
        if x == "1":
            work_days.append(float(input("Введите план: ")))
        else:
            work_days.append("NULL")

    data_insertion = f"""
INSERT INTO planned_tasks_for_revenue
VALUES ('20{current_year}-{current_month}-01', {shrr_id},
        {work_days[0]}, {work_days[1]}, {work_days[2]});
"""


# выводим планы на экран и спрашиваем, нужно ли их изменять:
def update_plan():
    global work_days, work_days_new, someday_ru, data_update

    print(f"\nНапоминаю, что мы вносим данные на {wd_date} число.\n")

    for i, j in zip(someday_ru, work_days):
        x = yes_no_input(f"""{i} назначен {j}, нужно ли его изменять? """)
        if x == "1":
            j = float(input("Введите план: "))
            work_days_new.append(j)
        else:
            work_days_new.append(j)


# графики рейсов по плану:
def insert_schedule():
    global week_id, number_of_flights, first_shift, second_rush_hour, data_insertion, shift_or_rush_hour

    week_id = int(input("Если это будний день, введите '1'. Если выходной, введите '2': "))
    number_of_flights = str(input("Введите количество рейсов по плану (пример: 9+1): "))

    print("\n    При вводе данных по фактически отработанному времени у вас сохранились следующие данные:")
    # График "1" - сменный, "2" - пиковой:
    if shift_or_rush_hour == "1":
        print(f"""Время начала рейса - {first_shift[0]}, время окончания рейса - {first_shift[1]}, \
продолжительность рейса - {first_shift[2]}.
Желаете ли применить введенные даные для планового графика?
""")
        # Выбор пункта меню:
        x = yes_no_input("  введите \'Yes\' или \'No\'. ")
        if x == "1":
            pass
        elif x == "0":
            first_shift.clear()
            first_shift.append(str(input("Введите время начала рейса по плану (пример: 14:10): ")))
            first_shift.append(str(input("Введите время окончания рейса по плану (пример: 23:45): ")))
            first_shift.append(str(input("Введите плановую продолжительность рейса (пример: 8:10): ")))
        data_insertion = f"""
INSERT INTO planned_schedule (shrr_id, week_id,
                              start_of_time, end_of_time, time_duration,
                              number_of_flights)
VALUES ({shrr_id}, {week_id}, '{first_shift[0]}', '{first_shift[1]}', '{first_shift[2]}',
        '{number_of_flights}');
"""
        input(" Нажми Enter для продолжения...")

    elif shift_or_rush_hour == "2":
        print(f"""Время начала 1-го пика - {first_shift[0]}, время окончания 1-го пика - {first_shift[1]},
продолжительность 1-го пика - {first_shift[2]};
Время начала 2-го пика - {second_rush_hour[0]}, время окончания 2-го пика - {second_rush_hour[1]},
продолжительность 2-го пика - {second_rush_hour[2]}.
Желаете ли применить введенные даные для планового графика?\n
""")
        # Выбор пункта меню:
        x = yes_no_input("  введите \'Yes\' или \'No\'. ")
        if x == "1":
            pass
        elif x == "0":
            first_shift.clear()
            second_rush_hour.clear()
            first_shift.append(str(input("Введите время начала рейса по плану (пример: 05:10): ")))
            first_shift.append(str(input("Введите время окончания рейса по плану (пример: 10:45): ")))
            first_shift.append(str(input("Введите плановую продолжительность рейса (пример: 2:10): ")))
            second_rush_hour.append(str(input("Введите время начала рейса 2-го пика (пример: 14:25): ")))
            second_rush_hour.append(str(input("Введите время окончания рейса 2-го пика (пример: 20:20): ")))
            second_rush_hour.append(str(input("Введите плановую продолжительность рейса 2-го пика (пример: 4:35): ")))
        data_insertion = f"""
INSERT INTO planned_schedule (shrr_id, week_id,
                              start_of_time, end_of_time, time_duration,
                              second_start_of_time, second_end_of_time, second_time_duration,
                              number_of_flights)
VALUES ({shrr_id}, {week_id}, '{first_shift[0]}', '{first_shift[1]}', '{first_shift[2]}',
        '{second_rush_hour[0]}', '{second_rush_hour[1]}', '{second_rush_hour[2]}',
        '{number_of_flights}');
"""
        input("\n Нажми Enter для продолжения...")


# при наличии доп маршрутов:
def additional_route():
    global flight, local_plan, local_number_of_flights, week_id, data_search, data_insertion

    flight = str(input("""Введите номер маршрута
    (буквенные маршруты дописывать кирилицей, в нижнем регистре (пример: 13а)): """))
    week_id = int(input("Если это будний день, введите '1'. Если выходной, введите '2': "))
    local_plan = float(input("Введите план на данный маршрут (пример: 128.00): "))
    local_number_of_flights = str(input("Введите количество рейсов дополнительного маршрута (пример: 1+1): "))
    # при наличии доп маршрутов, поиск 'psch_id'
    data_search = f"""
SELECT psch_id FROM planned_schedule WHERE shrr_id = {shrr_id} AND week_id = {week_id};
"""
    # при наличии доп маршрутов, вставка:
    data_insertion = f"""
INSERT INTO flight (psch_id, flight, plan, number_of_flights, f_date) 
VALUES ({data_search}, '{flight}', {local_plan}, '{local_number_of_flights}', '{wd_date}');
"""


# замена рабочего дня на выходной и обратно:
def some_holiday():
    global data_update
    holiday = int(input("""Введите 1, если выходной день заменяется на рабочий,
        6, если рейсы в будний день ходят по расписанию субботы,
        7, если рейсы в будний день ходят по расписанию воскресенья: """))
    data_update = f"""
UPDATE working_date
SET holiday = {holiday}
WHERE wd_date = '{wd_date}';
"""


# вносим данные о резерве:
def reserve_time():
    global cursor, connection, data_insertion

    print(f"\n Давайте введем данные о резерве. \n")

    try:
        schema = "bus_depot_1"
        connection = psycopg.connect(host="localhost",
                                     port=5432,
                                     dbname="postgres",
                                     user="postgres",
                                     password="sbetrieb",
                                     options=f"-c search_path={schema},public")
        # Курсор для выполнения операций с базой данных
        cursor = connection.cursor()

        local_marker = True
        time_of_reserve = []

        while local_marker:
            time_of_reserve.append(str(input("Введите дату резерва (пример: 2020-09-31): ")))
            time_of_reserve.append(str(input("Введите время начала рейса (пример: 5:00): ")))
            time_of_reserve.append(str(input("Введите время окончания рейса (пример: 10:00): ")))

            x = yes_no_input(f"\nНадо ли добавить комментарий? ")
            if x == "1":
                time_of_reserve.append(str(input("\nВведите комментарий к данному резерву: \n")))

            print("\nПравильно ли введены данные?")
            print(f"""
Время начала рейса: {time_of_reserve[1]},
Время окончания рейса: {time_of_reserve[2]},
Комментарий: {time_of_reserve[3]}.
""")
            x = yes_no_input("  введите \'Yes\' или \'No\'. ")

            if x == "1":
                input("Нажми Enter для продолжения...")
                local_marker = False
            elif x == "0":
                print("\n Введите данные заново, и будьте внимательней: \n")

        data_insertion = f"""
INSERT INTO reserve (r_date, start_of_time, end_of_time, note)
VALUES('{time_of_reserve[0]}', '{time_of_reserve[1]}', '{time_of_reserve[2]}', '{time_of_reserve[3]}');
"""
        cursor.execute(data_insertion)
        connection.commit()
        print("Reserve inserted successfully")
        time_of_reserve.clear()

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)

    finally:
        cursor.close()
        connection.close()
        print("Соединение с PostgreSQL закрыто")

    input("\nВыход в главное меню...\n")
    clear()  # чистим экран консоли перед выводом меню
    main_menu()


# вставка данных о больничном:
def data_from_sick_leave():
    global cursor, connection, data_insertion

    print(f"\n Давайте введем данные о больничном. \n")

    try:
        schema = "bus_depot_1"
        connection = psycopg.connect(host="localhost",
                                     port=5432,
                                     dbname="postgres",
                                     user="postgres",
                                     password="sbetrieb",
                                     options=f"-c search_path={schema},public")
        # Курсор для выполнения операций с базой данных
        cursor = connection.cursor()

        local_marker = True
        sick_leave = []

        while local_marker:
            sick_leave.append(str(input("Введите дату открытия больничного (пример: 2020-08-25): ")))
            sick_leave.append(str(input("Введите дату закрытия больничного (пример: 2020-09-14): ")))
            sick_leave.append(str(input("Введите причину больничного (диагноз): ")))

            print("\nПравильно ли введены данные?")
            print(f"""
Дата открытия больничного: {sick_leave[0]},
Дата закрытия больничного: {sick_leave[1]},
Причина больничного (диагноз): {sick_leave[2]}.
""")
            x = yes_no_input("  введите \'Yes\' или \'No\'. ")

            if x == "1":
                input("Нажми Enter для продолжения...")
                local_marker = False
            elif x == "0":
                print("\n Введите данные заново, и будьте внимательней: \n")
                sick_leave.clear()

        data_insertion = f"""
INSERT INTO sick_leave (start_of_date, end_of_date, note)
VALUES ('{sick_leave[0]}', '{sick_leave[1]}', '{sick_leave[2]}')
"""
        cursor.execute(data_insertion)
        connection.commit()
        print("sick_leave inserted successfully")

        sick_leave.clear()

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)

    finally:
        cursor.close()
        connection.close()
        print("Соединение с PostgreSQL закрыто")

    input("\nВыход в главное меню...\n")
    clear()  # чистим экран консоли перед выводом меню
    main_menu()


def connect_postgres():
    global cursor, connection, shrr_id, wd_date, comment, \
        record_search, data_search, create_id, data_insertion, data_update, \
        work_days, work_days_new, someday_en, \
        first_shift, second_rush_hour, current_year, current_month

    try:
        # Подключение к существующей базе данных
        schema = "bus_depot_1"
        connection = psycopg.connect(host="localhost",
                                     port=5432,
                                     dbname="postgres",
                                     user="postgres",
                                     password="sbetrieb",
                                     options=f"-c search_path={schema},public")
        # Курсор для выполнения операций с базой данных
        cursor = connection.cursor()

        # находим последнюю дату, внесённую в базу:
        last_date = f"""
SELECT MAX(wd_date) FROM working_date;
"""
        cursor.execute(last_date)
        my_query = cursor.fetchone()
        wd_date = my_query[0]

        # работаем с данными с БУЛа и путевого листа:
        print(f"\nПоследняя запись в базе данных датирована {wd_date}.\n")
        print("Давайте внесем данные с БУЛа и путевого листа: \n")

        # ввод рабочих данных с клавиатуры:
        insert_my_date()

        # проверяем наличие id смены/маршрута/выхода:
        cursor.execute(record_search)
        my_query = cursor.fetchone()
        count_id = my_query[0]

        # запоминаем id либо заносим (создаём) в бд:
        if count_id == 0:
            # создаем shrr_id:
            cursor.execute(create_id)
            connection.commit()
            print("shrr_id created successfully")

            # вытягиваем созданный shrr_id из таблиц:
            cursor.execute(data_search)
            my_query = cursor.fetchone()
            shrr_id = my_query[0]
        else:
            # вытягиваем существующий shrr_id из таблиц:
            cursor.execute(data_search)
            my_query = cursor.fetchone()
            shrr_id = my_query[0]

        # вносим данные с путевого и була:
        data_insertion = f"""
INSERT INTO working_date (wd_date, shrr_id, proceeds, number_of_flights, waybill, modified_plan,
                          start_of_time, end_of_time, time_duration)
VALUES ('{wd_date}', {shrr_id}, {proceeds}, '{number_of_flights}', {waybill}, {modified_plan},
        '{first_shift[0]}', '{first_shift[1]}', '{first_shift[2]}');
"""
        cursor.execute(data_insertion)
        connection.commit()
        print("Date from waybill inserted successfully")

        # добавляем заметки, если требуется:
        local_marker = True
        while local_marker:
            print("\n Желаете ли добавить заметку на данный рейс?\n")

            x = yes_no_input('  введите \'Yes\' или \'No\'. ')

            if x == "1":
                insert_note()
                cursor.execute(data_insertion)
                connection.commit()  # коммитим вставку данных
                print("Note inserted successfully")
                local_marker = False
            elif x == "0":
                local_marker = False
        comment = None  # обнуляем переменную комментария для последующих вставок/изменений

        # проездные, если требуется:
        local_marker = True
        while local_marker:
            print("\n Желаете ли добавить информацию о проданных проездных?\n")
            x = yes_no_input('  введите \'Yes\' или \'No\'. ')

            if x == "1":
                print("Введите информацию о проданных проездных билетах:")
                insert_my_ticket()
                cursor.execute(data_insertion)
                connection.commit()
                print("Tickets inserted successfully")
                local_marker = False
            elif x == "0":
                local_marker = False

        # проверяем наличие планового задания в принципе:
        current_year = wd_date[2:4]
        current_month = wd_date[5:7]
        record_search = f"""
SELECT COUNT(ptfr_date) FROM planned_tasks_for_revenue
WHERE shrr_id = {shrr_id} AND EXTRACT(month FROM ptfr_date) = {current_month};
"""
        cursor.execute(record_search)
        my_query = cursor.fetchone()
        count_tasks = my_query[0]

        # плановые задания по выручке - запоминаем и заносим (создаём) в бд:
        if count_tasks == 0:
            print("\nВ этом месяце план на данный маршрут ещё НЕ был внесён.")
            # определяются переменные планов:
            insert_plan()
            cursor.execute(data_insertion)
            connection.commit()
            print("\nPlanned task inserted successfully\n")

        # изменяем плановые задания при их наличии в БД в случае необходимости.
        # для этого получаем уже существующие:
        else:
            data_search = f"""
SELECT plan_weekday, plan_saturday, plan_sunday FROM planned_tasks_for_revenue
WHERE shrr_id = {shrr_id} AND EXTRACT(month FROM ptfr_date) = {current_month};
"""
            cursor.execute(data_search)
            my_query = cursor.fetchall()
            for row in my_query:
                for i in row:
                    if i == None:
                        work_days.append("NULL")
                    else:
                        work_days.append(i)

            # выводим планы на экран и спрашиваем, нужно ли их изменять:
            update_plan()

        # если есть изменения в планах, вносим в БД:
        if work_days != work_days_new:
            for i, j in zip(someday_en, work_days_new):
                data_update = f"""
UPDATE planned_tasks_for_revenue
SET {i} = {j}
WHERE shrr_id = {shrr_id} AND EXTRACT(month FROM ptfr_date) = {current_month};
"""
                cursor.execute(data_update)
                connection.commit()
            print("\nPlanned task updated successfully")

        work_days.clear()
        work_days_new.clear()

        # проверяем наличие графики рейсов по плану в принципе:
        record_search = f"""
SELECT count(psch_id) FROM planned_schedule WHERE shrr_id = {shrr_id};
"""
        cursor.execute(record_search)
        my_query = cursor.fetchone()
        count_tasks = my_query[0]

        # графики рейсов по плану - запоминаем и заносим (создаём) в бд:
        if count_tasks == 0:
            # определяются переменные графиков:
            insert_schedule()
            cursor.execute(data_insertion)
            connection.commit()
            print("planned schedule inserted successfully")

        first_shift.clear()
        second_rush_hour.clear()

        # при наличии доп. маршрутов:
        local_marker = True
        while local_marker:
            print(f"\n Желаете ли добавить дополнительный маршрут на дату {wd_date}?\n")

            x = yes_no_input('  введите \'Yes\' или \'No\'. ')

            if x == "1":
                # определяются переменные доп.маршрутов:
                additional_route()
                cursor.execute(data_search)  # определяется 'psch_id'

                cursor.execute(data_insertion)
                connection.commit()
                print("flight inserted successfully")

            elif x == "0":
                local_marker = False

        # работа в собственный выходной:
        local_marker = True
        while local_marker:
            print(f"\n Дата {wd_date} является рабочим днем по графику, или это выход в ваш выходной день?\n")

            x = get_input("12", "введите \'1\' если по графику, или \'2\' если это выходной день? ")

            if x == "1":
                local_marker = False
            elif x == "2":
                data_update = f"""
UPDATE working_date
SET personal_day_off = 1
WHERE wd_date = '{wd_date}';
"""
                cursor.execute(data_update)
                connection.commit()
                local_marker = False

        # меняем МАЗ, если требуется:
        local_marker = True
        while local_marker:
            print(f"\n Вы работали на длинной машине, или с короткой базой?\n")

            x = get_input("12", "введите \'1\' если был МАЗ 105(215), или \'2\' если был МАЗ 107(103)? ")

            if x == "1":
                local_marker = False
            elif x == "2":
                # меняем с МАЗ 105(215) (по умолчанию) на МАЗ 107(103):
                data_update = f"""
UPDATE working_date
SET bus_id = 2
WHERE wd_date = '{wd_date}' AND shrr_id = {shrr_id};
"""
                cursor.execute(data_update)
                connection.commit()
                local_marker = False

        # замена рабочего дня на выходной и обратно:
        local_marker = True
        while local_marker:
            print(f"\nБыла ли произведена замена {wd_date} с рабочего на выходной или обратно? \n")

            x = yes_no_input('  введите \'Yes\' или \'No\'. ')

            if x == "1":
                some_holiday()
                cursor.execute(data_update)
                connection.commit()
                local_marker = False
            elif x == "0":
                local_marker = False

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)

    finally:
        # if connection:
        # Close the cursor and connection to so the server can allocate bandwidth to other requests
        cursor.close()
        connection.close()
        print("Соединение с PostgreSQL закрыто")
    input("\nВыход в главное меню...\n")
    clear()  # чистим экран консоли перед выводом меню
    main_menu()


clear()  # чистим экран консоли перед выводом приветстия
print("Вас приветствует программа ввода данных по выручке кондуктора \"АП-1\".")
sleep(4)  # sleep time 4 seconds after printing output

clear()  # чистим экран консоли перед выводом меню
main_menu()
