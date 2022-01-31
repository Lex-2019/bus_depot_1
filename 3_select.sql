SET search_path TO bus_depot_1, public;

SELECT * FROM shift_route_round;
SELECT wd_date, shrr_id, proceeds FROM working_date WHERE EXTRACT(months FROM wd_date) = 11;
SELECT * FROM planned_tasks_for_revenue WHERE EXTRACT(months FROM ptfr_date) = 10;
SELECT * FROM ticket WHERE EXTRACT(months FROM t_date) = 11;
SELECT * FROM planned_schedule WHERE shrr_id = 20;
SELECT shrr_id FROM planned_schedule GROUP BY shrr_id HAVING COUNT(psch_id) >1;
SELECT * FROM reserve WHERE EXTRACT(months FROM r_date) = 10;
SELECT * FROM planned_schedule;
SELECT * FROM flight;

-- для сравнения с распечаткой в конторе:
SELECT sum(plan) AS "план", sum(proceeds) AS "выручка", (sum(proceeds) - sum(plan)) AS "отклонение",
       CAST((sum(proceeds) * 100 / sum(plan)) AS DECIMAL(4,1)) AS "% выполнения плана",
       sum(CAST(time_duration AS INTERVAL)) AS "итого время"
FROM (
	SELECT wd_date, proceeds, time_duration,
		CASE
		-- день недели, считая с понедельника (1) до воскресенья (7)
		-- учесть праздничные дни и отработки в будни !!!!!!!!!
		-- заменить на проверку соответствия количества маршрутов в плане и фактически,
		-- а так же какая машина - 105 или 107 маз
			WHEN EXTRACT(isodow FROM wd_date) = 6 AND modified_plan IS NULL
				THEN "plan_saturday"
			WHEN EXTRACT(isodow FROM wd_date) = 7 AND modified_plan IS NULL
				THEN "plan_sunday"
			WHEN EXTRACT(isodow FROM wd_date) BETWEEN 1 AND 5 AND modified_plan IS NULL
				THEN "plan_weekday"
			ELSE modified_plan
		END plan
	FROM working_date AS wd
	LEFT JOIN shift_route_round AS shrr
		ON wd.shrr_id = shrr.shrr_id
	RIGHT JOIN planned_tasks_for_revenue AS ptfr
		ON shrr.shrr_id = ptfr.shrr_id
	WHERE EXTRACT(month FROM wd_date) = 10 AND EXTRACT(month FROM ptfr_date) = 10 -- изменять согласно необходимому месяцу
) plan_of_the_month;

-- по дням:
SELECT wd_date, plan, proceeds,
       CAST((proceeds * 100 / plan) AS DECIMAL(4,1)) AS PERCENT,
       time_duration
FROM (
	SELECT DISTINCT wd_date, proceeds, wd.time_duration,
		CASE
		-- день недели, считая с понедельника (1) до воскресенья (7)
            WHEN EXTRACT(isodow FROM wd_date) = 6 AND modified_plan IS NULL -- AND ps.number_of_flights <> wd.number_of_flights
                THEN plan_saturday
            WHEN EXTRACT(isodow FROM wd_date) = 7 AND modified_plan IS NULL -- AND ps.number_of_flights <> wd.number_of_flights
                THEN plan_sunday
            WHEN EXTRACT(isodow FROM wd_date) BETWEEN 1 AND 5 AND modified_plan IS NULL -- AND ps.number_of_flights <> wd.number_of_flights
                THEN plan_weekday
            ELSE modified_plan
		END plan
	FROM working_date AS wd
	LEFT JOIN shift_route_round AS shrr
		ON wd.shrr_id = shrr.shrr_id
	RIGHT JOIN planned_tasks_for_revenue AS ptfr
		ON shrr.shrr_id = ptfr.shrr_id
	/*JOIN planned_schedule AS ps
	    ON shrr.shrr_id = ps.shrr_id */
    WHERE EXTRACT(month FROM wd_date) = 10 AND EXTRACT(month FROM ptfr_date) = 10 -- изменять согласно необходимому месяцу
) plan_of_the_month
ORDER BY wd_date;

-- проданные проездные:
SELECT SUM(decade_only_b) AS "декада автобус",
       SUM(decade_b_and_t) AS "декада общий",
       SUM(month_only_b) AS "месяц автобус",
       SUM(month_b_and_t) AS "месяц общий"
FROM ticket WHERE EXTRACT(month FROM t_date) = 10; -- изменять согласно необходимому месяцу

-- по дням:
SELECT t_date,
       to_char(t_date, 'Day') AS weekday, 
       decade_only_b AS "декада автобус",
       decade_b_and_t AS "декада общий",
       month_only_b AS "месяц автобус",
       month_b_and_t AS "месяц общий"
FROM ticket
LEFT JOIN working_date AS wd
    ON t_date = wd_date
/*JOIN shift_route_round AS shrr
    ON wd.shrr_id = shrr.shrr_id*/
WHERE EXTRACT(month FROM t_date) = 10 -- изменять согласно необходимому месяцу
GROUP BY t_date
ORDER BY t_date;
