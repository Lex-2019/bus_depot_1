import psycopg
from psycopg import Error

cursor = None
connection = None
# choice = True  # логическая переменная для определения, вносить ли дальше данные или достаточно

# работа с запросами (нужны ли они в глобале?):
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
current_year, current_month = None, None
# придумать отдельное правило для 21 и 52 маршрутов (те, что без выходов)

# информация с БУЛа / график по плану:
shrr_id = 0
week_id = 0
proceeds = 0.0
number_of_flights = ""
waybill = 0
first_shift = []  # время первой смены / пика
second_rush_hour = []  # время второго пика

# проездные:
ticket_name = ["декадные билеты на автобус",
               "общие декадные билеты",
               "месячные билеты на автобус",
               "общие месячные билеты"]
number_of_tickets = []

# плановые задания:
work_days = []
work_days_new = []
someday_ru = ["план на БУДНИЙ ДЕНЬ",
              "план на субботу",
              "план на воскресенье",
              "модифицированный план"]
someday_en = ["plan_weekday",
              "plan_saturday",
              "plan_sunday",
              "modified_plan"]

# дополнительные маршруты (нужны ли они в глобале?):
psch_id = 0
flight = ""
local_plan = 0.0
local_number_of_flights = 1

# замена рабочих и выходных дней (нужны ли они в глобале?)
holiday = ""

# больничный (нужны ли они в глобале?):
sick_leave = []  # альтернатива трём переменным:
start_of_sick = ""
end_of_sick = ""
diagnosis = ""


# функция ввода цифрового значения при выборе:
def get_input(digit, message):
    # пример вызова функции:
    # print(" Ставлю на...")
    # print("    1. Чётное (выигрыш 1:1)")
    # print("    2. Нечётное (выигрыш 1:1)")
    # print("    3. Дюжина (выигрыш 3:1)")
    # print("    4. Число (выигрыш 36:1)")
    # print("    0. Возврат в предыдущее меню")
    # x = get_input("01234", "    Ваш выбор? ")
    ret = ""
    while ret == "" or ret not in digit:
        # выполнять, пока Символ ПУСТОЙ или символа НЕТ в СТРОКЕ digit
        ret = input(message)
    return ret


# ожидаем ответ 'Yes' или 'No'
def yes_no_input(message):
    print(message)
    # примерный вызов функции:
    # yes_no_input("Пожалуйста введите \'yes\' или \'no\'. ")

    user = ""
    local_marker = True  # маркер цикла

    while (local_marker
           and user.upper() != "YES"
           and user.upper() != "Y"
           and user.upper() != "НУЫ"
           and user.upper() != "Н"
           and user.upper() != "NO"
           and user.upper() != "N"
           and user.upper() != "ТЩ"
           and user.upper() != "Т"):
        user = input("\nВаш ответ?\n")

        # если ДА:
        if (user.upper() == "YES"
                or user.upper() == "Y"
                or user.upper() == "НУЫ"
                or user.upper() == "Н"):
            user = "1"
            local_marker = False

        # если НЕТ
        elif (user.upper() == "NO"
              or user.upper() == "N"
              or user.upper() == "ТЩ"
              or user.upper() == "Т"):
            user = "0"
            local_marker = False

        # проверка на ввод числа:
        elif user.isdigit():
            print("\nПожалуйста, будьте внимательныю Введите 'yes' или 'no'.\n")

    return user


# проверка необходимости внесения данных "с путевого листа о рейсе", ввод данных в случае необходимости:
def insert_my_date():
    global wd_date, shift, route, sh_round, shrr_id, proceeds, number_of_flights, \
        waybill, first_shift, second_rush_hour, comment, \
        record_search, data_search, create_id, data_insertion

    print(f"\nПоследняя запись в базе данных датирована {wd_date}.\n")

    local_marker = True  # маркер цикла

    while local_marker:
        print("Желаете ли внести данные / продолжить внесение данных?\n")

        # Выбор пункта меню:
        x = yes_no_input("введите \'Yes\' или \'No\'. ")

        if x == "1":
            shift = int(input("Введите номер смены: "))
            route = str(input("""Введите номер маршрута
(буквенные маршруты дописывать кирилицей, в нижнем регистре): """))
            sh_round = int(input("Введите номер выхода: "))

            wd_date = str(input("Введите дату выхода на рейс (пример: 2021-10-31): "))
            # подумать о сокращённом варианте ввода. пример: 21-11-14
            proceeds = float(input("Введите сумму выручки: "))
            number_of_flights = str(input("Введите количество выполненных рейсов (пример: 9+1): "))
            waybill = int(input("Введите номер путевого листа: "))

            # print("\nДанный график сменный или пиковой?\n")
            # x = yes_no_input('введите \'Yes\', если сменный или \'No\', если пиковой.')
            print("\nДанный график \"1\" - сменный или \"2\" - пиковой?")
            x = get_input("12", "    Ваш выбор? \n")

            if x == "1":
                first_shift.append(str(input("Введите время начала рейса по факту (пример: 14:10): ")))
                first_shift.append(str(input("Введите время окончания рейса по факту (пример: 23:45): ")))
                first_shift.append(str(input("Введите фактическую продолжительность рейса (пример: 8:10): ")))
                print(f"""\n    Давайте проверим введенные данные.
Ваша смена - {shift}, маршрут номер "{route}", выход - {sh_round}.
Дата рейса - {wd_date}.
Выручка составила {proceeds} рублей, количество рейсов - "{number_of_flights}", путевой лист номер 00{waybill}.
Начало рейса в "{first_shift[0]}", окончание в "{first_shift[1]}", продолжительность рейса "{first_shift[2]}".
""")
            elif x == "0":
                first_shift.append(str(input("Введите время начала рейса 1-го пика (пример: 05:10): ")))
                first_shift.append(str(input("Введите время окончания рейса 1-го пика (пример: 10:45): ")))
                first_shift.append(str(input("Введите фактическую продолжительность рейса 1-го пика (пример: 2:10): ")))
                second_rush_hour.append(str(input("Введите время начала рейса 2-го пика (пример: 14:25): ")))
                second_rush_hour.append(str(input("Введите время окончания рейса 2-го пика (пример: 20:20): ")))
                second_rush_hour.append(str(input("Введите фактическую продолжительность рейса 2-го пика \
                                                   (пример: 4:35): ")))
                print(f"""\n    Давайте проверим введенные данные.
Ваша смена - {shift}, маршрут номер "{route}", выход - {sh_round}.
Дата рейса - {wd_date}.
Выручка составила {proceeds} рублей, количество рейсов - "{number_of_flights}", путевой лист номер 00{waybill}.
Начало 1-го пика в "{first_shift[0]}", окончание в "{first_shift[1]}", продолжительность пика "{first_shift[2]}".
Начало 2-го пика в "{second_rush_hour[0]}", окончание в "{second_rush_hour[1]}", \
продолжительность пика "{second_rush_hour[2]}".
""")

            # написать функцию по промежуточной проверке точности введенных данных пользователем
            # отдельно для смен и пиков
            print("Правильно ли введены данные?\n")

            # Выбор пункта меню:
            x = yes_no_input("введите \'Yes\' или \'No\'. ")

            if x == "1":
                # Ждём нажатия Enter и продолжаем:
                input("Нажми Enter для продолжения...")
                local_marker = False
            elif x == "0":
                # обнуляем все ранее введенные данные в списки
                first_shift.clear()
                second_rush_hour.clear()
                print("\n Введите данные заново, и будьте внимательней: \n")
                # рекурсивный вызов функции (предлагаем ввести значения заново):
                insert_my_date()

        elif x == "0":
            local_marker = False

    # проверяем наличие id смены/маршрута/выхода:
    record_search = f"""
SELECT COUNT(shrr_id) FROM shift_route_round
WHERE shift = {shift} AND route = '{route}' AND round = {sh_round};
"""
    # вывод id смены/маршрута/выхода:
    data_search = f"""
SELECT shrr_id FROM shift_route_round
WHERE shift = {shift} AND route = '{route}' AND round = {sh_round};
"""
    # если нет, добавляем:
    create_id = f"""
INSERT INTO shift_route_round (shift, route, round)
VALUES ({shift}, '{route}', {sh_round});
"""


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
    global ticket_name, number_of_tickets, data_insertion

    print(f"Напоминаю, что мы вносим данные на {wd_date} число.")

    for i in ticket_name:
        x = yes_no_input(f"""Были ли проданы {i}? """)
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


# вносим данные о резерве:
def reserve_time():
    global comment, data_insertion

    start_of_time = str(input("Введите время начала рейса (пример: 5:00): "))
    end_of_time = str(input("Введите время окончания рейса (пример: 10:00): "))

    x = yes_no_input(f"\nНадо ли добавить комментарий? ")
    if x == "1":
        comment = str(input("\nВведите комментарий к данному резерву: "))

    data_insertion = f"""
INSERT INTO reserve VALUES('{wd_date}', '{start_of_time}', '{end_of_time}', '{comment}');
"""


# плановые задания по выручке:
def insert_plan():
    global work_days, someday_ru, someday_en, data_insertion, data_search

    print(f"\nНапоминаю, что мы вносим данные на {wd_date} число.\n")

    for i in someday_ru:
        x = yes_no_input(f"Надо ли внести {i}? ")
        if x == "1":
            work_days.append(float(input("Введите план: ")))
        else:
            work_days.append("NULL")

    data_insertion = f"""
INSERT INTO planned_tasks_for_revenue
VALUES ('20{current_year}-{current_month}-01', {shrr_id},
        {work_days[0]}, {work_days[1]}, {work_days[2]}, {work_days[3]});
"""
    data_search = f"""
SELECT plan weekday, plan saturday, plan sunday, modified plan FROM planned_tasks_for_revenue
WHERE shrr_id = {shrr_id} AND EXTRACT(month FROM ptfr_date) = {current_month};
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
    global week_id, number_of_flights, first_shift, second_rush_hour, data_insertion

    week_id = int(input("Если это будний день, введите '1'. Если выходной, введите '2': "))
    number_of_flights = str(input("Введите количество рейсов по плану (пример: 9+1): "))

    # определить сменный график или пиковой
    # (запомнить выбор при вводе фактических данных за смену/рейс -?)
    # также можно ввести автокопирование времени, если изменений в графике не было!
    print("\nДанный график \"1\" - сменный или \"2\" - пиковой?")
    x = get_input("12", "    Ваш выбор? \n")

    if x == "1":
        first_shift.append(str(input("Введите время начала рейса по плану (пример: 14:10): ")))
        first_shift.append(str(input("Введите время окончания рейса по плану (пример: 23:45): ")))
        first_shift.append(str(input("Введите плановую продолжительность рейса (пример: 8:10): ")))
        input(" Нажми Enter для продолжения...")
    elif x == "0":
        first_shift.append(str(input("Введите время начала рейса по плану (пример: 05:10): ")))
        first_shift.append(str(input("Введите время окончания рейса по плану (пример: 10:45): ")))
        first_shift.append(str(input("Введите плановую продолжительность рейса (пример: 2:10): ")))
        second_rush_hour.append(str(input("Введите время начала рейса 2-го пика (пример: 14:25): ")))
        second_rush_hour.append(str(input("Введите время окончания рейса 2-го пика (пример: 20:20): ")))
        second_rush_hour.append(str(input("Введите плановую продолжительность рейса 2-го пика (пример: 4:35): ")))
        input(" Нажми Enter для продолжения...")

    data_insertion = f"""
INSERT INTO planned_schedule (shrr_id, week_id,
                              start_of_time, end_of_time, time_duration,
                              second_start_of_time, second_end_of_time, second_time_duration,
                              number_of_flights)
VALUES ({shrr_id}, {week_id}, '{first_shift[0]}', '{first_shift[1]}', '{first_shift[2]}',
        '{second_rush_hour[0]}', '{second_rush_hour[1]}', '{second_rush_hour[2]}',
        '{number_of_flights}');
"""


# при наличии доп маршрутов:
def additional_route():
    global flight, local_plan, local_number_of_flights, data_search, data_insertion

    flight = str(input("""Введите номер маршрута
    (буквенные маршруты дописывать кирилицей, в нижнем регистре (пример: 13а)): """))
    local_plan = float(input("Введите план на данный маршрут (пример: 128.00): "))
    local_number_of_flights = int(input("Введите количество рейсов дополнительного маршрута (пример: 1+1): "))
    # при наличии доп маршрутов, поиск 'psch_id'
    data_search = f"""
SELECT psch_id FROM planned_schedule WHERE shrr_id = {shrr_id};
"""
    # при наличии доп маршрутов, вставка:
    data_insertion = f"""
INSERT INTO flight (psch_id, flight, plan, number_of_flights, f_date) 
VALUES ({data_search}, '{flight}', {local_plan}, '{local_number_of_flights}', '{wd_date}');
"""


# вставка данных о больничном:
def data_from_sick_leave():
    global start_of_sick, end_of_sick, diagnosis, data_insertion

    start_of_sick = str(input("Введите дату открытия больничного (пример: 2021-10-31): "))
    end_of_sick = str(input("Введите дату закрытия больничного (пример: 2021-10-31): "))
    diagnosis = str(input("Введите причину больничного (диагноз): "))  # если потребуется
    data_insertion = f"""
INSERT INTO sick_leave (start_of_date, end_of_date, note)
VALUES ('{start_of_sick}', '{end_of_sick}', '{diagnosis}')
"""


def connect_postgres():
    # global choice  # маркер главного цикла, пока не придумал, как применить...
    global cursor, connection, shrr_id, wd_date, comment, \
        record_search, data_search, create_id, data_insertion, data_update, \
        number_of_tickets, psch_id, holiday, \
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
        # ввод рабочих данных с клавиатуры:
        insert_my_date()

        # проверяем наличие id смены/маршрута/выхода:
        cursor.execute(record_search)
        my_query = cursor.fetchone()
        count_id = my_query[0]

        # запоминаем id либо заносим (создаём) в бд:
        if count_id == 0:
            cursor.execute(create_id)
            connection.commit()  # коммитим вставку данных
            print("shrr_id created successfully")
        else:
            cursor.execute(data_search)
            my_query = cursor.fetchone()
            shrr_id = my_query[0]

            # connect_postgres()  # рекурсивный вызов функции ??

        # вносим данные с путевого и була:
        data_insertion = f"""
INSERT INTO working_date (wd_date, shrr_id, proceeds, number_of_flights, waybill,
                          start_of_time, end_of_time, time_duration)
VALUES ('{wd_date}', {shrr_id}, {proceeds}, '{number_of_flights}', {waybill},
        '{first_shift[0]}', '{first_shift[1]}', '{first_shift[2]}');
"""
        cursor.execute(data_insertion)
        connection.commit()  # коммитим вставку данных
        print("Date from waybill inserted successfully")
        # чистим списки:
        first_shift.clear()

        # добавляем заметки, если требуется:
        local_marker = True  # маркер цикла
        while local_marker:
            print(" Желаете ли добавить заметку на данный рейс?\n")
            # Выбор пункта меню:
            x = yes_no_input('введите \'Yes\' или \'No\'. ')

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
        local_marker = True  # маркер цикла
        while local_marker:
            print(" Желаете ли добавить информацию о проданных проездных?\n")
            # Выбор пункта меню:
            x = yes_no_input('введите \'Yes\' или \'No\'. ')

            if x == "1":
                print("Введите информацию о проданных проездных билетах:\n")
                insert_my_ticket()
                cursor.execute(data_insertion)
                connection.commit()
                print("Tickets inserted successfully")
                local_marker = False
            elif x == "0":
                local_marker = False

        number_of_tickets.clear()

        # добавляем резерв, если требуется:
        local_marker = True  # маркер цикла
        while local_marker:
            print("\n Был ли в этот день резерв?\n")
            # Выбор пункта меню:
            x = yes_no_input('введите \'Yes\' или \'No\'. ')

            if x == "1":
                reserve_time()
                cursor.execute(data_insertion)
                connection.commit()
                print("Reserve inserted successfully")
                local_marker = False
            elif x == "0":
                local_marker = False
        comment = None  # обнуляем переменную комментария для последующих вставок/изменений

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
        # (возможно нужно поменять местами содержимое цикла if/else)
        if count_tasks == 0:
            print("В этом месяце план на данный маршрут ещё не был внесён.")
            insert_plan()  # определяются переменные планов
            cursor.execute(data_insertion)
            connection.commit()
            print("Planned task inserted successfully")

        # изменяем плановые задания при их наличии в БД в случае необходимости.
        # для этого получаем уже существующие:
        else:
            cursor.execute(data_search)
            my_query = cursor.fetchall()
            for row in my_query:
                for i in row:
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
 # !!!!!!!!!!!!!!!!!!!!!
                # удалить после отладки:
                print("data_update")
                input("если цикл не сработал, остановить программу (с 0 до 3 включительно)")

                cursor.execute(data_update)
                connection.commit()
                print("Planned task updated successfully")

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
            insert_schedule()  # определяются переменные планов
            cursor.execute(data_insertion)
            connection.commit()
            print("planned schedule inserted successfully")

        first_shift.clear()
        second_rush_hour.clear()
        # start_of_time_2 = None
        # end_of_time_2 = None
        # time_duration_2 = None

        # при наличии доп. маршрутов:
        local_marker = True  # маркер цикла
        while local_marker:
            print(f"\n Желаете ли добавить дополнительный маршрут на дату {wd_date}?\n")
            # Выбор пункта меню:
            x = yes_no_input('введите \'Yes\' или \'No\'. ')

            if x == "1":
                additional_route()  # определяются переменные планов
                cursor.execute(data_search)  # определяется 'psch_id'
                my_query = cursor.fetchone()
                psch_id = my_query[0]

                cursor.execute(data_insertion)
                connection.commit()
                print("flight inserted successfully")

            elif x == "0":
                local_marker = False

        # работа в собственный выходной:
        local_marker = True  # маркер цикла
        while local_marker:
            print(f"\n Дата {wd_date} является рабочим днем по графику, или это выход в ваш выходной день?\n")
            # Выбор пункта меню:
            x = yes_no_input('введите \'Yes\' если по графику, или \'No\' если это выходной день? ')

            if x == "1":
                local_marker = False
            elif x == "0":
                data_update = f"""
UPDATE working_date
SET personal_day_off = 1
WHERE wd_date = '{wd_date}';
"""
                cursor.execute(data_update)
                connection.commit()
                local_marker = False

        # меняем МАЗ, если требуется:
        local_marker = True  # маркер цикла
        while local_marker:
            print(f"\n Вы работали на длинной машине, или с короткой базой?\n")
            # Выбор пункта меню:
            x = yes_no_input('введите \'Yes\' если был МАЗ 105(215), или \'No\' если был МАЗ 107(103)? ')

            if x == "1":
                local_marker = False
            elif x == "0":
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
        local_marker = True  # маркер цикла
        while local_marker:
            print(f"\nБыла ли произведена замена {wd_date} с рабочего на выходной или обратно? \n")
            # Выбор пункта меню:
            x = yes_no_input('введите \'Yes\' или \'No\'. ')

            if x == "1":
                holiday = int(input("""Введите 1, если выходной день заменяется на рабочий,
        6, если рейсы в будний день ходят по расписанию субботы,
        7, если рейсы в будний день ходят по расписанию воскресенья: """))
                data_update = f"""
UPDATE working_date
SET holiday = {holiday}
WHERE wd_date = '{wd_date}';
"""
                cursor.execute(data_update)
                connection.commit()
                local_marker = False
            elif x == "0":
                local_marker = False

        # вставка данных о больничном:
        local_marker = True  # маркер цикла
        while local_marker:
            print(f"\n Желаете ли добавить данные о больничном? \n")
            # Выбор пункта меню:
            x = yes_no_input('введите \'Yes\' или \'No\'. ')

            if x == "1":
                data_from_sick_leave()  # определяются переменные больничного листа

                cursor.execute(data_insertion)
                connection.commit()
                print("sick_leave inserted successfully")

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


connect_postgres()
