-- добавляет стоимость ко всем статьям из указанного промежутка id с курсором
-- искуственный пример((

create or replace procedure proc_cur(upd_article_id_start int, upd_article_id_end int, add_amount int) as
$$
declare cur cursor
	for select *
	from lab.article
	where article_id between upd_article_id_start and upd_article_id_end;
line record;

begin
	open cur;
	loop
		fetch cur into line;
		exit when not found;
		update lab.article 
		set amount = amount + add_amount
		where lab.article.article_id = line.article_id;
	end loop;
	close cur;
end;
$$ language plpgsql;

call proc_cur(1, 3, 99);

select * from lab.article;

call proc_cur(1, 3, -99);