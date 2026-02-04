from .funciones_sqlite import Sqlite_create
from datetime import datetime as dt
import os

class User(Sqlite_create):
    def __init__(self, name) -> None:
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
        self.sesion()

    def sesion(self):
        hora = dt.now()
        str_hora = hora.strftime(f"%d/%m %H:%M")
        self.set_key_of_value("ult_session", str_hora)
        
    def upload_photo(self, photo, name_photo, ex):
        CARPETA_SUBIDAS = r"C:\Users\Joaquin\Desktop\Matos Hub\static\uploads"
        os.makedirs(CARPETA_SUBIDAS, exist_ok=True)

        self.sesion()

        hora = dt.now()
        str_hora = hora.strftime("%d-%m_%H-%M")

        ex = ex.lstrip('.')

        photo_name = f"{self.name}_{name_photo}_{str_hora}.{ex}"
        ruta = os.path.join(CARPETA_SUBIDAS, photo_name)

        photo.save(ruta)

        self.set_key_of_value("photos_num", self.photos_num + 1)
        self.photos.append(photo_name)
        self.set_list_value("photos", self.photos)

        return ruta