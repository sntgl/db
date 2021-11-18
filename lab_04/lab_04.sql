--Лаба 4

CREATE LANGUAGE plpython3u;

--1
--Определяемую пользователем скалярную функцию CLR
--имя по ID owner'a
create or replace function get_name_by_id(id_ int) returns varchar
as $$
ppl = plpy.execute("select * from lab.owner")
for person in ppl:
	if person['owner_id'] == id_:
		return person['first_name']
return 'None'
$$ language plpython3u;

select get_name_by_id(15);

--2
--Пользовательскую агрегатную функцию CLR
--количество авто у владельца по owner_id
create or replace function get_count_cars_by_id(id_ int) returns varchar
as $$
summ = 0
ppl = plpy.execute("select * from lab.car")
for car in ppl:
	if car['owner_id'] == id_:
		summ+=1
return summ
$$ language plpython3u;

select get_count_cars_by_id(41);

--3
--Определяемую пользователем табличную функцию CLR
--все авто у владельца по owner_id
DROP FUNCTION get_cars_by_id(integer);
create or replace function get_cars_by_id(id_ int) returns table(car_id int, owner_id int, model text, color text, plate text, vin text, reg_certificate numeric(10), reg_date text, issue_year numeric(4))
as $$
cars = []
ppl = plpy.execute("select * from lab.car")
for car in ppl:
	if car['owner_id'] == id_:
		cars.append(car)
return cars
$$ language plpython3u;

select * from get_cars_by_id(41);

--4
--Хранимую процедуру CLR
--добавляет статью штрафа
create or replace procedure add_article(article_id int, department text, article_number text, description text, amount int) as
$$
plan = plpy.prepare("insert into lab.article(article_id, department, article_number, description, amount) values($1, $2, $3, $4, $5);", ["int", "text", "text", "text", "int"])
plpy.execute(plan, [article_id,  department,  article_number, description, amount])
$$ language plpython3u;

call add_article(20, 'Управление по управлению всеми управлениями', '2.2.8', 'test', 100000);


--5
--Триггер CLR
--при удалении статьи штрафа она добавляется в таблицу old (что-то типа корзины)
drop table if exists old ;
create temp table old (article_id int, department text, article_number text, description text, amount int);
create or replace function backup_deleted_articles()
returns trigger 
as $$
plan = plpy.prepare("insert into old(article_id, department, article_number, description, amount) values($1, $2, $3, $4, $5);", ["int", "text", "text", "text", "int"])
pi = TD['old']
rv = plpy.execute(plan, [pi["article_id"], pi["department"], pi["article_number"], pi["description"], pi["amount"]])
return TD['new']
$$ language  plpython3u;

drop trigger backup_deleted_articles on lab.article ; 

create trigger backup_deleted_articles
before delete on lab.article for each row
execute procedure backup_deleted_articles();

delete from lab.article 
where article_id = 20;

select * from old;

--6
--Определяемый пользователем тип данных CLR.
create type article_desc as (
  article_number text,
  description text
);

drop function get_article_desc_by_id;
--drop type player_cut;
-- Вывод параметров статьи по id
create or replace function get_article_desc_by_id(id_ integer) returns article_desc 
as $$
plan = plpy.prepare("select article_number, description from lab.article where article_id = $1", ["int"])
cr = plpy.execute(plan, [id_])
return (cr[0]['article_number'], cr[0]['description'])
$$ language plpython3u;

select * from get_article_desc_by_id(3);

select *
from lab.article a 
where article_id = 3;

