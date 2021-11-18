

--Лаба 5
--1
select to_json(c) from lab.car c;
select row_to_json(c) from lab.car c

--2.1 экспорт
-- в консоли
psql --username=postgres -c "\copy (select row_to_json(c) from lab.car c) to '~/dev/db/lab_04/save.json'"

--2.2 импорт
--в консоли
create temp table lab_02.car(doc json);
\copy lab_02.car from '~/dev/db/lab_04/save.json';
select p.* from lab_02.car, json_populate_record(null::lab.car, doc) as p;
drop table cardupp;


--3
drop table test;
--нормальный способ
create temp table test as (select c.*, to_json(o) owner_json from lab.car c join lab."owner" o on c.owner_id = o.owner_id);

--с использованием апдейта)
create temp table test as (select * from lab.car);
alter table test add column owner_json json;
update test t set owner_json = (
	select to_json(o)
	from lab."owner" o
	where o.owner_id = t.owner_id
);


select * from test;


select * from test;
--4.1
--Извлечь XML/JSON фрагмент из XML/JSON документа
select '[{"owner_id":0,"passport_id":4126367970,"last_name":"Шарова","first_name":"Юлия","middle_name":"Тимуровна","date_birth":"1952-12-04","city_birth":"клх Североморск"},{"owner_id":22,"passport_id":4390941053,"last_name":"Самсон","first_name":"г-н","middle_name":"Соколов","date_birth":"1973-05-07","city_birth":"г. Нарткала"}]'::json->0


--4.2
--Извлечь значения конкретных узлов или атрибутов XML/JSON документа
select owner_json->'owner_id' owner_id from test;

--4.3
--Есть ли поле среди атрибутов
select owner_json->'owner_id' is not NULL field_exists from test;
select owner_json->'owner_dsdasdasfaqid' is not null field_exists from test;

--4.4
--Поменял поле last_name
select jsonb_set('{"owner_id":0,"passport_id":4126367970,"last_name":"Шарова"}', '{last_name}', jsonb '"Ольговна"')

--4.5
--Несколько json из одного
drop table if exists test;
create temp table test as(select '{"owner_id":0,"passport_id":4126367970,"last_name":"Шарова"}'::json as a);
select json_build_object('owner_id', a->'owner_id'), json_build_object('last_name', a->'last_name')
from test a



