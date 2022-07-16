import psycopg2
from config import user, password, db_name, host

def drop_db(conn):
    with conn.cursor() as cursor:
        cursor.execute("""
                DROP TABLE IF EXISTS phones;
                DROP TABLE IF EXISTS clients_db;
        """)
        conn.commit()

def create_db(conn):
    with conn.cursor() as cursor:
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS clients_db (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(25) NOT NULL,
                last_name VARCHAR(25) NOT NULL,
                email VARCHAR(25) NOT NULL
            );
                CREATE TABLE IF NOT EXISTS phones (
                clients_id INT REFERENCES clients_db(id),
                phone VARCHAR(11) NOT NULL
            );       
        """)
        conn.commit()

def add_client(conn, first_name, last_name, email, phones=None):
    if phones:
        with conn.cursor() as cursor:
            cursor.execute(f"""
                            INSERT INTO clients_db(first_name, last_name, email)
                            VALUES(%s,%s,%s) RETURNING id;""",
                           (first_name, last_name, email))
            id_client = cursor.fetchone()

            cursor.execute(f"""
                INSERT INTO phones (clients_id, phone) VALUES (%s,%s);""",
                (id_client, phones)
                )
            conn.commit()

    else:
        with conn.cursor() as cursor:
            cursor.execute(f"""
                INSERT INTO clients_db(first_name, last_name, email)
                VALUES(%s,%s,%s);""",
               (first_name, last_name, email)
               )
            conn.commit()

def add_phone(conn, client_id, phone):
    with conn.cursor() as cursor:
        cursor.execute(f"""
            INSERT INTO phones (clients_id, phone) VALUES (%s,%s);""",
           (client_id, phone)
           )
        conn.commit()

def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):

    with conn.cursor() as cursor:
        if first_name:
            cursor.execute("""
                UPDATE clients_db
                SET first_name=%s
                WHERE id=%s
                """,
                (first_name, client_id))
        if last_name:
            cursor.execute("""
                UPDATE clients_db
                SET last_name=%s
                WHERE id=%s
                """,
            (last_name, client_id))
        if email:
            cursor.execute("""
                UPDATE clients_db
                SET email=%s
                WHERE id=%s
                """,
            (email, client_id))
        if phones:
            add_phone(conn, client_id, phones)
        conn.commit()

def delete_phone(conn, client_id, phone):
    with conn.cursor() as cursor:
        cursor.execute(f"""
            DELETE FROM phones 
            WHERE clients_id = %s and phone = %s;""",
           (client_id, phone)
           )
        conn.commit()

def delete_client(conn, client_id):
    with conn.cursor() as cursor:
        cursor.execute(f"""
            DELETE FROM clients_db 
            WHERE id = %s;""",
           (client_id,)
           )
        conn.commit()

def find_client(conn, first_name=None, last_name=None, email=None, phone=None):

    def prefix(ob):
        return "%"+ob+"%" if ob else None

    with conn.cursor() as cursor:
        cursor.execute(f"""
            SELECT c.first_name, c.last_name, c.email, p.phone  FROM clients_db c
            LEFT JOIN phones p
            ON c.id = p.clients_id
            WHERE c.first_name LIKE %s OR c.last_name LIKE %s OR c.email LIKE %s OR c.id = (
                SELECT p.clients_id FROM phones p WHERE p.phone LIKE %s);""",
                       (prefix(first_name), prefix(last_name), prefix(email), phone))
        print(*cursor.fetchall(), sep="\n")

def main():
    conn = psycopg2.connect(host=host, database=db_name, user=user, password=password)
    try:
        # drop_db(conn)
        # create_db(conn)
        # add_client(conn, 'Ivanov', "Ivan", "ivan@mail.ru", "89991234567") #, "89991234567"
        # add_client(conn, 'Ivanov2', "Ivan2", "ivan2@mail.ru") #, "89991234567"
        # add_phone(conn, 2, "01234567890")
        # change_client(conn, 2, "sdfgh", "kjhgf", "dfghd@dfg.tu", "12345678905")
        # delete_phone(conn, 2, "12345678905")
        # delete_client(conn, 2)
        find_client(conn, 'Iva', email="@mail.ru")


    except Exception as ex:
        print("[INFO] ERROR -->", ex)
    finally:
        conn.close()

if __name__ == "__main__":
    main()