from datetime import datetime
from app.serial_file import SerialFile
from app.constants import *
from app.record import Record
from app.sequential_file import SequentialFile
import os


active_file = None
change_file_ser = None
change_file_seq = None
mistake_file = None


def empty_file():
    global active_file
    rec = Record(ATTRIBUTES, FMT, CODING)
    f_name = input("\nUnesite zeljeno ime datoteke: ").strip()
    if f_name == "":
        print("Greska! Ime datoteke ne moze biti prazan string.")
        return

    if f_name.endswith(".dat"):
        f = SequentialFile("./data/" + f_name , rec, F)
    else:
        f = SequentialFile("./data/" + f_name + ".dat", rec, F)
    f.init_file()

    print("Datoteka imena '"+ f_name + "' je uspesno kreirana.")



def choose_active():
    global active_file
    file_name = input("\nUnesite ime datoteke koju zelite da postavite za aktivnu: ").strip()
    try:
        if not file_name.endswith(".dat"):
            file_name += ".dat"
        rec = Record(ATTRIBUTES, FMT, CODING)
        x = open("./data/" + file_name)
        x.close()
        file = SequentialFile("./data/" + file_name, rec, F)
        active_file = file
        print("Uspesno ste izabrali aktivnu datoteku.")
    except FileNotFoundError:
        print("Ne postoji datoteka sa ovim imenom.")
        return 


def show_active():
    global active_file 
    if not active_file:
        print("\nNijedna datoteka nije trenutno aktivna")
    else:
        print(active_file.filename)


def change_add(choice):
    id = input("\nID (8 cifara): ")
    while (len(id) != 8 and not isinstance(id, int)):
        print("!ID mora sadrzati 8 cifara!\n")
        id = input("ID (8 cifara): ")
    registration = input("Registarska oznaka vozila: ").strip()
    while len(registration) > 10 :
        print("!Registarska oznaka vozila moze da sadrzi do 10 karaktera!")
        registration = input("Registarska oznaka vozila: ").strip()
    date = datetime.strftime(datetime.now(), "%d.%m.%Y. %H:%M:%S")
    ramp = input("Oznaka naplatne rampe: ")
    while len(ramp) != 4:
        print("!Oznaka naplatne rampe mora da sadrzi tacno 4 znaka!")
        ramp = input("Oznaka naplatne rampe: ")
    tr = False
    while not tr:
        try:
            value = int(input("Placeni iznos: "))
            tr = True
        except ValueError:
            print("Unesite celobrojnu vrednost!")
    if choice == "1":
        return {"id" : id,
                "registration" : registration,
                "date" : date,
                "ramp" : ramp,
                "value" : value,
                "status" : 1}
    else:
        return {"id" : id,
                "registration" : registration,
                "date" : date,
                "ramp" : ramp,
                "value" : value,
                "status" : 2}


def delete():
    id = input("\nID (8 cifara): ")
    while (len(id) != 8 and not isinstance(id, int)):
        print("!ID mora sadrzati 8 cifara!\n")
        id = input("ID (8 cifara): ")
    return {"id": id,
            "registration" : "",
            "date" : "",
            "ramp" : "",
            "value": 0,
            "status" : 3}

def change_data():
    global active_file
    global change_file_ser
    while not active_file:
        choose_active()
    if not change_file_ser:
        rec = Record(ATTRIBUTES, FMT, CODING)
        change_file_ser = SerialFile("./data/datoteka_promene.dat", rec, F)
    change_file_ser.init_file()
    items = []
    while True:
        print("\n\n1. Izmena\n2. Dodavanje\n3. Brisanje\nx. Odustani")
        choice = input(">>")
        if choice == "1" or choice == "2":
            item = change_add(choice)
            items.append(item)
        elif choice == "3":
            items.append(delete())
        elif choice == "x":
            break
        else:
            print("Nepostojeca opcija.")
    for i in range(len(items)):
        change_file_ser.insert_record(items[i])


def make_seq():
    global change_file_ser
    global change_file_seq

    if not change_file_ser:
        print("\nNe postoje izmene koje mozemo da primenimo.")
        return

    size = os.path.getsize(change_file_ser.filename)
    blocks = size/(RECORD_SIZE * F)
    li = []

    rec = Record(ATTRIBUTES, FMT, CODING)
    change_file_seq = SequentialFile("./data/sekvencijalna_datoteka_promene.dat", rec, F)
    change_file_seq.init_file()

    with open(change_file_ser.filename, "rb") as serial:
        for i in range(int(blocks)):
            block = change_file_ser.read_block(serial)
            for dict in block:
                li.append(dict)
        li = [i for i in li if i['id']!='-1']
        li.sort(key=lambda x: int(x['id']))

        for record in li:
            change_file_seq.insert_record(record)


def make_record(id, mistake):
    return {'id': id,
            'registration': "",
            "date": mistake,
            "ramp": "",
            "value": 0,
            "status": 0}

def output():
    global change_file_seq
    global change_file_ser
    global active_file
    global mistake_file

    rec = Record(ATTRIBUTES, FMT, CODING)
    if not mistake_file:
        mistake_file = SerialFile("./data/datoteka_gresaka.dat", rec, F)
        mistake_file.init_file()
    else:
        mistake_file = SerialFile("./data/datoteka_gresaka.dat", rec, F)

    f_name = input("\nUnesite ime datoteke u koju zelite da upisujete promene: ").strip()
    if not f_name.endswith(".dat"):
        f_name += ".dat"
    while f_name == active_file.filename:
        f_name = input("Ova datoteka je izabrana kao aktivna. Unesite drugu: ")
        if not f_name.endswith(".dat"):
            f_name += ".dat"

    output_file = SequentialFile("./data/" + f_name, rec, F)
    output_file.init_file()

    print("\n------------------------------------------------\n")

    with open(active_file.filename, "rb") as active, open(change_file_seq.filename, "rb") as change:

        change_record = change_file_seq.read_record(change)
        active_record = active_file.read_record(active)

        while True:

            if change_record['id'] == '-1':
                while active_record['id'] != '-1':
                    active_record['status'] = 0
                    output_file.insert_record(active_record)
                    active_record = active_file.read_record(active)
                break
            elif active_record['id'] == '-1':
                while change_record['id'] != '-1':
                    if change_record['status'] == 1:
                        print("Ne postoji slog sa id-jem",change_record['id'] + ", promena nije moguca")
                        mistake_file.insert_record(make_record(change_record['id'], "nepostojeci slog"))
                        change_record = change_file_seq.read_record(change)
                    elif change_record['status'] == 3:
                        print("Ne postoji slog sa id-jem", change_record['id'] + ", brisanje nije moguce")
                        mistake_file.insert_record(make_record(change_record['id'], "nepostojeci slog"))
                        change_record = change_file_seq.read_record(change)
                    else:
                        change_record['status'] = 0
                        output_file.insert_record(change_record)
                        print("Uspesno dodat slog sa id-jem", change_record['id'])
                        change_record = change_file_seq.read_record(change)
                break


            if int(active_record['id']) < int(change_record['id']):
                active_record['status'] = 0
                output_file.insert_record(active_record)
                active_record = active_file.read_record(active)
            else:
                if int(active_record['id']) == int(change_record['id']):
                    if change_record['status'] == 1:
                        print("Uspesno promenjen slog sa id-jem", change_record['id'])
                        change_record['status'] = 0
                        output_file.insert_record(change_record)
                        active_record = active_file.read_record(active)
                        change_record = change_file_seq.read_record(change)
                    elif change_record['status'] == 3:
                        print("Uspesno obrisan slog sa id-jem", change_record['id'])
                        active_record = active_file.read_record(active)
                        change_record = change_file_seq.read_record(change)
                    else:
                        print("Vec postoji slog sa id-jem", change_record['id'])
                        mistake_file.insert_record(make_record(change_record['id'], "slog vec postoji"))
                        change_record = change_file_seq.read_record(change)
                else:
                    if change_record['status'] == 2:
                        print("Uspesno dodat slog sa id-jem", change_record['id'])
                        change_record['status'] = 0
                        output_file.insert_record(change_record)
                        change_record = change_file_seq.read_record(change)
                    elif change_record['status'] == 1:
                        print("Ne postoji slog sa id-jem", change_record['id'] + ", promena nije moguca.")
                        mistake_file.insert_record(make_record(change_record['id'], "nepostojeci slog"))
                        change_record = change_file_seq.read_record(change)
                    else:
                        print("Ne postoji slog sa id-jem",change_record['id'] + ", brisanje nije moguce.")
                        mistake_file.insert_record(make_record(change_record['id'], "nepostojeci slog"))
                        change_record = change_file_seq.read_record(change)


    # mistake_file.print_file()
    change_file_seq.init_file()
    change_file_ser.init_file()

    active_file = output_file


def print_file():
    while not active_file:
        choose_active()
    print("\n------------------------------------------------------------------------------------------------------------")
    active_file.print_file()
    print("--------------------------------------------------------------------------------------------------------------\n")


def main_menu():
    while True:
        print("\n\n==========================================")
        print("1. Formiranje prazne datoteke")
        print("2. Izbor aktivne datoteke")
        print("3. Prikaz naziva aktivne datoteke")
        print("4. Izmena podataka")
        print("5. Primena izmena")
        print("6. Prikaz slogova aktivne datoteke")
        print("x. Izlaz")
        print("==========================================")
        choice = input(">>")

        if choice == "1":
            empty_file()

        elif choice == "2":
            choose_active()
        
        elif choice == "3":
            show_active()

        elif choice == "4":
            change_data()

        elif choice == "5":
            make_seq()
            output()

        elif choice == "6":
            print_file()

        elif choice == "x":
            print("Dovidjenja!")
            break

        else:
            print("Nepostojeca opcija. Pokusajte ponovo.")

        
if __name__ == "__main__":
    main_menu()