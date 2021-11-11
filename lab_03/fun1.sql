-- самое большое количество штрафов среди всех машин 
drop function if exists scalar_function();
create function scalar_function() returns int as 
'	select count(*) cnt
	from lab.fine
	group by car_id
	order by cnt desc
'
language sql;

select scalar_function()
