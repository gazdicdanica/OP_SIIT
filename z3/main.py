from app.constants import *
from app.record import Record
from app.hash_file import HashFile
import datetime

active_file = None


def empty_file():
    file_name = input("\nUnesite zeljeno ime nove datoteke: ").strip()
    while file_name == "":
        print("Morate uneti ime datoteke!")
        file_name = input("\nUnesite zeljeno ime nove datoteke: ").strip()
    rec = Record(ATTRIBUTES_DATA, ATTRIBUTES_HEADER, FMT_DATA, FMT_HEADER, CODING)
    if file_name.endswith(".dat"):
        f = HashFile("./data/" + file_name, rec, F, B)
    else:
        f = HashFile("./data/" + file_name + ".dat", rec, F, B)
    f.init_file()
    print("\nDatoteka imena", file_name, "je uspesno kreirana." )


def choose_active():
    global active_file
    file_name = input("\nUnesite ime datoteke koju zelite da oznacite kao aktivnu: ").strip()
    try:
        if not file_name.endswith(".dat"):
            file_name += ".dat"
        rec = Record(ATTRIBUTES_DATA, ATTRIBUTES_HEADER, FMT_DATA, FMT_HEADER, CODING)
        x = open("./data/" + file_name)
        x.close()
        file = HashFile("./data/" + file_name, rec, F, B)
        active_file = file
        active_file.update_e()
        print("Uspesno ste izabrali aktivnu datoteku.")
    except FileNotFoundError:
        print("Ne postoji datoteka sa ovim imenom.")
        return


def show_active():
    global active_file
    if not active_file:
        print("\nNijedna datoteka nije trenutno aktivna")
    else:
        path = active_file.filename.split("/")
        print(path[2])


def print_file():
    global active_file
    if not active_file:
        print("\nNijedna datoteka nije trenutno aktivna")
        return
    print("\n")
    print("-------------------------------------------------" * 3)
    active_file.print_file()
    print("-------------------------------------------------" * 3)


def find_record():
    global active_file
    if not active_file:
        print("\nNijedna datoteka nije trenutno aktivna")
        return
    id = input("\nUnesite ID sloga: ").strip()
    try:
        int(id)
    except ValueError:
        print("\nUnos nije validan!")
        return
    ret = active_file.find_by_id(id)
    if ret is None:
        print("\nNe postoji slog sa unetim ID-jem.")
        return
    record = ret[0]
    address = ret[1]
    i = ret[2]
    print("\n")
    print("----------------------------------------------------------------" * 3)
    print("Baket {}".format(ret[3]))
    print("Adresa baketa {}".format(address))
    print("Redni broj sloga u baketu {}".format(i))
    print(record)
    print("----------------------------------------------------------------" * 3)


def add_record():
    global active_file
    if not active_file:
        print("Nijedna datoteka nije trenutno aktivna.")
        return
    while True:
        print("\n\n----------------------------------------------")
        id = input("ID (8 cifara): ")
        # if len(id) != 8:
        #     print("ID mora da sadrzi 8 cifara!")
        #     return
        # try:
        #     int(id)
        # except ValueError:
        #     print("\nUneti ID nije validan!")
        #     return
        s_address = input("Adresa posiljaoca: ")
        date = input("Datum i vreme (dd.MM.yyyy. HH:mm): ")
        # try:
        #     datetime.datetime.strptime(date, "%d.%m.%Y. %H:%M")
        # except ValueError:
        #     print("\nUneti datum nije validan!")
        #     return
        r_address = input("Adresa primaoca: ")
        price = input("Cena: ")
        # try:
        #     int(price)
        # except ValueError:
        #     print("\nUnos nije validan!")
        #     return
        print("----------------------------------------------")
        rec = {"id": id,
               "senderAddress": s_address,
               "dateTime": date,
               "receiveAddress": r_address,
               "price": int(price),
               "u": "",
               "status" : 1}

        success = active_file.insert_record(rec)
        if success:
            print("Slog sa ID-jem", id, "je uspesno dodat.")
        else:
            print("Vec postoji slog sa ID-jem", id, ",dodavanje nije moguce.")
        choice = input("\nkraj? (d/n):").lower()
        if choice == "d":
            break
        elif choice == "n":
            continue
        else:
            print("Nepostojeca opcija. Upis je prekinut.")
            return


def delete():
    global active_file
    if not active_file:
        print("Nijedna datoteka nije trenutno aktivna")
        return
    id = input("\nUnesite ID sloga za brisanje: ")
    try:
        int(id)
    except ValueError:
        print("\nUnos nije validan")
        return
    success = active_file.delete_by_id(id)
    if not success:
        print("Ne postoji slog sa ID-jem", id, ", brisanje nije moguce")
    else:
        print("Uspesno obrisan slog sa ID-jem", id)



def main_menu():
    while True:
        print("\n\n===================================================")
        print("1. Formiranje prazne datoteke")
        print("2. Izbor aktivne datoteke")
        print("3. Prikaz naziva aktivne datoteke")
        print("4. Upis novog sloga u aktivnu datoteku")
        print("5. Pretraga sloga u aktivnoj datoteci")
        print("6. Prikaz svih slogova u aktivnoj datoteci")
        print("7. Brisanje sloga iz aktivne datoteke")
        print("x. Izlaz")
        print("===================================================")

        choice = input(">>")

        if choice == "1":
            empty_file()
        elif choice == "2":
            choose_active()
        elif choice == "3":
            show_active()
        elif choice == "4":
            add_record()
        elif choice == "5":
            find_record()
        elif choice == "6":
            print_file()
        elif choice == "7":
            delete()
        elif choice == "x":
            break
        else:
            print("\nNepostojeca opcija. Pokusajte ponovo")


if __name__ == "__main__":
    main_menu()