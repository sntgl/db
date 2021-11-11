
create or replace procedure all_tables() as
$$
declare 
	cur cursor
	for select table_name, table_schema
	from (
		select table_name, table_schema
		from information_schema.tables
		where table_schema not in ('information_schema','pg_catalog')
	) AS tmp;
		 row record;
begin
	open cur;
	loop
		fetch cur into row;
		exit when not found;
		raise notice '{table : %, schema : %}', row.table_name, row.table_schema;
	end loop;
	close cur;
end
$$ language plpgsql;

call all_tables();