SET search_path TO bus_depot_1, public;

-- обычный день, проверяем наличие:
SELECT shrr_id FROM shift_route_round
WHERE shift = 2 AND route = '17' AND round = 15;

-- в случае отсутсвия оф."выхода" ('21', '52'), устанавливать номер от 1 и выше:
SELECT * FROM shift_route_round WHERE shift = 1 AND route = '21';

-- если нет, добавляем:
INSERT INTO shift_route_round (shift, route, round )
    VALUES (2, '17', 13);   -- буквенные маршруты дописывать кирилицей

-- данные с путевого и була:
SELECT * FROM working_date WHERE shrr_id = 53 ORDER BY wd_date;
INSERT INTO working_date (wd_date, shrr_id, proceeds, number_of_flights, waybill,
                          start_of_time, end_of_time, time_duration)
    VALUES ('2021-10-31', 17, 171.50 /*выручка*/, '6+1', 90001, '14:06', '21:09', '7:03');

UPDATE working_date
    SET modified_plan = 124.74 -- end_of_time = '12:09'
    WHERE shrr_id = 53 AND wd_date = '2021-10-08';

-- добавляем заметки, если требуется:
UPDATE working_date
    SET note = 'торой промежуток резерва с 17:09 до 19:13 - длительность 1:04'
    WHERE wd_date = '2022-01-02' AND shrr_id = 75;

-- проездные, если требуется:
INSERT INTO ticket VALUES ('2022-03-06', 1, 1, NULL, NULL);

SELECT * FROM ticket WHERE t_date = '2022-02-09';
UPDATE ticket
    SET decade_only_b = 10
    WHERE t_date = '2022-02-09';

-- резерв, если требуется:
INSERT INTO reserve VALUES('2022-01-02', '17:09', '19:13', NULL /*'...or some comment'*/);
SELECT * FROM reserve r ORDER BY reserve_id;
UPDATE reserve
    SET note = NULL
    WHERE r_date = '2022-01-02';

 -- плановые задания по выручке:
SELECT * FROM planned_tasks_for_revenue
    WHERE shrr_id = 53 AND EXTRACT(month FROM ptfr_date) = 10;

INSERT INTO planned_tasks_for_revenue
    VALUES ('2022-03-01' /*менять только месяц*/, 80 /*shrr_id*/, NULL /*будни*/,
                                                NULL /*сб*/, 108.5 /* вс*/);
UPDATE planned_tasks_for_revenue
    SET modified_plan = 134.66
    WHERE shrr_id = 13 AND EXTRACT(month FROM ptfr_date) = 1;

-- графики рейсов по плану:
SELECT * FROM planned_schedule WHERE shrr_id = 13;
INSERT INTO planned_schedule (shrr_id, week_id,
                              start_of_time, end_of_time, time_duration,
                              second_start_of_time, second_end_of_time, second_time_duration,
                              number_of_flights)
    VALUES (80, 2 /*or 2 - day off*/, '14:55', '1:28', '9:48',
            /*'16:16', '19:07', '2:51',*/ NULL, NULL, NULL, '10+1');
UPDATE planned_schedule
    SET time_duration = '8:04'
    WHERE shrr_id = 51;

-- при наличии доп маршрутов:
SELECT * FROM flight
WHERE psch_id IN (
                  SELECT psch_id FROM planned_schedule WHERE shrr_id = 37 AND week_id = 2
      ) AND EXTRACT(month FROM f_date) = ;
SELECT psch_id FROM planned_schedule WHERE shrr_id = 37 AND week_id = 1;
INSERT INTO flight (psch_id, flight, plan, number_of_flights, f_date) 
    VALUES (99, '21в', 13.3, '1+1', '2022-02-10');  -- буквенные маршруты дописывать кирилицей

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
    
-- вставка данных о больничном:
SELECT * FROM sick_leave;
INSERT INTO sick_leave (start_of_date, end_of_date, note)
    VALUES ('2021-09-06', '2021-09-18', '');
