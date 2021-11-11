create or replace function name_log_func()
returns trigger as
$example_table$
   begin
      raise notice 'Employee id=% got new name="%" at %', new.employeeid , new.firstname, current_timestamp;
     return new;
   end;
$example_table$ language plpgsql;

drop trigger if exists myemployees_new_name on lab.myemployees;
create trigger myemployees_new_name
	after update of firstname on lab.myemployees 
	for each row
	execute procedure name_log_func();

update lab.myemployees 
set firstname = 'Иванн'
where employeeid = 3
