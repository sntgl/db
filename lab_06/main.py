import psycopg2
from psycopg2 import Error


class Department:
    def __init__(self, _department_id, _department_name, _manager):
        self.department_id = _department_id
        self.department_name = _department_name
        self.manager = _manager

    def insert_query(self):
        return f"INSERT INTO lab.Department (department_id, department_name, manager) " \
               f"VALUES ({self.department_id}, '{self.department_name}', '{self.manager}');"


class DB:
    def __init__(self):
        self.__error = None
        try:
            self.__connection = psycopg2.connect(user="postgres",
                                                 password="123",
                                                 host="127.0.0.1",
                                                 port="5432",
                                                 database="postgres")
            self.__cursor = self.__connection.cursor()
            print("DB: Connected to PostgreSQL")
        except (Exception, Error) as error:
            # print("Error while connecting to PostgreSQL", error)
            self.__error = error

    def get_error(self):
        return self.__error

    def __del__(self):
        print("DB: Connection closed")
        self.__connection.close()

    def __exec(self, query, commit=False):
        self.__cursor.execute(query)
        if commit: self.__commit()
        try:
            return self.__cursor.fetchall()
        except:
            return

    def __commit(self):
        self.__connection.commit()
        print("DB: Commit success!")

    # 1 Имя по id овнера
    def name_by_owner_id(self, owner_id):
        self.__cursor.execute(f"SELECT first_name FROM lab.owner WHERE owner_id = {owner_id}")
        return self.__cursor.fetchone()[0]

    # 2 все штрафы по паспорту
    def all_cars_plates_by_owner_passport(self, passport_id):
        self.__cursor.execute(f"""
            SELECT f.fine_id, cc.model, cc.plate, f.is_paid
            FROM 
                    ((SELECT owner_id FROM lab.owner WHERE passport_id = {passport_id}) o
                    JOIN
                    lab.car c
                    ON c.owner_id = o.owner_id) cc
                JOIN
                    lab.fine f
                ON cc.car_id = f.car_id
        """)
        return self.__cursor.fetchall()

    def avg_fines_count(self):
        self.__cursor.execute(f"""
        WITH CTE (owner_id, fines_count) AS (
            SELECT owner_id, count(coalesce(tb2.finesCount, 0))
            FROM (
                lab.car tb1 LEFT JOIN (
                SELECT count(*)  as finesCount, car_id as cid
                FROM lab.fine
                GROUP BY car_id
                ) tb2
                ON tb2.cid = tb1.car_id
            )
            GROUP BY owner_id
        )
        SELECT AVG(fines_count) FROM CTE
        """)
        return self.__cursor.fetchone()[0]

    # Все таблички
    def get_tables(self):
        self.__cursor.execute(f"""
            SELECT table_name, table_schema
            FROM information_schema.tables
            WHERE table_schema NOT IN ('information_schema','pg_catalog')
        """)
        return self.__cursor.fetchall()

    # Cамое большое количество штрафов среди всех машин
    def max_fines_cnt(self):
        self.__cursor.execute(f"""
            SELECT lab.scalar_function()
        """)
        return self.__cursor.fetchone()[0]

    # Количество штрафов по car_id
    def fines_count_by_id(self, car_id):
        # self.cursor.execute(f"""
        #     SELECT lab.scalar_arg_function({car_id})
        # """)
        # return self.cursor.fetchone()[0]
        return self.__exec(f"SELECT lab.scalar_arg_function({car_id})")[0][0]

    # изменяет цену штрафа
    # id = 3 default = 5000
    def update_article_amount(self, article_id, new_amount):
        self.__exec(f"call proc_update_article_amount({article_id}, {new_amount});", True)

    # системная функция
    def get_database_and_user(self):
        return self.__exec("select current_database(), current_user")[0]

    # создает таблицу полиц. участков
    def create_police_department_table(self):
        self.__exec(f"DROP TABLE IF EXISTS lab.Department;"
                    f"CREATE TABLE lab.Department ("
                    f"department_id INT PRIMARY KEY,"
                    f"department_name TEXT, "
                    f"manager TEXT"
                    f");", True)

    def insert_into_police_departments(self, d: [Department]):
        for dep in d:
            self.__exec(dep.insert_query(), True)

    def get_all_departments(self):
        return self.__exec("SELECT * FROM lab.Department")

    def delete_article(self, fid):
        r = self.__exec(f"SELECT * FROM lab.article WHERE article_id={fid};")
        if len(r) == 0:
            raise Exception("Нет такой статьи!")
        r = self.__exec(f"SELECT c.car_id, c.plate, c.model "
                        f"FROM "
                        f"(SELECT * FROM lab.fine WHERE article_id = {fid}) f "
                        f"JOIN "
                        f"lab.car c "
                        f"ON f.car_id = c.car_id;")
        self.__exec(f"DELETE FROM lab.fine WHERE article_id={fid};")
        self.__exec(f"DELETE FROM lab.article WHERE article_id={fid};")
        self.__commit()
        return r

    def add_arts(self):
        self.__exec(
            f"insert into lab.article(article_id, department, article_number, description, amount) values (20, 'Управление', '2.2.8', 'ВЫАпщ', 10000);"
            f"insert into lab.fine(fine_id, car_id, article_id) values(80000, 255, 20);"
            f"insert into lab.fine(fine_id, car_id, article_id) values(80001, 152, 20);"
            f"insert into lab.fine(fine_id, car_id, article_id) values(80002, 567, 20);"
            f"insert into lab.fine(fine_id, car_id, article_id) values(80003, 12, 20);"
            f"insert into lab.fine(fine_id, car_id, article_id) values(80004, 657, 20);", True)


class UI:

    def __init__(self):
        self.exit = False
        self.db = DB()
        self.error = self.db.get_error()
        self.cmds = [
            self.do_quit,
            self.get_owner_name_by_id,
            self.get_cars_by_passport,
            self.get_avg_fines_count,
            self.get_all_tables,
            self.get_max_fine_count,
            self.get_fine_count_by_car_id,
            self.update_fine_amount,
            self.get_current_user_and_db,
            self.create_departments,
            self.add_department,
            self.get_all_departments,
            self.delete_fine,
            self.add_fines
        ]
        if self.error is None:
            while not self.exit:
                self.do_menu()
        else:
            self.do_db_error()

    def do_menu(self):
        print("""
Программа для работы с БД Штрафы ПДД.
Напишите цифру желаемой команды:
0. Выйти;
1. Имя владельца по идентификатору владельца; (scalar)
2. Все автомобили по номеру паспорта; (scalar w/ joins)
3. Среднее количество штрафов среди всех владельцев; (CTE)
4. Получить все таблицы; (meta)
5. Максимальное количество штрафов; (scalar fun)
6. Количество штрафов по идентификатору авто; (many oper-r fun)
7. Обновить стоимость штрафа; (proc)
8. Получить текущую БД и Пользователя; (system fun)
9. Создать таблицу полицейских участков; (create table)
10. Добавить полицеский участок; (insert)
11. Показать полицеские участки; (select)
12. Удалить штраф и показать все авто, получавшие его. (defend)
13. Добавить 20ю статью и штрафов к ней
""")
        c = input()
        try:
            c = int(c)
            if c < 0 or c > 13: raise Exception()
        except:
            self.do_input_error()
            return
        self.cmds[c]()

    def do_quit(self):
        self.exit = True

    def wait_enter(self):
        print("Нажмите Enter, чтобы продолжить:")
        input()

    def do_db_error(self):
        print(f"Неудача при подключении к БД: {self.error}")

    def do_input_error(self):
        print("Неправильный ввод")

    def out_result(self, result):
        if result is not None:
            print(f"Результат: {result}")
            self.wait_enter()

    def out_result_list(self, result):
        if result is not None:
            print(f"Результат:")
            for row in result:
                print(row)
            self.wait_enter()

    def e(self, f, arg1=None, arg2=None):
        try:
            if arg1 is None:
                return f()
            else:
                if arg2 is None:
                    return f(arg1)
                else:
                    return f(arg1, arg2)
        except (Exception) as error:
            print(f"База данных вернула ошибку: {error}")
        return None

    def get_owner_name_by_id(self):
        print("Введите идентификатор владельца:")
        print("Введите паспорт:")
        o = input()
        try:
            o = int(o)
        except:
            self.do_input_error()
            return
        r = self.e(self.db.name_by_owner_id, o)
        self.out_result(r)

    def get_cars_by_passport(self):
        print("Введите паспорт:")
        o = input()
        try:
            o = int(o)
            r = self.e(self.db.all_cars_plates_by_owner_passport, o)
            self.out_result_list(r)
        except:
            self.do_input_error()

    def get_avg_fines_count(self):
        r = self.e(self.db.avg_fines_count)
        self.out_result(r)

    def get_all_tables(self):
        r = self.e(self.db.get_tables)
        self.out_result_list(r)

    def get_max_fine_count(self):
        r = self.e(self.db.max_fines_cnt)
        self.out_result(r)

    def get_fine_count_by_car_id(self):
        print("Введите идентификатор авто:")
        o = input()
        try:
            o = int(o)
            r = self.e(self.db.fines_count_by_id, o)
            self.out_result(r)
        except:
            self.do_input_error()

    def update_fine_amount(self):
        print("Введите идентификатор статьи:")
        aid = input()
        try:
            aid = int(aid)
        except:
            self.do_input_error()
            return
        print("Введите новую стоимость штрафа:")
        am = input()
        try:
            am = int(am)
        except:
            self.do_input_error()
            return
        self.e(self.db.update_article_amount, aid, am)

    def get_current_user_and_db(self):
        r = self.e(self.db.get_database_and_user)
        self.out_result(r)

    def create_departments(self):
        self.e(self.db.create_police_department_table)

    def add_department(self):
        deps = []
        cont = 'df'
        while cont != '':
            print("Введите идентификатор нового участка:")
            aid = input()
            try:
                aid = int(aid)
            except:
                self.do_input_error()
                return
            print("Введите название нового участка:")
            name = input()
            print("Введите директора нового участка:")
            man = input()
            print("Напишите что-нибудь чтоб добавить еще один, иначе Enter")
            deps.append(Department(aid, name, man))
            cont = input()
        self.e(self.db.insert_into_police_departments, deps)

    def get_all_departments(self):
        r = self.e(self.db.get_all_departments)
        self.out_result_list(r)

    def delete_fine(self):
        print("Введите идентификатор штрафа:")
        aid = input()
        try:
            aid = int(aid)
        except:
            self.do_input_error()
            return
        r = self.e(self.db.delete_article, aid)
        self.out_result_list(r)

    def add_fines(self):
        self.db.add_arts()


if __name__ == '__main__':
    UI()
