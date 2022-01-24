SET search_path TO bus_depot_1, public;

-- обычный день, проверяем наличие:
SELECT shrr_id FROM shift_route_round
WHERE shift = 2 AND route = '18' AND round = 17;

-- в случае отсутсвия оф."выхода" ('21', '52'), устанавливать номер от 1 и выше:
SELECT * FROM shift_route_round WHERE shift = 2 AND route = '21';

-- если нет, добавляем:
INSERT INTO shift_route_round (shift, route, round )
    VALUES (2, '17', 13);   -- буквенные маршруты дописывать кирилицей

-- данные с путевого и була:
INSERT INTO working_date (wd_date, shrr_id, proceeds, number_of_flights, waybill,
                          start_of_time, end_of_time, time_duration)
    VALUES ('2021-10-31', 17, 171.50 /*выручка*/, '6+1', 90001, '14:06', '21:09', '7:03');

UPDATE working_date
    SET proceeds = 166.6
    WHERE wd_date = '2021-10-21';

-- добавляем заметки, если требуется:
UPDATE working_date
    SET note = 'На вторую смену (маршрут 17) дали двухдверный МАЗ-103!!!'
    WHERE wd_date = '2021-10-20' AND shrr_id = 38;

-- проездные, если требуется:
INSERT INTO ticket VALUES ('2021-11-07', 1, 1, NULL, NULL);

-- резерв, если требуется:
INSERT INTO reserve VALUES('2021-09-28', '13:00', '14:00', NULL /*'...or some comment'*/);


 -- плановые задания по выручке:
SELECT * FROM planned_tasks_for_revenue
    WHERE shrr_id = 58 AND EXTRACT(month FROM ptfr_date) = 11;
INSERT INTO planned_tasks_for_revenue
    VALUES ('2021-11-01' /*менять только месяц*/, 7 /*shrr_id*/, 177.16 /*будни*/,
                                                NULL /*сб*/, NULL /* вс*/, NULL /*modified_plan*/);
UPDATE planned_tasks_for_revenue
    SET plan_weekday = NULL
    WHERE shrr_id = 58 AND EXTRACT(month FROM ptfr_date) = 11;

-- графики рейсов по плану:
SELECT * FROM planned_schedule WHERE shrr_id = 59;
INSERT INTO planned_schedule (shrr_id, week_id,
                              start_of_time, end_of_time, time_duration,
                              second_start_of_time, second_end_of_time, second_time_duration,
                              number_of_flights)
    VALUES (59, 1 /*or 2 - day off*/, '15:46', '1:31', '9:15',
            /*'16:16', '19:07', '2:51',*/ NULL, NULL, NULL, '8+1');
UPDATE planned_schedule
    SET time_duration = '8:04'
    WHERE shrr_id = 51;

-- при наличии доп маршрутов:
SELECT * FROM flight
WHERE psch_id IN (SELECT psch_id FROM planned_schedule WHERE shrr_id = 29) AND
      EXTRACT(month FROM f_date) = 8;

INSERT INTO flight (psch_id, flight, plan, number_of_flights, f_date) 
    VALUES (13, '21в', 24.15, '1', '2021-10-01');  -- буквенные маршруты дописывать кирилицей

-- работа в собственный выходной:
UPDATE working_date
    SET personal_day_off = 1
    WHERE wd_date = '2021-11-01';
SELECT * FROM working_date WHERE wd_date = '2021-11-01';

-- меняем МАЗ, если требуется:
UPDATE working_date
    SET bus_id = 2
    WHERE wd_date = '2021-11-08' AND shrr_id = 7;

-- замена рабочего дня на выходной и обратно:
UPDATE working_date
    SET holiday = 1  -- 1-рабочий день, 6-сб, 7-вс -?
    WHERE wd_date = '2021-09-06';
    
-- вставка данных о больничном:
SELECT * FROM sick_leave;
INSERT INTO sick_leave (start_of_date, end_of_date, note)
    VALUES ('2021-09-06', '2021-09-18', '');
