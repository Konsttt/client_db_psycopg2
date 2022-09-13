import psycopg2


def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
                CREATE TABLE IF NOT EXISTS client(
                    id SERIAL PRIMARY KEY,
                    first_name VARCHAR(40),
                    last_name VARCHAR(40),
                    email VARCHAR(40) UNIQUE
                );
                """)
        cur.execute("""CREATE TABLE IF NOT EXISTS tel(
                    id SERIAL PRIMARY KEY,
                    client_id INTEGER NOT NULL REFERENCES client(id),
                    phone VARCHAR(20)
                );
                """)
    conn.commit()


def add_client(conn, first_name, last_name, email, phone=None):
    with conn.cursor() as cur:
        cur.execute("""
                INSERT INTO client(first_name, last_name, email) VALUES(%s, %s, %s) RETURNING id;
                """, (first_name, last_name, email))
        client_id = cur.fetchone()[0]
        if phone:
            cur.execute("""    
                INSERT INTO tel(client_id, phone) VALUES(%s, %s);
                """, (client_id, phone))
        conn.commit()


def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""    
                INSERT INTO tel(client_id, phone) VALUES(%s, %s);
                """, (client_id, phone))
        conn.commit()


def change_client(conn, client_id, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cur:
        if first_name:
            cur.execute("""
                UPDATE client SET first_name=%s WHERE id=%s;
                """, (first_name, client_id))
        if last_name:
            cur.execute("""
                UPDATE client SET last_name=%s WHERE id=%s;
                """, (last_name, client_id))
        if email:
            cur.execute("""
                UPDATE client SET email=%s WHERE id=%s;
                """, (email, client_id))
        if phone:
            cur.execute("""
                UPDATE tel SET phone=%s WHERE client_id=%s;
                """, (phone, client_id))
        conn.commit()


def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM tel WHERE client_id=%s AND phone=%s;
            """, (client_id, phone))
        conn.commit()


def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM tel WHERE client_id=%s;
            """, (client_id,))
        cur.execute("""
            DELETE FROM client WHERE id=%s;
        """, (client_id,))
        conn.commit()


# Перебраны все комбинации полноты ввода пользователем данных для поиска
def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cur:
        if first_name and not last_name and not email and not phone:
            cur.execute("""
                SELECT id, first_name, last_name, email FROM client WHERE first_name=%s;
                """, (first_name,))
            list_tuple_client = cur.fetchall()
            return fetch_to_list(cur, list_tuple_client)
        elif not first_name and last_name and not email and not phone:
            cur.execute("""
                SELECT id, first_name, last_name, email FROM client WHERE last_name=%s;
                """, (last_name,))
            list_tuple_client = cur.fetchall()
            return fetch_to_list(cur, list_tuple_client)
        elif not first_name and not last_name and email and not phone:
            cur.execute("""
                SELECT id, first_name, last_name, email FROM client WHERE email=%s;
                """, (email,))
            list_tuple_client = cur.fetchall()
            return fetch_to_list(cur, list_tuple_client)
        elif not first_name and not last_name and not email and phone:
            cur.execute("""
                SELECT id, first_name, last_name, email 
                FROM client 
                WHERE id IN (SELECT client_id FROM tel WHERE phone=%s);
                """, (phone,))
            list_tuple_client = cur.fetchall()
        elif first_name and last_name and not email and not phone:
            cur.execute("""
                SELECT id, first_name, last_name, email FROM client WHERE first_name=%s and last_name=%s;
                """, (first_name, last_name))
            list_tuple_client = cur.fetchall()
        elif first_name and not last_name and email and not phone:
            cur.execute("""
                SELECT id, first_name, last_name, email FROM client WHERE first_name=%s and email=%s;
                """, (first_name, email))
            list_tuple_client = cur.fetchall()
        elif first_name and not last_name and not email and phone:
            cur.execute("""
                SELECT id, first_name, last_name, email 
                FROM client 
                WHERE first_name=%s and id IN (SELECT client_id FROM tel WHERE phone=%s);
                """, (first_name, phone))
            list_tuple_client = cur.fetchall()
        elif first_name and last_name and email and not phone:
            cur.execute("""
                SELECT id, first_name, last_name, email FROM client WHERE first_name=%s and last_name=%s and email=%s;
                """, (first_name, last_name, email))
            list_tuple_client = cur.fetchall()
        elif first_name and last_name and not email and phone:
            cur.execute("""
                SELECT id, first_name, last_name, email 
                FROM client 
                WHERE first_name=%s and last_name=%s and id IN (SELECT client_id FROM tel WHERE phone=%s);
                """, (first_name, last_name, phone))
            list_tuple_client = cur.fetchall()
        elif first_name and last_name and email and phone:
            cur.execute("""
                       SELECT id, first_name, last_name, email 
                       FROM client 
                       WHERE first_name=%s and last_name=%s and email=%s and id IN (SELECT client_id FROM tel WHERE phone=%s);
                       """, (first_name, last_name, email, phone))
            list_tuple_client = cur.fetchall()
        elif not first_name and last_name and email and phone:
            cur.execute("""
                       SELECT id, first_name, last_name, email 
                       FROM client 
                       WHERE last_name=%s and email=%s and id IN (SELECT client_id FROM tel WHERE phone=%s);
                       """, (last_name, email, phone))
            list_tuple_client = cur.fetchall()
        elif not first_name and last_name and not email and phone:
            cur.execute("""
                       SELECT id, first_name, last_name, email 
                       FROM client 
                       WHERE last_name=%s and id IN (SELECT client_id FROM tel WHERE phone=%s);
                       """, (last_name, phone))
            list_tuple_client = cur.fetchall()
        elif not first_name and not last_name and email and phone:
            cur.execute("""
                       SELECT id, first_name, last_name, email 
                       FROM client 
                       WHERE email=%s and id IN (SELECT client_id FROM tel WHERE phone=%s);
                       """, (email, phone))
            list_tuple_client = cur.fetchall()
        return fetch_to_list(cur, list_tuple_client)


# Вспомогательная функция обработки списка кортежей после выборки из БД
# Эта функция используется в функции find_client, для уменьшения повторения больших кусков кода
def fetch_to_list(cur, list_tuple_client):
    result_list = []
    if list_tuple_client:
        for one_client in list_tuple_client:
            client_id = one_client[0]
            one_client_info = list(one_client)
            cur.execute("""
                            SELECT phone FROM tel WHERE client_id=%s;
                            """, (client_id,))
            phones_one_client = cur.fetchall()
            if phones_one_client:
                phones_list = []
                for phone in phones_one_client:
                    phones_list.append(phone[0])
                one_client_info.extend(phones_list)
            result_list.append(one_client_info)
        return result_list
    else:
        print(f'В БД нет клиента с такими данными')


# Функция печати результатов выборки. Печать списка со списками.
def print_find_result(list_result):
    if list_result:
        for client in list_result:
            print(f'id: {client[0]}, first_name: {client[1]}, last_name: {client[2]}, email: {client[3]}')
            n = len(client)
            if n > 4:
                if n == 5:
                    print('phone: ', end='')
                else:
                    print('phones: ', end='')
                for i in range(4, n):
                    if i < n-1:
                        print(f'{client[i]}, ', end='')
                    else:
                        print(f'{client[i]}')
            print()


def dialog_db(conn):
    print("Программа работы с базой данных clients_db.")
    print("Введите '?' для справки по командам.")
    flag = True
    while flag:
        command_ = input('Введите команду: ')
        if command_ == '?':
            print("               'c' - создать БД\n\
               'a' - добавить клиента\n\
               'p' - добавить телефон\n\
               'ch' - изменить данные клиента\n\
               'd' - удаление клиента из БД\n\
               'dp' - удаление телефона клиента\n\
               'f' - найти клиента в БД\n\
               'q' - выход из программы")
        elif command_ == 'с':
            create_db(conn)
        elif command_ == 'a':
            f_name = input('Введите имя клиента: ')
            l_name = input('Введите фамилию клиента: ')
            email_c = input('Введите email клиента: ')
            phone_c = input('Введите телефон клиента или пропустите, нажав Enter: ')
            add_client(conn, f_name, l_name, email_c, phone_c)
        elif command_ == 'p':
            c_id = input('Введите id клиента: ')
            phone_c = input('Введите телефон клиента: ')
            add_phone(conn, c_id, phone_c)
        elif command_ == 'ch':
            id_c = input('Введите id клиента данные которого будут изменены: ')
            f_name = input('Введите имя клиента или пропустите, нажав Enter: ')
            l_name = input('Введите фамилию клиента или пропустите, нажав Enter: ')
            email_c = input('Введите email клиента или пропустите, нажав Enter: ')
            phone_c = input('Введите телефон клиента или пропустите, нажав Enter: ')
            change_client(conn, id_c, f_name, l_name, email_c, phone_c)
        elif command_ == 'd':
            id_c = input('Введите id клиента, все данные которого будут удалены из БД: ')
            delete_client(conn, id_c)
        elif command_ == 'dp':
            id_c = input('Введите id клиента, телефон которого хотите удалить: ')
            phone_c = input('Введите телефон клиента: ')
            delete_phone(conn, id_c, phone_c)
        elif command_ == 'f':
            f_name = input('Для поиска по имени введите имя клиента или пропустите, нажав Enter: ')
            l_name = input('Для поиска по фамилии введите фамилию клиента или пропустите, нажав Enter: ')
            email_c = input('Для поиска по email введите email клиента или пропустите, нажав Enter: ')
            phone_c = input('Для поиска по телефону введите телефон клиента или пропустите, нажав Enter: ')
            print_find_result(find_client(conn, f_name, l_name, email_c, phone_c))
        elif command_ == 'q':
            flag = False
            print('Завершение работы. Выполнен выход из программы.')


with psycopg2.connect(database="clients_db", user="postgres", password="Your_password") as conn:
    dialog_db(conn)
conn.close()