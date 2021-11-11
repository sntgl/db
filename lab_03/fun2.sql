-- количество штрафов по car_id 
drop function if exists scalar_arg_function(int);
create function scalar_arg_function(int) returns int as 
'	select count(*) cnt
	from lab.fine
	where car_id = $1
'
language sql;

select scalar_arg_function(65)
