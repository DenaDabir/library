from datetime import date, datetime, timedelta
import enum
import sqlite3



class Person :
    
    def __init__(self , name , national_number):
        self.name = name
        self.national_number = national_number
        self.memberships = [] 

    
class Employee(Person) :
    def __init__(self, name, national_number , role: Role):
        super().__init__(name, national_number )   
        self.role = role

    
class Role(enum.Enum) :
    boss = 1
    ketab_dar = 2
    mostakhdem = 3

class Membership :
    
    def __init__(self , person : Person , employee  : Employee , 
                 start_time :datetime , finish_time :datetime , type ):
        self.person = person
        self.created_by =employee
        self.start_time =start_time
        self.finish_time =finish_time
        self.type =type
        self.borrows = []
        


class Membershiptype(enum.Enum) :
    spacial = 1
    normal = 2

class Borrow :
    def __init__(self , book :Book , membership :Membership, start_time :datetime ,
                  expected_finish_time  :datetime, actual_finish_time :datetime = None):
        self.book = book
        self.membership = membership
        self.start_time = start_time
        self.expected_finish_time = expected_finish_time
        self.actual_finish_time = actual_finish_time

    
class Book :
    def __init__(self ,name  , page_count , book_id):
        self.name = name
        self.page_count = page_count
        self.borrows = []
        self.id = book_id


persons = []
books = []
memberships = []

def setup_library():

    connection = sqlite3.connect("library.db")

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS persons(
            id INTEGER PRIMARY KEY AUTOINCREMENT ,
            name TEXT NOT NULL ,
            national_id TEXT NOT NULL
        )
    """)

    connection.commit()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS role(
        id INTEGER PRIMARY KEY AUTOINCREMENT ,
        role_name TEXT NOT NULL)
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS membership_type(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        membership_type_name TEXT NOT NULL
        )  
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees(
        id INTEGER PRIMARY KEY AUTOINCREMENT ,
        national_id TEXT NOT NULL ,
        role TEXT NOT NULL,
        FOREIGN KEY (national_id)
            REFERENCES persons(national_id) ,
        FOREIGN KEY (role)
            REFERENCES role(id)
        )"""
        )

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS memberships (
    id INTEGER PRIMARY KEY AUTOINCREMENT ,
    person_id ,
    created_by ,
    start time NOT NULL ,
    finish_time NOT NULL , 
    membership_type ,
    FOREIGN KEY (person_id)
        references persons(id) ,
    FOREIGN KEY (created_by) 
        REFERENCES employees(id) ,
    FOREIGN KEY (membership_type)
        REFERENCES membership_type(id))
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS borrow (
        id INTEGER PRIMARY KEY AUTOINCREMENT ,
        book INTEGER,
        membership INTEGER,
        start_time ,
        expected_finish_time ,
        actual_finish_time ,
        FOREIGN KEY (book)
            REFERENCES book(id) ,
        FOREIGN KEY (membership)
            REFERENCES membership(id))
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Books (
            id INTEGER PRIMARY KEY AUTOINCREMENT ,
            name TEXT NOT NULL,
            page_count INTEGER NOT NULL
        )
    """)


    connection.commit()


def has_conflict(start1, finish1, start2, finish2) -> bool:
    if start2  > finish1 or finish2 < start1 :
        return False
    else :
        return True

def create_membership(creator: Employee, person_name: str , person_national_number: str , membershipType , membershipDurationInMonth: int) :
    does_person_exists = False
    for person in persons:
        if person.national_number == person_national_number :
            if person.name != person_name :
                raise Exception("person with this national code already exists but with diffrent name ")

            does_person_exists = True
            break
 
    start_time = datetime.now()
    finish_time = start_time + timedelta(30*membershipDurationInMonth)

    #print(does_person_exists)
    if does_person_exists == False:
        person = Person(person_name, person_national_number)
        persons.append(person)
    #else:
    for previous_membership in person.memberships:
        if has_conflict(previous_membership.start_time, previous_membership.finish_time, start_time, finish_time):
            raise "there is already some membership in this time period"

    membership = Membership(person, creator, start_time, finish_time, membershipType)
    person.memberships.append(membership)

    memberships.append(membership)
    return membership

def borrow_book( book , membership , duration_in_days) :

    start_time = datetime.now()
    finish_time = datetime.now() + timedelta(duration_in_days )

    # 0 : book is available (has no active borrow)
    for borrow in book.borrows :
            if borrow.actual_finish_time == None :
                raise "this book has active borrow"

    # 0-1: membership is active 
    if membership.finish_time < finish_time :
        raise "this membership is not active "

    #0-2 : membership has no active borrow
    for borrowed in membership.borrows :
        if borrowed.actual_finish_time == None :
            raise "this membership has not returned book"

    # 1 : create borrow object
    new_borrow = Borrow(book , membership , start_time ,finish_time)
    # 3 : add borrow to membership
    membership.borrows.append(new_borrow)
    # 2 : add borrow to book
    book.borrows.append(new_borrow)


def return_book(borrow) :
    if borrow.actual_finish_time != None :
        raise "this membership has no borrowed book at the moment"
    
    borrow.actual_finish_time = datetime.now()

def add_book(book : Book ) :
    for cbook in books :
        if cbook.id == book.id :
            raise "this book is exists in library book's list"
        
    books.append(book)


setup_library()
