import sqlite3 as sq
import os,sys
import hashlib
import json
import os

class Sqlite_create():
    def __init__(self,table_name) -> None:
        self.table_name = table_name
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.ruta = os.path.join(base_dir, "datos_activos", "datos.db")
        
    def encriptar(self,contra:str):
        return hashlib.sha256(contra.encode()).hexdigest()
    
    def new_route(self,ruta):
        self.ruta = ruta
        
    def Create_table(self):
    
        conn = sq.connect(self.ruta)

        cursor = conn.cursor()
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                key text,
                value any
            )"""
        )
        conn.commit()
        conn.close()
        
        print(f"Se creó la tabla in {self.ruta}")
    

    def exist_key(self,key_search) -> bool:
          
        conn = sq.connect(self.ruta)

        cursor = conn.cursor()
        
        instruccion = f"SELECT * FROM {self.table_name}"
        cursor.execute(instruccion)
        datos = cursor.fetchall()
        conn.commit()
        conn.close()

        for i in datos:
            if key_search in i:
                return True
        return False
        
    def set_key_of_value(self,key,value):
        
        if type(value) == str:
            value = f"'{value}'"
        
        conn = sq.connect(self.ruta)

        cursor = conn.cursor()
        
        if not self.exist_key(key):
            instruccion = f"INSERT INTO {self.table_name} VALUES ('{key}', {value})"
        else:
            instruccion = f"UPDATE {self.table_name} SET key='{key}', value={value} WHERE key like '{key}'"
            
        cursor.execute(instruccion)
        
        conn.commit()
        conn.close()
    
    def get_value_of_key(self,key):

        if not self.exist_key(key):
            return None
        
        conn = sq.connect(self.ruta)

        cursor = conn.cursor()
        
        instruccion = f"SELECT * FROM {self.table_name} WHERE key like '{key}'"
        cursor.execute(instruccion)
        datos = cursor.fetchall()
        conn.commit()
        conn.close()
        
        return datos[0][1]
    
    def exist_table(self) -> bool:
        try:
            conn = sq.connect(self.ruta)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT name 
                FROM sqlite_master 
                WHERE type='table' AND name=?;
            """, (self.table_name,))

            existe = cursor.fetchone() is not None

            conn.close()
            return existe

        except sq.Error:
            return False
        
    def set_list_value(self, key, lista:list):

        if not isinstance(lista, list):
            raise ValueError("El value debe ser una lista")

        value = json.dumps(lista)  # list → string

        conn = sq.connect(self.ruta)
        cursor = conn.cursor()

        if not self.exist_key(key):
            cursor.execute(
                f"INSERT INTO {self.table_name} (key, value) VALUES (?, ?)",
                (key, value)
            )
        else:
            cursor.execute(
                f"UPDATE {self.table_name} SET value=? WHERE key=?",
                (value, key)
            )

        conn.commit()
        conn.close()
        

    def get_list_value(self, key):

        if not self.exist_key(key):
            return None

        conn = sq.connect(self.ruta)
        cursor = conn.cursor()

        cursor.execute(
            f"SELECT value FROM {self.table_name} WHERE key=?",
            (key,)
        )

        data = cursor.fetchone()
        conn.close()

        return json.loads(data[0])  # string → list

    def get_all_tables(self) -> list: # type: ignore
        
        conn = sq.connect(self.ruta)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name 
            FROM sqlite_master 
            WHERE type='table'
            AND name NOT LIKE 'sqlite_%';
        """)

        tablas = cursor.fetchall()
        conn.close()

        return [t[0] for t in tablas]


    def delete_table(self) -> None:
        conn = sq.connect(self.ruta)
        cursor = conn.cursor()

        try:
            cursor.execute(f"DROP TABLE IF EXISTS {self.table_name};")
            conn.commit()
        finally:
            conn.close()