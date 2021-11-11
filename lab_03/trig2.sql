--SQL Error [42809]: ERROR: "myemployees" is a table
-- Detail: Tables cannot have INSTEAD OF triggers.

create or replace view emplV as
select *
from lab.myemployees;


create or replace function do_not_delete_employees()
returns trigger as
$$
begin
--	if ((select count(*) cnt from emplV where managerid = old.employeeid) > 0)
--	then
--	    raise notice 'Cannot delete from emplV - this employee is manager!';
--    	return old;
--    end if;	
--    raise notice 'Deleting from emplV!';
--    return new;
	raise notice 'Cannot delete from emplV';
	return old;
end;
$$ language plpgsql;

drop trigger if exists myemployees_do_not_delete on emplV;

create trigger myemployees_do_not_delete
	instead of delete on emplV
	for each row 
	execute procedure do_not_delete_employees();

delete 
from emplV
where employeeid = 9