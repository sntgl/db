-- добавляет стоимость ко всем статьям из указанного промежутка id 
-- искуственный пример((

create or replace procedure proc_recursive(upd_article_id_start int, upd_article_id_end int, add_amount int) as
$$
begin
	if (upd_article_id_start <= upd_article_id_end) then 
		update lab.article 
		set amount = amount + add_amount
		where article_id = upd_article_id_start;
		call proc_recursive(upd_article_id_start + 1, upd_article_id_end, add_amount);
	end if;
end;
$$ language plpgsql;

call proc_recursive(1, 3, 500);

select * from lab.article;

call proc_recursive(1, 3, -500);