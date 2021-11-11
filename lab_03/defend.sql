-- изменяет цену штрафа по имени
-- id = 3 default = 5000
create or replace procedure proc_update_article_amountt(upd_article_number text, new_amount int) as
$$
	update lab.article 
	set amount = new_amount
	where article_number = upd_article_number 
$$ language sql;

call proc_update_article_amountt('12.9.5', 999);

select * from lab.article a;

call proc_update_article_amountt('12.9.5', 5000);