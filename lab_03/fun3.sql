-- автомобили владельца по owner_id 
drop function if exists scalar_arg_many_op_function(int);
create function scalar_arg_many_op_function(int) returns table (
	id  int,
	model text,
	plate text
) as 
'	select car_id, model, plate
	from lab.car
	where owner_id = $1
'
language sql;

select * from scalar_arg_many_op_function(7)
