from datos_activos.funciones_sqlite import Sqlite_create
from datos_activos.funciones_user_sqlite import User

print("1 = ban por nombre")
print("2 = ban por ip")
op = input("Opcion: ")

sq = Sqlite_create(None)
all_tables = sq.get_all_tables()

baner = Sqlite_create("_baner_")

if op == "1":
    name = input("Nombre usuario: ").replace("#","")

    us = User(name)

    baner.set_key_of_value(f"user_{us.name}", True)
    baner.set_key_of_value(f"ip_{us.ip}", True)
    baner.set_key_of_value(f"device_{us.device_id}", True)
    baner.set_key_of_value(f"fingerprint_{us.fingerprint}", True)

    print(f"BANEADO COMPLETO: {us.name}")


elif op == "2":
    ip_ban = input("Ingrese ip a banear: ")

    for i in all_tables:
        name = i.replace("_adm","")
        us = User(name)

        if us.ip == ip_ban:
            baner.set_key_of_value(f"user_{us.name}", True)
            baner.set_key_of_value(f"ip_{us.ip}", True)
            baner.set_key_of_value(f"device_{us.device_id}", True)
            baner.set_key_of_value(f"fingerprint_{us.fingerprint}", True)

            print(f"Se baneo a {us.name}")