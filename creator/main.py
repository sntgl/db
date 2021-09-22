import datetime

import pandas as pd
import random
import faker
import VinGenerator.vin as vin
from faker_vehicle import VehicleProvider
from faker.providers.automotive.ru_RU import Provider as RuCarProvider
from faker.providers.color.ru_RU import Provider as RuColorProvider
from datetime import datetime, timezone

fake = faker.Faker('ru_RU', seed=0)
fake.add_provider(VehicleProvider)
fake.add_provider(RuCarProvider)
fake.add_provider(RuColorProvider)

fines_amounts = [*[500] * 10,
                 *[1000] * 5,
                 *[3000] * 1,
                 *[5000] * 3, ]
cars_count_weights = [*[1] * 100,
                      *[2] * 20,
                      *[3] * 10,
                      *[4] * 8,
                      *[5] * 7,
                      *[6] * 6,
                      *[7] * 4,
                      *[8] * 2,
                      9, 10, 11, 12]
fines_counts = [*[0] * 10,
                *[1] * 10,
                *[2] * 5,
                *[3] * 4,
                *[4] * 3,
                *[5] * 2,
                *[6] * 2,
                *[7] * 2,
                *[8] * 2,
                9, 10, 11, 12]
is_paid_weights = [*[True] * 5,
                   *[False] * 1]
camera_types = [*['Стрелка-СТ'] * 4,
                *['Стрелка-СТ NEW'] * 5,
                *['Стрелка Плюс'] * 2,
                'Автоураган',
                *['Автодория'] * 2,
                *['Кордон'] * 3,
                *['Кречет-С'] * 2]
departments = [*['ЦОДД'] * 20,
               'Частный владелец',
               *['МВД'] * 2,
               *['ГИБДД'] * 3, ]
random.seed(1)


def to_sql_date(d):
    return datetime.utcfromtimestamp(d).strftime("%Y-%m-%d %H:%M")


def randomize_date(from_date=900000000, to_date=1631367760):
    return random.randint(from_date, to_date)


class Database:
    uid = 0

    def __init__(self):
        self.uid = self.__class__.uid
        self.__class__.uid += 1
        self.db = 'sobaka'

    def tolist(self):
        raise NotImplementedError()


class Camera(Database):
    def __init__(self, address_in, latitude_in, longitude_in):
        Database.__init__(self)
        self.address = address_in
        self.latitude = latitude_in
        self.longitude = longitude_in
        self.date_added = randomize_date(from_date=968679698)
        self.department = random.choice(departments)
        self.system_type = random.choice(camera_types)

    def tolist(self):
        return [self.uid, self.address, self.latitude, self.longitude, to_sql_date(self.date_added), self.department,
                self.system_type]

    def __str__(self):
        return f'{self.uid} | {self.address} | {self.latitude} | {self.longitude} | {datetime.utcfromtimestamp(self.date_added).strftime("%Y-%m-%d %H:%M")} | {self.department} | {self.system_type}'


class Owner(Database):
    def __init__(self):
        Database.__init__(self)
        self.passport_id = random.randint(2000000000, 5000000000)
        self.first_name, self.middle_name, self.last_name = fake.name().split(' ')[:3]
        self.date_birth = randomize_date(-600000000, 1031758244)
        self.city_birth = fake.city()

    def tolist(self):
        return [self.uid, self.passport_id, self.last_name, self.first_name, self.middle_name,
                datetime.utcfromtimestamp(self.date_birth).strftime("%Y-%m-%d %H:%M"), self.city_birth]

    def __str__(self):
        # return f'{self.uid} | {self.passport_id} | {self.last_name} | {self.first_name} | {datetime.utcfromtimestamp(self.date_birth).strftime("%Y-%m-%d %H:%M")} | {self.middle_name} | {self.city_birth}'
        return f'{self.uid};{self.passport_id};{self.last_name};{self.first_name};{self.middle_name};{self.date_birth};{self.city_birth}'


class Car(Database):
    def __init__(self, owner_id):
        Database.__init__(self)
        self.plate = fake.license_plate()
        self.model = fake.vehicle_make_model()
        self.color = fake.color_name()
        self.vin = vin.getRandomVin()
        self.issue_year = fake.year()
        self.owner = owner_id
        d = fake.date_between_dates(date_start=datetime(int(self.issue_year), 1, 1),
                                    date_end=datetime.now())  # ).replace(tzinfo=timezone.utc).timestamp()
        dt = datetime.combine(d, datetime.min.time())
        self.registration_date = dt.replace(tzinfo=timezone.utc).timestamp()
        self.registration_number = random.randint(1000000000, 9999999999)

    def tolist(self):
        return [self.uid, self.owner, self.model, self.color, self.plate, self.vin, self.registration_number,
                to_sql_date(self.registration_date), self.issue_year]

    def __str__(self):
        return f'{self.uid} | {self.plate} | {self.model} | {self.color} | {self.vin} | {self.issue_year} | {datetime.utcfromtimestamp(self.registration_date).strftime("%Y-%m-%d %H:%M")} | {self.owner} | {self.registration_number}'


class Fine(Database):
    def __init__(self, camera_id, car_id, registration_date):
        Database.__init__(self)
        self.camera_id = camera_id
        self.car_id = car_id
        self.date = randomize_date(max([registration_date, 1208025770]), int(datetime.now().timestamp()))
        self.description = ''
        self.is_paid = random.choice(is_paid_weights)
        self.article_id = random.randint(0, 11)

    def tolist(self):
        return [self.uid, self.camera_id, self.car_id, self.article_id, self.is_paid, to_sql_date(self.date),
                self.description]

    def __str__(self):
        return f'"{self.uid};{self.camera_id};{self.car_id};{self.date};{self.is_paid};{self.article_id};{self.date}"'
        # return f'{self.uid} | {self.camera_id} | {self.car_id} | {self.date} | {self.is_paid} | {self.amount} | {datetime.utcfromtimestamp(self.date).strftime("%Y-%m-%d %H:%M")}'

# class Articles(Database):
#     def __init__(self):
#         Database.__init__(self)
#

def generate_data():
    print('Input count of car owners: ')
    car_owners_count = int(input())

    df = pd.read_csv('../gg/cams.csv', delimiter=';', header=0)

    del df['Unnamed: 3']
    del df['Unnamed: 4']
    del df['Unnamed: 5']
    df.columns = ['address', 'latitude', 'longitude']
    cameras = []
    owners = []
    cars = []
    fines = []

    for i, line in df.iterrows():
        cameras.append(Camera(line['address'], line['latitude'], line['longitude']))
    print('Cameras reading done')
    for _ in range(car_owners_count):
        owners.append(Owner())
        for _ in range(random.choice(cars_count_weights)):
            cars.append(Car(owners[-1].uid))
    print('Car and owners created')
    for car in cars:
        for _ in range(random.choice(fines_counts)):
            fines.append(Fine(random.choice(cameras).uid, car.uid, car.registration_date))
    print('Cars created')

    print(f'Cameras {len(cameras)}:')
    for i in range(10):
        print(cameras[i])
    print('...')

    print(f'Owners {len(owners)}:')
    for i in range(10):
        print(owners[i])
    print('...')

    print(f'Cars {len(cars)}:')
    for i in range(10):
        print(cars[i])
    print('...')

    print(f'Fines {len(fines)}:')
    for i in range(10):
        print(fines[i])
    print('...')
    import csv

    with open('created/owners.csv', 'w') as myfile:
        wr = csv.writer(myfile, delimiter=",", lineterminator="\r")
        wr.writerow('')
        for owner in owners:
            wr.writerow(owner.tolist())
    with open('created/cameras.csv', 'w') as myfile:
        wr = csv.writer(myfile, delimiter=",", lineterminator="\r")
        wr.writerow('')
        for camera in cameras:
            wr.writerow(camera.tolist())
    with open('created/cars.csv', 'w') as myfile:
        wr = csv.writer(myfile, delimiter=",", lineterminator="\r")
        wr.writerow('')
        for car in cars:
            wr.writerow(car.tolist())
    with open('created/fines.csv', 'w') as myfile:
        wr = csv.writer(myfile, delimiter=",", lineterminator="\r")
        wr.writerow('')
        for fine in fines:
            wr.writerow(fine.tolist())


def main():
    import psycopg2
    conn = psycopg2.connect("dbname=postgres user=postgres password='123'")
    try:
        # read the connection parameters
        # params = config()
        # connect to the PostgreSQL server
        # conn = psycopg2.connect(**params)
        conn.autocommit = True
        cur = conn.cursor()
        # create table one by one
        # for command in commands:
        # cur.execute(open("create.sql", 'r').readlines())
        cur.execute(open("created/create.sql", "r").read())
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    generate_data()
    # main()
