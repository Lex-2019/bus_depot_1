SET search_path TO bus_depot_1, public;

-- обычный день, проверяем наличие:
SELECT shrr_id FROM shift_route_round
WHERE shift = 2 AND route = '18' AND round = 17;

-- в случае отсутсвия оф."выхода" ('21', '52'), устанавливать номер от 1 и выше:
SELECT * FROM shift_route_round WHERE shift = 1 AND route = '21';

-- если нет, добавляем:
INSERT INTO shift_route_round (shift, route, round )
    VALUES (1, '21', 3);   -- буквенные маршруты дописывать кирилицей

-- данные с путевого и була:
SELECT * FROM working_date WHERE shrr_id = 59 ORDER BY wd_date;
INSERT INTO working_date (wd_date, shrr_id, proceeds, number_of_flights, waybill,
                          start_of_time, end_of_time, time_duration)
    VALUES ('2021-10-31', 17, 171.50 /*выручка*/, '6+1', 90001, '14:06', '21:09', '7:03');

UPDATE working_date
    SET modified_plan = 86.94
    WHERE wd_date = '2022-02-28'; AND shrr_id = 13;

-- ...корректировка планов по окончании месяца...
SELECT wd_date, working_date.shrr_id, plan_weekday, plan_saturday, plan_sunday, modified_plan
FROM working_date
JOIN planned_tasks_for_revenue
    ON working_date.shrr_id = planned_tasks_for_revenue.shrr_id
WHERE EXTRACT(month FROM wd_date) = 4 AND EXTRACT(month FROM ptfr_date) = 4  ORDER BY wd_date;
UPDATE working_date
    SET modified_plan = 125.0
    WHERE wd_date = '2022-04-06' AND shrr_id = 89;
-- ...корректировка планов в доп маршрутах...
SELECT * FROM flight WHERE f_date = '2022-03-01';

-- добавляем заметки, если требуется:
UPDATE working_date
    SET note = 'отработка за 24-е (я отпросился в обл.больницу)'
    WHERE wd_date = '2022-03-25' AND shrr_id = 75;

-- проездные, если требуется:
INSERT INTO ticket VALUES ('2022-04-12', 1, NULL, NULL, NULL);

SELECT * FROM ticket WHERE t_date = '2022-04-12';
UPDATE ticket
    SET decade_only_b = 1
    WHERE t_date = '2022-04-12';

 -- плановые задания по выручке:
SELECT * FROM planned_tasks_for_revenue
    WHERE shrr_id = 21 AND EXTRACT(month FROM ptfr_date) = 4;

INSERT INTO planned_tasks_for_revenue
    VALUES ('2022-02-01' /*менять только месяц*/, 92 /*shrr_id*/, 94.5 /*будни*/,
                                                NULL /*сб*/, NULL /* вс*/);
UPDATE planned_tasks_for_revenue
    SET plan_saturday = 137.2
    WHERE shrr_id = 21 AND EXTRACT(month FROM ptfr_date) = 4;

-- графики рейсов по плану:
SELECT * FROM planned_schedule WHERE shrr_id = 19;
INSERT INTO planned_schedule (shrr_id, week_id,
                              start_of_time, end_of_time, time_duration,
                              second_start_of_time, second_end_of_time, second_time_duration,
                              number_of_flights)
    VALUES (92, 1 /*or 2 - day off*/, '6:14', '13:40', '6:54',
            /*'16:16', '19:07', '2:51',*/ NULL, NULL, NULL, '6+1');
UPDATE planned_schedule
    SET time_duration = '8:04'
    WHERE shrr_id = 51;

-- при наличии доп маршрутов:
SELECT * FROM flight
WHERE psch_id IN (
                  SELECT psch_id FROM planned_schedule WHERE shrr_id = 95 AND week_id = 1
      ) AND EXTRACT(month FROM f_date) = 3;
SELECT psch_id FROM planned_schedule WHERE shrr_id = 95 AND week_id = 1;
INSERT INTO flight (psch_id, flight, plan, number_of_flights, f_date) 
    VALUES (111, '13а', 39.9, '3+1', '2022-03-23');  -- буквенные маршруты дописывать кирилицей

-- работа в собственный выходной:
UPDATE working_date
    SET personal_day_off = 1
    WHERE wd_date = '2022-02-22';
SELECT * FROM working_date WHERE wd_date = '2022-02-22';

-- меняем МАЗ, если требуется:
UPDATE working_date
    SET bus_id = 2
    WHERE wd_date = '2021-11-08' AND shrr_id = 10 AND proceeds = 88.2;

-- замена рабочего дня на выходной и обратно:
UPDATE working_date
    SET holiday = 1  -- 1-рабочий день, 6-сб, 7-вс -?
    WHERE wd_date = '2021-09-06';

-- резерв, если требуется:
INSERT INTO reserve VALUES('2022-05-02', '5:00', '13:00', NULL /*'...or some comment'*/);
SELECT * FROM reserve r ORDER BY reserve_id;
UPDATE reserve
    SET note = NULL
    WHERE r_date = '2022-01-02';

-- вставка данных о больничном:
SELECT * FROM sick_leave;
INSERT INTO sick_leave (start_of_date, end_of_date, note)
    VALUES ('2021-09-06', '2021-09-18', '');
