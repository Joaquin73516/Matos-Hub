from .funciones_sqlite import Sqlite_create
from datetime import datetime as dt
import os
import re

class User(Sqlite_create):
    def __init__(self, name, ip = False) -> None:
        self.name = name.replace("#", "")
        self.table_name = f"{self.name}_adm"
        super().__init__(self.table_name)
        if not self.exist_table():
            self.Create_table()
            self.photos_num = 0
            self.photos = []
            self.set_list_value("photos", self.photos)
            self.set_key_of_value("photos_num",self.photos_num)
        else:
            self.photos:list = self.get_list_value("photos") # type: ignore
            self.photos_num:int = self.get_value_of_key("photos_num") # type: ignore
        if ip:
            self.ip = ip
            self.set_key_of_value("ip",self.ip)
        self.sesion()

    def sesion(self):
        hora = dt.now()
        str_hora = hora.strftime(f"%d/%m %H:%M")
        self.set_key_of_value("ult_session", str_hora)


    def upload_photo(self, photo, name_photo, ex):

        if self.photos_num >= 50:
            raise Exception("Limite de fotos alcanzado")

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        BASE_DIR = os.path.dirname(BASE_DIR)

        CARPETA_SUBIDAS = os.path.join(BASE_DIR, "static", "uploads")
        os.makedirs(CARPETA_SUBIDAS, exist_ok=True)

        self.sesion()

        # limpiar nombre foto (anti cosas raras)
        name_photo = re.sub(r'[^a-zA-Z0-9_-]', '', name_photo)

        hora = dt.now()
        str_hora = hora.strftime("%d-%m_%H-%M")

        ex = ex.lstrip('.')

        photo_name = f"{self.name}_{name_photo}_{str_hora}.{ex}"
        ruta = os.path.join(CARPETA_SUBIDAS, photo_name)

        # 🔥 guardar archivo como bytes (modo seguro)
        with open(ruta, "wb") as f:
            f.write(photo.read())

        # actualizar datos usuario
        self.set_key_of_value("photos_num", self.photos_num + 1)
        self.photos.append(photo_name)
        self.set_list_value("photos", self.photos)

        return ruta
