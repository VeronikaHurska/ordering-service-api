import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

class DatabaseManager:
    def __init__(self, dbname, user, password, host, port):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    def execute_query(self, query, args=None):
        print("===============",args)
        try:
            con = self.connect()
            cur = con.cursor()
            cur.execute(query, args)
            result = cur.fetchall()
            cur.close()
            con.close()
            return result
        except Exception as e:
            print("Error executing query:", e)
            raise

    
    def connect(self):
        con = psycopg2.connect(
            dbname="postgres",  # Connect to the default "postgres" database
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return con

    def create_database(self):
        con = self.connect()
        cur = con.cursor()

        try:
            cur.execute(sql.SQL("CREATE DATABASE {};").format(sql.Identifier(self.dbname)))
            print(f"Database {self.dbname} created successfully.")
        except psycopg2.errors.DuplicateDatabase:
            cur.execute(sql.SQL("DROP DATABASE {};").format(sql.Identifier(self.dbname)))
            cur.execute(sql.SQL("CREATE DATABASE {};").format(sql.Identifier(self.dbname)))
            print(f"Database {self.dbname} already exists and created again")

        con.close()

    def create_tables(self):
        con = self.connect()
        cur = con.cursor()

        create_orders_table = """
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            created_date TIMESTAMP DEFAULT NOW(),
            updated_date TIMESTAMP DEFAULT NOW(),
            title VARCHAR(255) NOT NULL
        );
        """

        create_items_table = """
        CREATE TABLE IF NOT EXISTS items (
            id SERIAL PRIMARY KEY,
            order_id INTEGER REFERENCES orders(id),
            name VARCHAR(255) NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            number INT NOT NULL
        );
        """

        try:
            cur.execute(sql.SQL(create_orders_table))
            cur.execute(sql.SQL(create_items_table))
            print("Tables created successfully.")
        except psycopg2.errors.DuplicateTable:
            print("Tables already exist.")

        con.close()

# Create a DatabaseManager instance and create the database and tables
db = DatabaseManager(dbname="orders", user="postgres", host="db", password="postgres", port="5432")
db.create_database()
db.create_tables()


# import psycopg2


# class DatabaseManager:
#     def __init__(self, db_params):
#         self.db_params = db_params
#         self.connection = None
#         self.cursor = None

#     def connect(self):
#         try:
#             self.connection = psycopg2.connect(**self.db_params)
#             self.cursor = self.connection.cursor()
#         except psycopg2.Error as e:
#             print("Error:", e)

#     def close(self):
#         if self.cursor:
#             self.cursor.close()
#         if self.connection:
#             self.connection.close()

#     def execute_query(self, query, params=None):
#         if not self.connection or not self.cursor:
#             raise ValueError("----------Database connection not established.---------")
        
#         self.cursor.execute(query, params)
        

#         if query.lower().startswith("select"):
#             return self.cursor.fetchall()
#         else:
#             return None  

# db_params = {
#     "dbname": "orders",
#     "user": "veronika",
#     "password": "0000",
#     "host": "localhost",
#     "port": 5
# }

# create_orders_table = """
# CREATE TABLE IF NOT EXISTS orders (
#     id SERIAL PRIMARY KEY,
#     created_date TIMESTAMP DEFAULT NOW(),
#     updated_date TIMESTAMP DEFAULT NOW(),
#     title VARCHAR(255) NOT NULL
# );
# """

# create_items_table = """
# CREATE TABLE IF NOT EXISTS items (
#     id SERIAL PRIMARY KEY,
#     order_id INTEGER REFERENCES orders(id),
#     name VARCHAR(255) NOT NULL,
#     price DECIMAL(10, 2) NOT NULL
# );
# """

# # Execute the SQL statements

# db = DatabaseManager(db_params)

# db.connect()

# db.execute_query(create_orders_table)
# db.execute_query(create_items_table)

# print('--------------------------')



# @router.on_event("startup")
# async def create_database():
#     await asyncio.sleep(10)
#     con = psycopg2.connect(dbname="postgres", user="postgres", host="db", password="postgres")

#     con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)  # <-- ADD THIS LINE

#     cur = con.cursor()

#     try:
#         cur.execute(sql.SQL("CREATE DATABASE test;"))
#     except:
#         cur.execute(sql.SQL("DROP DATABASE test;"))
#         cur.execute(sql.SQL("CREATE DATABASE test;"))

#     db_con = psycopg2.connect(dbname="test", user="postgres", host="db", password="postgres")

#     cur = db_con.cursor()
#     db_con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
#     cur.execute(sql.SQL("CREATE TABLE IF NOT EXISTS test_table (id int);"))