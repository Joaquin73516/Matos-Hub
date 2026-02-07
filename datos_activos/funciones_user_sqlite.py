import os, re
from datetime import datetime as dt
from .funciones_sqlite import Sqlite_create

class User(Sqlite_create):
    def __init__(self, name, ip=None, device_id=None, fingerprint=None) -> None:
        self.name = name.replace("#", "")
        self.table_name = f"{self.name}_adm"
        super().__init__(self.table_name)

        # 🔵 SI NO EXISTE TABLA → CREAR
        if not self.exist_table():
            self.Create_table()

            self.photos_num = 0
            self.photos = []

            self.set_list_value("photos", self.photos)
            self.set_key_of_value("photos_num", self.photos_num)

            # seguridad (solo si vienen datos)
            if ip is not None:
                self.ip = ip
                self.set_key_of_value("ip", ip)

            if device_id is not None:
                self.device_id = device_id
                self.set_key_of_value("device_id", device_id)

            if fingerprint is not None:
                self.fingerprint = fingerprint
                self.set_key_of_value("fingerprint", fingerprint)

            # historial ips
            if ip is not None:
                self.ips_historial = [ip]
            else:
                self.ips_historial = []

            self.set_list_value("ips_historial", self.ips_historial)

        # 🔵 SI YA EXISTE TABLA
        else:
            self.photos: list = self.get_list_value("photos") or []
            self.photos_num: int = self.get_value_of_key("photos_num") or 0

            # cargar solo si existen en db
            db_ip = self.get_value_of_key("ip")
            db_device = self.get_value_of_key("device_id")
            db_fingerprint = self.get_value_of_key("fingerprint")
            db_ips_hist = self.get_list_value("ips_historial") or []

            if db_ip is not None:
                self.ip = db_ip

            if db_device is not None:
                self.device_id = db_device

            if db_fingerprint is not None:
                self.fingerprint = db_fingerprint

            self.ips_historial = db_ips_hist

        # 🔵 ACTUALIZAR SOLO SI LLEGAN DATOS NUEVOS
        if ip is not None:
            self.ip = ip
            self.set_key_of_value("ip", ip)

            if ip not in self.ips_historial:
                self.ips_historial.append(ip)
                self.set_list_value("ips_historial", self.ips_historial)

        if device_id is not None:
            self.device_id = device_id
            self.set_key_of_value("device_id", device_id)

        if fingerprint is not None:
            self.fingerprint = fingerprint
            self.set_key_of_value("fingerprint", fingerprint)

        self.sesion()

    def sesion(self):
        hora = dt.now()
        str_hora = hora.strftime("%d/%m %H:%M")
        self.set_key_of_value("ult_session", str_hora)

    def upload_photo(self, photo, name_photo, ex):

        if self.photos_num >= 50:
            raise Exception("Limite de fotos alcanzado")

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        BASE_DIR = os.path.dirname(BASE_DIR)

        CARPETA_SUBIDAS = os.path.join(BASE_DIR, "uploads")
        os.makedirs(CARPETA_SUBIDAS, exist_ok=True)

        self.sesion()

        # limpiar nombre
        name_photo = re.sub(r'[^a-zA-Z0-9_-]', '', name_photo)

        hora = dt.now()
        str_hora = hora.strftime("%d-%m_%H-%M")
        ex = ex.lstrip('.')

        photo_name = f"{self.name}_{name_photo}_{str_hora}.{ex}"
        ruta = os.path.join(CARPETA_SUBIDAS, photo_name)

        with open(ruta, "wb") as f:
            f.write(photo.read())

        self.photos_num += 1
        self.set_key_of_value("photos_num", self.photos_num)

        self.photos.append(photo_name)
        self.set_list_value("photos", self.photos)

        return ruta

    def get_security_info(self):
        return {
            "ip_actual": self.ip,
            "device_id": self.device_id,
            "fingerprint": self.fingerprint,
            "ips_usadas": self.ips_historial
        }
