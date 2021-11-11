-- вывод всех начальников 

drop function if exists fun_recursive(ct int);

create function fun_recursive (ct int)
returns table (
	id int, 
	manager int
) language plpgsql
as $$
begin
    return query select ct, (select managerid from lab.myemployees where employeeid = ct);
    if (select managerid from lab.myemployees where employeeid = ct) is not null then
        return query 
		select * 
		from fun_recursive((select managerid from lab.myemployees where employeeid = ct));
    end if;
end $$;

select * from fun_recursive(5);