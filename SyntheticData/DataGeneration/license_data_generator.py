# All required modules and initialisations for the person class.
import random
from datetime import datetime, date, timedelta
from faker import Faker
import pandas as pd

fake = Faker('en_GB')

class License:
    """This is a class to generate a synthetic driving license for a person and all the associated identity data for them.
This inludes their First Name, Last Name, Date of Birth, Place of Birth, Date of Issue, Date of Expiry, Issuing Authority, 
Driver Number, Address and Gender."""
    @staticmethod
    def f_name():
        """ Function to return a fake first name for the person."""
        return fake.first_name()
    
    @staticmethod
    def l_name():
        """ Function to return a fake last name for the person."""
        return fake.last_name()
    
    @staticmethod
    def date_of_birth():
        """ Function to return a fake date of birth for the person. To meet criteria this will be any date after 1950, and before 17 years ago from today"""
        # Specify constraints for the earliest and latest possible dates of birth.
        today = date.today()
        earliest_dob = date(1950, 1, 1) # After 1950.
        lastest_dob = today - timedelta(days=17*365)  # 17 years ago from today.

        # Uses constraints to generate a date. 
        date_of_birth = fake.date_between_dates(earliest_dob, lastest_dob)
        return date_of_birth.strftime('%d.%m.%Y')

    @staticmethod   
    def birthplace():
        """ Function to return a fake birthplace for the person."""
        return fake.country()
    
    @staticmethod
    def gender():
        """ Function to return a gender for the person."""
        gender = fake.random_element(elements=('Male', 'Female'))
        return gender
    
    @staticmethod
    def date_of_issue(date_of_birth):
        """ Function to return a fake date of issue for the person's license. To meet criteria this will be any date 17 years from their date of birth, and before today."""
        # Specify constraints for the earliest and latest possible dates of issue.
        dob = datetime.strptime(date_of_birth, '%d.%m.%Y')
        earliest_issue = dob + timedelta(days=17*365)  # 17 years after date of birth.
        latest_issue = date.today()  # Cant be issued after today.

        # Use constraints to generate a date.
        date_of_issue = fake.date_between(start_date=earliest_issue, end_date=latest_issue)
        return date_of_issue.strftime('%d.%m.%Y')
    
    @staticmethod
    def date_of_expiry(date_of_issue):
        """ Function to return a fake date of expiry for the person's license, which is 10 years from the date of issue."""
        date_of_issue = datetime.strptime(date_of_issue, '%d.%m.%Y')
        date_of_expiry = date_of_issue + timedelta(days=10*365)  # 10 years after date of issue
        return date_of_expiry.strftime('%d.%m.%Y')
    
    @staticmethod
    def issuing_authority():
        """ Function to return the issuing authority for the persons license, which for this dataset will be DA1. """
        return "DA1"

    @staticmethod
    def license_num(first_name, last_name, gender, date_of_birth):
        """ Function to generate a synthetic license number following a set of constraints."""
        # Digits 1-5: Process the name for the first 5 characters, accounting for special case of "Mac".
        l_name = last_name.upper().replace("MAC", "MC").ljust(5, '9')[:5]

        # Digit 6: Get the decade digit from the year of birth.
        decade_digit = date_of_birth[8]

        # Digits 7-8: Get the month of birth in a two digit format, where the number is incremented by 50 if the person is female.
        month_digit = str(int(date_of_birth[3:5])).zfill(2)
        if gender.lower() == 'female':
            month_digit = str(int(month_digit) + 50).zfill(2)

        # Digits 9-10: Get the day within the month of the day of birth in two digit format.
        day_digit = date_of_birth[:2].zfill(2)

        # Digit 11: Get the year digit from the year of birth.
        year_digit = date_of_birth[9]

        # Digits 12-14: Get the first letter of the first name and pad it with a 99 after.
        first_initial = first_name[0].upper() + '99'

        # Digits 15-16: Generate two random letters for the last two digits.
        random_letters = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=2))

        # Concatenate all parts to create the license number.
        license_number = f'{l_name}{decade_digit}{month_digit}{day_digit}{year_digit}{first_initial}{random_letters}'
        return license_number

    @staticmethod
    def address():
        """ Function to generate a synthetic UK address. """
        # Generate each of the 3 address components.
        street_address = str(random.randint(1, 999)) + " " + fake.street_name()
        city = fake.city()
        postcode = fake.postcode()

        # Format it all together.
        comma = ", "
        address = f"{street_address}{comma}{city}{comma}{postcode}"
        return address
    
    @staticmethod
    def generate_credentials():
        """ Function to call the other functions to generate the different data for a person. """
        first_name = License.f_name()
        last_name = License.l_name()
        date_of_birth = License.date_of_birth()
        birthplace = License.birthplace()
        gender = License.gender()
        date_of_issue = License.date_of_issue(date_of_birth)
        date_of_expiry = License.date_of_expiry(date_of_issue)
        issuing_authority = License.issuing_authority()
        license_num = License.license_num(first_name, last_name, gender, date_of_birth)
        address = License.address()

        return pd.DataFrame({
            "First Name": [first_name],
            "Last Name": [last_name],
            "Date of Birth":[date_of_birth],
            "Place of Birth":[birthplace],
            "Gender":[gender],
            "Date of Issue":[date_of_issue],
            "Date of Expiry":[date_of_expiry],
            "Issuing Authority":[issuing_authority],
            "License Number":[license_num],
            "Address":[address]
        })


