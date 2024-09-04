import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL':'https://faceattendancetesting-default-rtdb.firebaseio.com/'
})

ref = db.reference('Students')

data = {
    '240901':
    {
        'name': 'Dhananjaya Mudunkotuwa',
        'field': 'Data Science',
        'starting_year': 2021,
        'total_attendance': 20,
        'standing': 'Good',
        'year': 4,
        'Last_attendance_time': '2024-08-31 22:00:00'
    },
    '240902':
    {
        'name': 'Chris Evans',
        'field': 'Acting',
        'starting_year': 2022,
        'total_attendance': 14,
        'standing': 'Mid',
        'year': 3,
        'Last_attendance_time': '2024-08-31 22:00:00'
    },
    '240903':
    {
        'name': 'Scarlett Johanson',
        'field': 'Acting',
        'starting_year': 2023,
        'total_attendance': 16,
        'standing': 'Bad',
        'year': 1,
        'Last_attendance_time': '2024-08-31 22:00:00'
    },
    '240904':
    {
        'name': 'Elon Musk',
        'field': 'Entrepreneur',
        'starting_year': 2020,
        'total_attendance': 26,
        'standing': 'Good',
        'year': 2,
        'Last_attendance_time': '2024-08-31 22:00:00'
    },
    '240905':
    {
        'name': 'Lionel Messi',
        'field': 'Footballer',
        'starting_year': 2022,
        'total_attendance': 22,
        'standing': 'Mid',
        'year': 4,
        'Last_attendance_time': '2024-08-31 22:00:00'
    }
}

for key, value in data.items():
    ref.child(key).set(value)