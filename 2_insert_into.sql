SET search_path TO bus_depot_1, public;

-- обычный день, проверяем наличие:
SELECT shrr_id FROM shift_route_round
WHERE shift = 2 AND route = '26' AND round = 12;

-- в случае отсутсвия оф."выхода" ('21', '52'), устанавливать номер от 1 и выше:
SELECT * FROM shift_route_round WHERE shift = 1 AND route = '21';

-- если нет, добавляем:
INSERT INTO shift_route_round (shift, route, round )
    VALUES (2, '17', 13);   -- буквенные маршруты дописывать кирилицей

-- данные с путевого и була:
SELECT * FROM working_date WHERE shrr_id = 42;
INSERT INTO working_date (wd_date, shrr_id, proceeds, number_of_flights, waybill,
                          start_of_time, end_of_time, time_duration)
    VALUES ('2021-10-31', 17, 171.50 /*выручка*/, '6+1', 90001, '14:06', '21:09', '7:03');

UPDATE working_date
    SET proceeds = 166.6
    WHERE wd_date = '2021-10-21';

-- добавляем заметки, если требуется:
UPDATE working_date
    SET note = 'отработка за вторник'
    WHERE wd_date = '2021-12-19' AND shrr_id = 9;

-- проездные, если требуется:
INSERT INTO ticket VALUES ('2021-12-02', 1, NULL, 1, NULL);

-- резерв, если требуется:
INSERT INTO reserve VALUES('2021-11-23', '5:00', '6:25', NULL /*'...or some comment'*/);
SELECT * FROM reserve r ;

 -- плановые задания по выручке:
SELECT * FROM planned_tasks_for_revenue
    WHERE shrr_id = 12 AND EXTRACT(month FROM ptfr_date) = 12;
INSERT INTO planned_tasks_for_revenue
    VALUES ('2021-11-01' /*менять только месяц*/, 62 /*shrr_id*/, 143.6 /*будни*/,
                                                NULL /*сб*/, NULL /* вс*/, NULL /*modified_plan*/);
UPDATE planned_tasks_for_revenue
    SET plan_weekday = NULL
    WHERE shrr_id = 9 AND EXTRACT(month FROM ptfr_date) = 12;

-- графики рейсов по плану:
SELECT * FROM planned_schedule WHERE shrr_id = 42;
INSERT INTO planned_schedule (shrr_id, week_id,
                              start_of_time, end_of_time, time_duration,
                              second_start_of_time, second_end_of_time, second_time_duration,
                              number_of_flights)
    VALUES (42, 2 /*or 2 - day off*/, '6:01', '14:45', '8:04',
            /*'16:16', '19:07', '2:51',*/ NULL, NULL, NULL, '8+1');
UPDATE planned_schedule
    SET time_duration = '8:04'
    WHERE shrr_id = 51;

-- при наличии доп маршрутов:
SELECT * FROM flight
WHERE psch_id IN (
                  SELECT psch_id FROM planned_schedule WHERE shrr_id = 73 AND week_id = 1
      ) AND EXTRACT(month FROM f_date) = 12;
SELECT psch_id FROM planned_schedule WHERE shrr_id = 73 AND week_id = 1;
INSERT INTO flight (psch_id, flight, plan, number_of_flights, f_date) 
    VALUES (89, '55', 21.7, '2', '2021-12-01');  -- буквенные маршруты дописывать кирилицей

-- работа в собственный выходной:
UPDATE working_date
    SET personal_day_off = 1
    WHERE wd_date = '2021-12-27';
SELECT * FROM working_date WHERE wd_date = '2021-12-27';

-- меняем МАЗ, если требуется:
UPDATE working_date
    SET bus_id = 2
    WHERE wd_date = '2021-11-08' AND shrr_id = 10 AND proceeds = 88.2;

-- замена рабочего дня на выходной и обратно:
UPDATE working_date
    SET holiday = 1  -- 1-рабочий день, 6-сб, 7-вс -?
    WHERE wd_date = '2021-09-06';
    
-- вставка данных о больничном:
SELECT * FROM sick_leave;
INSERT INTO sick_leave (start_of_date, end_of_date, note)
    VALUES ('2021-09-06', '2021-09-18', '');
