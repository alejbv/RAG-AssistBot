
import psycopg
from psycopg.rows import dict_row
from libs.abstract_models.database_loader import DatabaseLoader

class PostgresLoader(DatabaseLoader):
    def __init__(self):
        super().__init__()
    
    def __get_connection__(self):
        return psycopg.connect(conninfo=f"dbname={self.databse} user={self.user} password={self.password} host={self.host} port={self.port}")
    
    def load_data(self):
        conn = self.__get_connection__()
        # It return every row as a dictionary with the columns name as key an the values are the respective row value
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute("SELECT * from biblioteca_normativa;")
            
            return cursor.fetchall()


