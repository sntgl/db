-- изменяет цену штрафа
-- id = 3 default = 5000
create or replace procedure proc_update_article_amount(upd_article_id int, new_amount int) as
$$
	update lab.article 
	set amount = new_amount
	where article_id = upd_article_id 
$$ language sql;

call proc_update_article_amount(3, 999);

select * from lab.article a;

call proc_update_article_amount(3, 5000);