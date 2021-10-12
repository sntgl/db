import psycopg2


task = ["",  """
--1 Все владельцы машин младше меня
SELECT * FROM lab.owner WHERE date_birth > '2001-08-19'
""" , """
--2 Камеры, установленные в 2010 году
SELECT * FROM lab.camera WHERE date_added BETWEEN '2010-01-01' AND '2010-12-31'
""", """
--3 Автомобили с номерами региона 159
SELECT * FROM lab.car WHERE car.plate LIKE '% 159'
""", """
--4 Владельцы, оштрафованные за 12.9.5 (более 80 км/ч)
SELECT owner_id, first_name, last_name
FROM lab.owner 
WHERE owner_id IN (
    SELECT car_id
    FROM lab.fine
    WHERE article_id IN (
        SELECT article_id
        FROM lab.article
        WHERE article_number = '12.9.5'
    )
)
""", """
--5 Автомобили с количеством штрафов > 10
SELECT car_id as cid, model
FROM lab.car as car1
WHERE EXISTS (
    SELECT car_id
    FROM (
        SELECT COUNT(*) as cnt, car_id
        FROM lab.fine
        GROUP BY car_id
    ) as fc
    WHERE cnt > 10 AND car1.car_id = fc.car_id
)
""", """
--6 Автомобили, зарегистрированные после добавления камер *условие*
SELECT *
FROM lab.car
WHERE reg_date > ALL (
    SELECT date_added
    FROM lab.camera
    WHERE latitude BETWEEN 55.5 AND 55.7 AND 
        longitude BETWEEN 37.4 AND 37.6
)
""", """
--7 Среднее и общее количество штрафов у автовладельца для каждого авто
SELECT owner_id, AVG(finesCount), SUM(finesCount), COUNT(*)
FROM (
    lab.car tb1 LEFT JOIN (
        SELECT count(*)  as finesCount, car_id
        FROM lab.fine
        GROUP BY car_id
    ) tb2
    ON tb2.car_id = tb1.car_id
)
GROUP BY owner_id
""", """
--8 Количество штрафов у авто выпуска 2013г (есть хотя бы один)
SELECT car_id, owner_id, model, plate, (
    SELECT COUNT(*)
    FROM lab.fine
    WHERE car_id = cid.car_id
)
FROM lab.car as cid
WHERE issue_year = 2013
""","""
--9 Как давно выпущено авто, зарегистрированные в этом году?
SELECT car_id, owner_id, model, issue_year, 
    CASE car.issue_year
        WHEN date_part('year', CURRENT_DATE) THEN 'This year'
        WHEN date_part('year', CURRENT_DATE) - 1 THEN 'Last year'
        ELSE CONCAT(CAST(date_part('year', CURRENT_DATE) - car.issue_year AS TEXT), ' years ago')
        END
    as actual
FROM lab.car
WHERE date_part('year', reg_date) = date_part('year', CURRENT_DATE)
""", """
--10 Является ли авто темно-зеленого цвета актуальным для Trade-in (младше 8 лет)
SELECT car_id, owner_id, model, issue_year, 
    CASE 
        WHEN date_part('year', CURRENT_DATE) - car.issue_year < 8 THEN 'YES'
        ELSE 'NO'
        END
    as valid
FROM lab.car
WHERE color = 'Темно-зеленый'
""", """
--11 Предыдущий запрос в локальной временной таблице
CREATE TEMP TABLE my_table_name AS
SELECT car_id, owner_id, model, issue_year, 
    CASE 
        WHEN date_part('year', CURRENT_DATE) - car.issue_year < 8 THEN 'YES'
        ELSE 'NO'
        END
    as valid
FROM lab.car
WHERE color = 'Темно-зеленый';

SELECT * FROM my_table_name
""", """
--12 Самый популярный авто по количеству штрафов и по количеству экземпляров
(SELECT model as Model, COUNT(*) as ByCount
FROM lab.car
GROUP BY model
ORDER BY ByCount DESC LIMIT 1)
UNION
(SELECT tb3.model as Model, SUM(coalesce(finesCount,0)) as ByFinesAvg
FROM (
    lab.car tb1 LEFT JOIN (
        SELECT count(*)  as finesCount, car_id
        FROM lab.fine
        GROUP BY car_id
    ) tb2
    ON tb2.car_id = tb1.car_id
) tb3
GROUP BY tb3.model
ORDER BY ByFinesAvg DESC LIMIT 1)
""", """
--13 Все авто модели, самой популярной по штрафам
CREATE TEMP TABLE car_fines AS
SELECT *
FROM
(
    lab.car tb1 LEFT JOIN (
    SELECT count(*)  as finesCount, car_id as cid
    FROM lab.fine
    GROUP BY car_id
    ) tb2
    ON tb2.cid = tb1.car_id
);
SELECT finesCount, car_id, owner_id, color, plate, model
FROM car_fines
WHERE model = (
    SELECT model
    FROM (
        SELECT SUM(coalesce(finesCount,0)) fk, model
        FROM car_fines
        GROUP BY model
        ORDER BY fk DESC
        LIMIT 1) as fm)
""", """
--14 
SELECT owner_id, SUM(coalesce(finesCount, 0)), COUNT(*), AVG(coalesce(finesCount, 0))
FROM
(
    lab.car tb1 LEFT JOIN (
    SELECT count(*)  as finesCount, car_id as cid
    FROM lab.fine
    GROUP BY car_id
    ) tb2
    ON tb2.cid = tb1.car_id
) tb
WHERE model = 'BMW 5 Series'
GROUP BY owner_id
""", """
--15
SELECT owner_id, SUM(coalesce(finesCount, 0)) AS sm, COUNT(*), AVG(coalesce(finesCount, 0))
FROM
(
    lab.car tb1 LEFT JOIN (
    SELECT count(*)  as finesCount, car_id as cid
    FROM lab.fine
    GROUP BY car_id
    ) tb2
    ON tb2.cid = tb1.car_id
) tb
GROUP BY owner_id
HAVING SUM(coalesce(finesCount, 0)) > 10
""", """
--16
INSERT INTO lab.article (article_id, department, article_number, description, amount)
VALUES (12, 'КОАП РФ', '2.2.8', 'Езда по пешеходам', '200')
""", """
--17
INSERT INTO lab.article (article_id, department, article_number, description, amount)
SELECT (SELECT article_id FROM lab.article ORDER BY article_id DESC LIMIT 1) + 1, department, article_number, description, amount
FROM lab.article
WHERE article_id = 10
""", """
--18
UPDATE lab.article
SET amount = 999
WHERE article_id = 12
""", """
--19
UPDATE lab.article
SET amount = (SELECT AVG(amount) FROM lab.article)
WHERE article_id = 12
""", """
--20
DELETE FROM lab.article
WHERE article_id > 11
""", """
--21 Удаление всех неиспользованных статей
DELETE FROM lab.article
WHERE article_id NOT IN (
    SELECT article_id
    FROM lab.fine
    GROUP BY article_id
)
""", """
--22 Среднее количество штрафов у всех водителей
WITH CTE (owner_id, fines_count) AS (
    SELECT owner_id, count(coalesce(tb2.finesCount, 0))
    FROM (
        lab.car tb1 LEFT JOIN (
        SELECT count(*)  as finesCount, car_id as cid
        FROM lab.fine
        GROUP BY car_id
        ) tb2
        ON tb2.cid = tb1.car_id
    )
    GROUP BY owner_id
)
SELECT AVG(fines_count)
FROM CTE
""", """
--23 Количество вложенности начальников)
DROP TABLE IF EXISTS lab.OTB_TEST;
-- Создание таблицы.
CREATE TABLE lab.OTB_TEST (
EmployeeID smallint NOT NULL,
FirstName text NOT NULL,
LastName text NOT NULL,
Title text NOT NULL,
ManagerID int NULL,
CONSTRAINT PK_EmployeeID PRIMARY KEY (EmployeeID)
);
-- Заполнение таблицы значениями.
INSERT INTO lab.OTB_TEST
VALUES (1, N'Иван', N'Петров', N'Главный исполнительный директор',NULL),
(2, N'Иван', N'Собакин', N'Зам. глав. исп. директора',1),
(3, N'Иван', N'Кошкин', N'Главный бухгалтер',2),
(4, N'Иван', N'Иванов', N'Бухгалтер',3),
(5, N'Иван', N'Максимов', N'Младший бухгалтер',4),
(6, N'Иван', N'Главный', N'Старший менеджер',1),
(7, N'Иван', N'Большой', N'Младший менеджер',6),
(8, N'Иван', N'Небольшой', N'Младший менеджер',6)
; 
-- Определение ОТВ
WITH RECURSIVE OTB (ManagerID, EmployeeID, Title, Level) AS
(
    -- Закрепленный
    SELECT ManagerID, EmployeeID, Title, 0 AS Level FROM lab.OTB_TEST
    WHERE ManagerID IS NULL
    UNION ALL
    -- Рекурсивный
    SELECT tb.ManagerID, tb.EmployeeID, tb.Title, d.Level + 1 FROM lab.OTB_TEST AS tb INNER JOIN OTB AS d
    ON tb.ManagerID = d.EmployeeID
)
-- Инструкция, использующая ОТВ
SELECT ManagerID, EmployeeID, Title, Level FROM OTB;
""", """
--24 К кадждому авто добавить среднее, мин, макс количества штрафов по модели
SELECT car_id, model, plate,
    AVG(cnt) OVER (PARTITION BY model) as AvgModelFines,
    MIN(cnt) OVER (PARTITION BY model) as AvgModelFines,
    MAX(cnt) OVER (PARTITION BY model) as AvgModelFines
FROM (
    SELECT car_id,finesCount as cnt, model, plate
    FROM (
        lab.car tb1 LEFT JOIN (
        SELECT count(*)  as finesCount, car_id as cid
        FROM lab.fine
        GROUP BY car_id
        ) tb2
        ON tb2.cid = tb1.car_id
    )
) as cicm
""", """
--25 Количество вложенности начальников)
DROP TABLE IF EXISTS lab.OTB_TEST;
-- Создание таблицы.
CREATE TABLE lab.OTB_TEST (
EmployeeID smallint NOT NULL,
FirstName text NOT NULL,
LastName text NOT NULL,
Title text NOT NULL,
ManagerID int NULL
);
-- Заполнение таблицы значениями.
INSERT INTO lab.OTB_TEST
VALUES (1, N'Иван', N'Петров', N'Главный исполнительный директор',NULL),
(2, N'Иван', N'Собакин', N'Зам. глав. исп. директора',1),
(3, N'Иван', N'Кошкин', N'Главный бухгалтер',2),
(4, N'Иван', N'Иванов', N'Бухгалтер',3),
(5, N'Иван', N'Максимов', N'Младший бухгалтер',4),
(6, N'Иван', N'Главный', N'Старший менеджер',1),
(6, N'Иван', N'Сильный', N'Просто менеджер',1),
(7, N'Иван', N'Большой', N'Младший менеджер',6),
(8, N'Иван', N'Небольшой', N'Младший менеджер',6),
(8, N'Иван', N'Небольшой', N'Младший менеджер',6),
(8, N'Иван', N'Небольшой', N'Младший менеджер',6)
; 
-- по ID + фамилии
delete from lab.OTB_TEST where EmployeeID in (
    select EmployeeID from (
        select EmployeeID,
        row_number() over (partition by EmployeeID, LastName order by EmployeeID)  rn
        from lab.OTB_TEST
    ) a 
    where a.rn >1 );
SELECT * FROM lab.OTB_TEST;
""", """
--Камера с наибольшим количеством штрафов на Ford
SELECT camera_id, COUNT(*) cnt
FROM (
    (SELECT * FROM lab.car WHERE model LIKE '%Ford%') lc JOIN lab.fine lf
    ON lf.car_id = lc.car_id
)
GROUP BY camera_id
ORDER BY cnt DESC
""", """
--Дополнительное
-- Создание начальных таблиц
DROP SCHEMA IF EXISTS lab_02 CASCADE;
CREATE SCHEMA IF NOT EXISTS lab_02;

CREATE TABLE IF NOT EXISTS lab_02.table1
(
 id INTEGER,
 var TEXT,
 valid_from_dttm DATE,
 valid_to_dttm DATE
);

CREATE TABLE IF NOT EXISTS lab_02.table2
(
 id INTEGER,
 var TEXT,
 valid_from_dttm DATE,
 valid_to_dttm DATE
);

--Добавляем данные
INSERT INTO lab_02.table1 (id, var, valid_from_dttm, valid_to_dttm)
VALUES (1, 'A', '2018-09-01', '2018-09-15'),
 (1, 'B', '2018-09-16', '5999-12-31');

INSERT INTO lab_02.table2 (id, var, valid_from_dttm, valid_to_dttm)
VALUES (1, 'A', '2018-09-01', '2018-09-18'),
 (1, 'B', '2018-09-19', '5999-12-31');

--Сливаем в одну

SELECT t1.id AS id, t1.var AS var1, t2.var AS var2,
CASE
    WHEN t1.valid_from_dttm >= t2.valid_from_dttm THEN t1.valid_from_dttm
    ELSE t2.valid_from_dttm
END,
CASE 
    WHEN t1.valid_to_dttm <= t2.valid_to_dttm THEN t1.valid_to_dttm
    ELSE t2.valid_to_dttm
END
FROM lab_02.table1 AS t1 JOIN lab_02.table2 AS t2 ON t2.id = t1.id
WHERE t1.valid_from_dttm <= t2.valid_to_dttm AND t2.valid_from_dttm <= t1.valid_to_dttm;

"""]

"""
-- по ID
delete from lab.OTB_TEST where EmployeeID in (
    select EmployeeID from (
        select EmployeeID,
        row_number() over (partition by EmployeeID order by EmployeeID)  rn
        from lab.OTB_TEST
    ) a where a.rn >1 );
SELECT * FROM lab.OTB_TEST;

"""

conn = psycopg2.connect("dbname=postgres user=postgres password='123'")
conn.autocommit = True
try:
    cur = conn.cursor()
    # cur.execute(open("create.sql", 'r').readlines())
    # cur.execute(open("created/create.sql", "r").read())
    cur.execute(task[-1])
    for i in (cur.fetchall()):
        print(i)
    cur.close()
    conn.commit()
except (Exception, psycopg2.DatabaseError) as error:
    print(error)
finally:
    if conn is not None:
        conn.close()