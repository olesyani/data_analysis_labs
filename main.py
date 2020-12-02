import csv
import os
import pandas as pd
import datetime

database_path = "data.csv"


# функция позволяет вывести весь справочник
def view_database():
    df = pd.read_csv(database_path)
    pd.set_option('display.max_columns', 20)
    pd.set_option('display.width', 2000)
    print(df)


# проверяет, содержит ли имя неразрешенные символы, если да - запускается рекурссия, пока имя не будет правильным
# второй аргумент функции отвечает за то, имя это или фамилия (чтобы вывести нужное сообщение)
def name_correctness(name, i):
    while not (name.replace(' ', '')).isalnum() or not name.isascii():
        if i == 0:
            print("You used wrong symbols in the name, try again")
            name_extra = input("Please, enter name: ")
        else:
            print("You used wrong symbols in the surname, try again")
            name_extra = input("Please, enter surname: ")
        name = name_correctness(name_extra, i)
    return name


# проверяет, правильно ли введен номер телефона, если все хорошо, то возращает в формате 8ХХХХХХХХХХ
# если нет - запускается рекурссия
def phone_fmt(phone_num):
    if len(phone_num) == 10 and phone_num.isdigit():
        return '8' + phone_num
    if len(phone_num) == 11 and phone_num[0] == '8' and phone_num.isdigit():
        return str(phone_num)
    if len(phone_num) == 12 and phone_num[0:2] == "+7" and phone_num[1:].isdigit():
        return '8' + phone_num[2:]
    else:
        phone = input("Wrong format, try again: ")
        phone = phone_fmt(phone)
        return phone


# функция позволяет вывести записи, удовлетворяющие некоторым параметрам
def search():
    # выбор ключей
    ind = input("By what parameters to search?\nname (1), surname (2), age (3), mobile phone "
                "(4), work phone (5), home phone (6)\nUse , if you want to delete several (f.e. 2,4,5): ")
    while (ind.replace(',', '')).isdigit() == 0:
        ind = input("Wrong format, try again: ")
    list = ind.split(',')
    df = pd.read_csv(database_path)
    tmp = df
    # инициализирование выбранных ключей
    for i in list:
        if i == '1':
            name = input("Enter the name: ")
            name = name_correctness(name, 0)
            name = (name.lower()).title()
            df = df[df["Name"] == name]
            # позволяет сохранять удовлетворяющие конкретному параметру и всем предыдущим записи
        elif i == '2':
            surname = input("Enter the surname: ")
            surname = name_correctness(surname, 1)
            surname = (surname.lower()).title()
            df = df[df["Surname"] == surname]
        elif i == '3':
            age = input("Enter the age: ")
            while age.isdigit() == 0:
                age = input("It is not a number, please, enter the age again: ")
            if 0 < int(age) <= 9:
                age = '0' + age
            df = df[df["Age"] == age]
        elif i == '4':
            mob_phone = input("Enter the mobile phone, please: ")
            mob_phone = phone_fmt(mob_phone)
            df = df[df["Mobile Phone"] == mob_phone]
        elif i == '5':
            w_phone = input("Enter the work phone, please: ")
            w_phone = phone_fmt(w_phone)
            df = df[df["Work Phone"] == w_phone]
        elif i == '6':
            h_phone = input("Enter the home phone, please: ")
            h_phone = phone_fmt(h_phone)
            df = df[df["Home Phone"] == h_phone]
        else:
            print("Wrong index")
    print(df)


# проверяет, может ли быть у человека такая дата рождения
def date_correctness(birth_date):
    if birth_date.isdigit() == 0:
        birth_date = birth_date.replace("/", "")
    try:
        date = datetime.datetime.strptime(birth_date, '%d%m%Y')
    except ValueError:
        print("Wrong date or format, try again")
        birth_date = input("Enter the birth date: ")
        birth_date = date_correctness(birth_date)
        return birth_date
    else:
        today = (datetime.datetime.now()).strftime('%Y%m%d')
        if date.strftime('%Y%m%d') > today:
            print("Future date, try again")
            birth_date = input("Enter the birth date: ")
            birth_date = date_correctness(birth_date)
        return birth_date


# проверяет, правильно ли введена дата рождения, если все хорошо, то возращает в формате DD/MM/YYYY
# если нет - запускается рекурссия
def date_fmt(birth_date):
    if birth_date.isdigit() == 0:
        birth_date = birth_date.replace("/", "")
    if len(birth_date) == 8 and birth_date.isdigit():
        date = date_correctness(birth_date)
        return date[0:2] + "/" + date[2:4] + "/" + date[4:]
    else:
        birth_date = input("Wrong format, try again: ")
        birth_date = date_fmt(birth_date)
        return birth_date


# присваивает человеку возраст, опираясь на полученную дату рождения
def age_from(birth_date):
    birth_date = datetime.datetime.strptime(birth_date.replace("/", ""), '%d%m%Y')
    today = datetime.datetime.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    if 0 < int(age) <= 9:
        age = '0' + str(age)
    return age


# проверяет, есть ли уже человек с таким именем и фамилией
def exist(name, surname):
    name = name_correctness(name, 0)
    surname = name_correctness(surname, 1)
    if in_row(name, surname) != -1:
        command = input("This person is already in the phonebook, do you want to try again? (Yes/No)")
        if command.casefold() == 'yes':
            name_extra = input("Please, enter name: ")
            surname_extra = input("Please, enter surname: ")
            name, surname = exist(name_extra, surname_extra)
            return name, surname
        else:
            command = input("Do you want to edit the record with these name and surname? (Yes/No)")
            if command.casefold() == 'yes':
                edit_row(name, surname)
            return 'no', 'addition'
    return name, surname


# добавление новой записи в справочнике
def add(name, surname):
    # вызывает фукнцию проверки на уникальность комбинации имени и фамилии
    name, surname = exist(name, surname)
    if name == 'no' and surname == 'addition':
        return
    name = (name.lower()).title()
    surname = (surname.lower()).title()
    birth_date, work_phone, home_phone, age = "-", "-", "-", "-"
    # далее поочередно узнает данные от пользователя, при этом учитывая, что не все поля обязательны и можно
    # отказаться от их заполнения
    answer = input("Do you want to write a birth date? (Yes/No) ")
    if answer.casefold() == 'yes':
        birth_date = input("Enter the birth date (DD/MM/YYYY or DDMMYYYY): ")
        birth_date = date_fmt(birth_date)
        age = age_from(birth_date)
    mob_phone = input("Enter the mobile phone, please: ")
    mob_phone = phone_fmt(mob_phone)
    answer = input("Do you want to write a work phone? (Yes/No) ")
    if answer.casefold() == 'yes':
        work_phone = input("Enter the work phone, please: ")
        work_phone = phone_fmt(work_phone)
    answer = input("Do you want to write a home phone? (Yes/No) ")
    if answer.casefold() == 'yes':
        home_phone = input("Enter the home phone, please: ")
        home_phone = phone_fmt(home_phone)
    person = {"Name": name, "Surname": surname, "Birth Date": birth_date, "Age": age, "Mobile Phone": mob_phone,
              "Work Phone": work_phone, "Home Phone": home_phone}
    # записываем новую строку в таблицу
    with open(database_path, 'a') as dataframe:
        writer = csv.DictWriter(dataframe, fieldnames=columns)
        writer.writerow(person)


# возвращает индекс строки с данными именем и фамилией
def in_row(name, surname):
    with open(database_path, 'r') as file:
        df = csv.reader(file)
        index = -1
        for row in df:
            index += 1
            if row[0].casefold() == name.casefold() and row[1].casefold() == surname.casefold():
                return index - 1
        return -1


# изменяем запись с указанными именем и фамилией
def edit_row(name, surname):
    i = in_row(name, surname)
    # если запись не найдена, тогда предлагаем пользователю сохранить в справочник нового человека
    # или ввести имя и фамилию заново
    if i == -1:
        answer = input("This person isn't in the phonebook, do you want to add him/her? (Yes/No): ")
        if answer.casefold() == 'yes':
            add(name, surname)
        else:
            answer = input("Do you want to try editing again? (Yes/No): ")
            if answer.casefold() == 'yes':
                name_extra = input("Please, enter name: ")
                surname_extra = input("Please, enter surname: ")
                edit_row(name_extra, surname_extra)
    else:
        # в случае успешного нахождения записи выводим ее и запрашиваем, что нужно изменить
        # работает цикл до тех пор, пока пользователь не скажет, что ничего не нужно менять
        df = pd.read_csv(database_path)
        print(df.loc[i])
        command = input("What do you want to edit? Choose one: name (1), surname (2), birth date (3), mobile phone (4),"
                        " work phone (5), home phone (6), none (7)\n")
        while command.casefold() != 'none' and command != '7':
            if command.casefold() == 'name' or command == '1':
                name = input("Please, enter name: ")
                name = name_correctness(name, 0)
                while in_row(name, surname) != -1:
                    name = input("This combination already exists, enter new name or cancel (0): ")
                    name = name_correctness(name, 0)
                if name.casefold() != "cancel" and name != '0':
                    df.loc[i, "Name"] = (name.lower()).title()
            elif command.casefold() == 'surname' or command == '2':
                surname = input("Please, enter surname: ")
                surname = name_correctness(name, 1)
                while in_row(name, surname) != -1:
                    surname = input("This combination already exists, enter new surname or cancel (0): ")
                    surname = name_correctness(name, 1)
                if name.casefold() != "cancel" and surname != '0':
                    df.loc[i, "Surname"] = (surname.lower()).title()
            elif command.casefold() == 'birth date' or command == '3':
                birth_date = input("Enter the birth date (DD/MM/YYYY or DDMMYYYY) or cancel (1): ")
                birth_date = date_fmt(birth_date)
                age = age_from(birth_date)
                df.loc[i, "Birth Date"] = birth_date
                df.loc[i, "Age"] = age
            elif command.casefold() == 'mobile phone' or command == '4':
                mob_phone = input("Enter the mobile phone, please: ")
                mob_phone = phone_fmt(mob_phone)
                df.loc[i, "Mobile Phone"] = mob_phone
            elif command.casefold() == 'work phone' or command == '5':
                w_phone = input("Enter the work phone, please: ")
                w_phone = phone_fmt(w_phone)
                df.loc[i, "Work Phone"] = w_phone
            elif command.casefold() == 'home phone' or command == '6':
                h_phone = input("Enter the home phone, please: ")
                h_phone = phone_fmt(h_phone)
                df.loc[i, "Home Phone"] = h_phone
            command = input("What do you want to edit? Choose one: name (1), surname (2), birth date (3), mobile phone "
                            "(4), work phone (5), home phone (6), none (7)\n")
        # сохраняем все изменения
        df.to_csv(database_path, index=False)


# позволяет вывести записи младше/старше/такого же возраста, что и введенное число
def view_age():
    age = input("Enter the age: ")
    while age.isdigit() == 0:
        age = input("It is not a number, try again or cancel and turn back to the command menu (0): ")
    if 0 < int(age) <= 9:
        age = '0' + age
    if age != '0':
        df = pd.read_csv(database_path)
        command = input("Do you want to view people who are: younger (1), older (2), this age (3): ")
        if command == '1' or command.casefold() == 'younger':
            print(df.loc[(df.Age < str(age)) & (df.Age != '-')])
        elif command == '2' or command.casefold() == 'older':
            print(df.loc[(df.Age > str(age)) & (df.Age != '-')])
        elif command == '3' or command.casefold() == 'this age':
            print(df.loc[df.Age == age])


# дни рождения в ближайшие 30 дней
def birthday_list():
    with open(database_path, 'r') as file:
        df = pd.read_csv(file)
        today = (datetime.datetime.today()).strftime('%Y%m%d')
        month_later = (datetime.datetime.today() + datetime.timedelta(days=30)).strftime('%Y%m%d')
        year = (datetime.datetime.today()).strftime('%Y')
        ind = []
        for index, row in df.iterrows():
            if row[2] != '-':
                if today <= year + row[2][3:5] + row[2][0:2] < month_later:
                    ind.append(index)
        print(df.loc[ind, "Name":"Birth Date"])


# удалить строку по имени и фамилии
def delete_row(name, surname):
    i = in_row(name, surname)
    if i == -1:
        answer = input("There is not anyone with these identifiers. Do you want to try again? (Yes/No): ")
        if answer.casefold() == 'yes':
            name_extra = input("Please, enter name: ")
            surname_extra = input("Please, enter surname: ")
            delete_row(name_extra, surname_extra)
    else:
        df = pd.read_csv(database_path)
        df = df.drop(i)
        df.to_csv(database_path, index=False)
        print(df)


# возвращает список из индексов строк, номера мобильных телефонов которых совпадают с аргументом
def phone_in(phone):
    list = []
    with open(database_path, 'r') as file:
        df = csv.reader(file)
        index = -1
        for row in df:
            index += 1
            if row[4] == phone:
                list.append(index - 1)
        return list


# удаляет записи по номеру телефона
def delete_by_phone(mob_phone):
    list = phone_in(mob_phone)
    df = pd.read_csv(database_path)
    # выводит все записи с данным номером и предлагает выбрать, какие удалить
    print(df.loc[list])
    if len(list) != 0:
        ind = input("Which rows do you want to delete? Enter indexes of these rows\n"
                    "Use , if you want to delete several (f.e. 2,7,8): ")
        while (ind.replace(',', '')).isdigit() == 0:
            ind = input("Wrong format, try again: ")
        ind = ind.split(',')
        for i in ind:
            if int(i) in list:
                df = df.drop(int(i))
                print("Successfully delete the", i, "row")
            else:
                print("Cannot delete", i, "row because it is not in the given table")
        df.to_csv(database_path, index=False)
        print(df)


# при запуске обновляет возраст
def age_update():
    df = pd.read_csv(database_path)
    for index, row in df.iterrows():
        if row[2] != '-':
            df.loc[index, 'Age'] = age_from(row[2])
    df.to_csv(database_path, index=False)


if __name__ == "__main__":
    columns = ["Name", "Surname", "Birth Date", "Age", "Mobile Phone", "Work Phone", "Home Phone"]
    # на случай, если файл пустой, создаем ключи для словаря
    with open(database_path, 'a') as df:
        if os.stat(database_path).st_size == 0:
            writer = csv.DictWriter(df, fieldnames=columns)
            writer.writeheader()
    # в начале работы программы обновляет возраст у всех людей с датой рождения
    age_update()
    # далее список всевозможных функций программы
    command = input("Enter a command from the list:\nview (1) - view the whole table\nsearch (2) - search and output "
                    "according to certain parameters\nadd (3) - add a new entry\nedit (4) - edit an existing entry\n"
                    "view by age (5) - record output based on age\nbirthday list (6) - birthdays next month\ndelete by "
                    "name and surname (7) - delete a record\ndelete by phone (8) - delete (a) record(s)\nquit (9)\n")
    # цикл работает до того момента, пока не примет quit
    while command.casefold() != "quit" and command != '9':
        if command.casefold() == "view" or command == '1':
            view_database()
        elif command.casefold() == "search" or command == '2':
            search()
        elif command.casefold() == "add" or command == '3':
            name = input("Please, enter name: ")
            surname = input("Please, enter surname: ")
            add(name, surname)
        elif command.casefold() == "edit" or command == '4':
            name = input("Please, enter name: ")
            surname = input("Please, enter surname: ")
            edit_row(name, surname)
        elif command.casefold() == "view by age" or command == '5':
            view_age()
        elif command.casefold() == "birthday list" or command == '6':
            birthday_list()
        elif command.casefold() == "delete by name and surname" or command == '7':
            name = input("Please, enter name: ")
            surname = input("Please, enter surname: ")
            delete_row(name, surname)
        elif command.casefold() == "delete by phone" or command == '8':
            phone = input("Please, enter phone: ")
            phone = phone_fmt(phone)
            delete_by_phone(phone)
        else:
            print("Wrong command, try again")
        command = input("Enter a command from the list:\nview (1)\nsearch (2)\nadd (3)\nedit (4)\nview by age (5)\n"
                        "birthday list (6)\ndelete by name and surname (7)\ndelete by phone (8)\nquit (9)\n")