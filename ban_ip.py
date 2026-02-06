from datos_activos.funciones_sqlite import Sqlite_create
from datos_activos.funciones_user_sqlite import User


ip_ban = input("Ingrese ip a banear:")
sq = Sqlite_create(None)
all_tables = sq.get_all_tables()

for num,i in enumerate(all_tables):
    us = User(i.replace("_adm",""))
    if us.get_value_of_key("ip") == ip_ban:
        baner = Sqlite_create("_baner_")
        baner.set_key_of_value(us.name,us.get_value_of_key("ip"))
        print(f"Se baneo a {us.name}")
