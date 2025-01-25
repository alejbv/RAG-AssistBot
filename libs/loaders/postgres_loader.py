
import psycopg
from libs.abstract_models.database_loader import DatabaseLoader


class PostgresLoader(DatabaseLoader):
    def __init__(self):
        super().__init__()
        self.document_info = []
    
    def __get_connection__(self):
        return psycopg.connect(conninfo=f"dbname={self.databse} user={self.user} password={self.password} host={self.host} port={self.port}")
    
    def load_data(self):
        conn = self.__get_connection__()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * from biblioteca_normativa;")
            
            return cursor.fetchall()




