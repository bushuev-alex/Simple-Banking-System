import sqlite3

TABLE_CARDS = 'card'
TABLE_COLUMNS = """id INTEGER PRIMARY KEY, 
                    number TEXT, 
                    pin TEXT, 
                    balance INTEGER DEFAULT 0"""
SQL_NAME = 'card.s3db'


class DatabaseManager:

    def __init__(self, sql_filename):
        self.connection = sqlite3.connect(sql_filename)

    def _execute(self, statement, values=None):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(statement)
            self.connection.commit()
            return cursor

    def create_table(self, table_name, table_columns):
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({table_columns});"
        self._execute(query)

    def delete_row(self, table_name, column, value_to_compare):
        query = f"DELETE FROM {table_name} WHERE {column}={value_to_compare};"
        self._execute(query)

    def fetch_one_by_card_number(self, table_name, card_number):
        with self.connection:
            cursor = self.connection.cursor()
            sql_query = f"""SELECT * from {table_name} WHERE number={card_number}"""
            cursor.execute(sql_query)
            return cursor.fetchone()

    def add(self, table_name, column_names, values):
        query = f"""INSERT OR REPLACE INTO {table_name} {column_names} VALUES {values};"""
        self._execute(query)

    def update_table(self, table_name, value_to_add, column, value_to_compare):
        query = f"""UPDATE {table_name} SET balance={value_to_add} WHERE {column}={value_to_compare};"""
        self._execute(query)

    def __del__(self):
        self.connection.close()
