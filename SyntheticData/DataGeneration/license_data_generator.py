# All required modules and initialisations.
import random
import string
from datetime import datetime, date, timedelta
from faker import Faker
import pandas as pd
import re

# Ensure faker uses British formatting.
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
    def driver_num(first_name, last_name, gender, date_of_birth):
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
        driver_number = f'{l_name}{decade_digit}{month_digit}{day_digit}{year_digit}{first_initial}{random_letters}'
        return driver_number

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
        driver_num = License.driver_num(first_name, last_name, gender, date_of_birth)
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
            "License Number":[driver_num],
            "Address":[address]
        })
    
    @staticmethod
    def generate_dataset(num_times):
        """ Function to generate a dataframe containing however many rows of synthetic people you want."""
        # Manually generate first row on which to append subsequent rows.
        data = License.generate_credentials()

        # Loop to generate subsequent rows and append them on.
        for i in range(num_times-1):
            synthetic_person = License.generate_credentials()
            data = pd.concat([data, synthetic_person], ignore_index=True)

        return data

class Corrupt:
    """This is a class containing functions to corrupt the data generated by the class License."""
    @staticmethod
    def introduce_name_corruption(df, column_name, corruption_level):
        """ Function that specifies the column in a database to be corrupted, as well as the corruption level (1 is Fully Corrupted)."""
        def corrupt_name(name):
            """ Function that iterates through every row in a column containing names of things to introduce corruption."""
            new_name = ''
            for char in name:
                if random.random() < corruption_level:
                    # Introduce corruption by randomly replace/add special characters or numbers.
                    new_char = random.choice(string.digits + string.punctuation)
                else:
                    new_char = char
                new_name += new_char
            return new_name
        
        # Apply the corruption function to the column.
        df[column_name] = df[column_name].apply(corrupt_name)
        return df
    
    @staticmethod
    def introduce_date_corruption(df, column_name, corruption_level):
        """ Function that specifies any date column to be corrupted, as well as the corruption level (1 is Fully Corrupted)."""
        def corrupt_date(date):
            """ Function that iterates through every row in the column containing a date to introduce corruption."""
            corrupted_date = date
            if random.random() < corruption_level:
                # Introduce various corruptions based on the corruption level.
                action = random.random()
                if action < 0.25:   # 25% chance of changing format by replacing '.' with '/'.
                    corrupted_date = date.replace('.', '/')
                elif action < 0.5:  # 25% chance of swapping day and month
                    day, month, year = date.split('.')
                    corrupted_date = f"{month}.{day}.{year}"
                else:   # 50% chance of introducing impossible values.
                    day, month, year = date.split('.')
                    corrupted_day = str(random.randint(32, 99))
                    corrupted_month = str(random.randint(13, 99))
                    corrupted_date = f"{corrupted_day}.{corrupted_month}.{year}"
            return corrupted_date
        
        # Apply the corruption function to the column.
        df[column_name] = df[column_name].apply(corrupt_date)
        return df
    
    @staticmethod
    def introduce_gender_corruption(df, column_name, corruption_level):
        """ Function that specifies the gender column to be corrupted, as well as the corruption level (1 is Fully Corrupted)."""
        def corrupt_gender(gender):
            """ Function that iterates through every row in the column containing gender to introduce corruption by returning any word that isn't Male or Female."""
            corrupted_gender = gender
            if random.random() < corruption_level:
                # Replace gender with a random word if corruption level is met.
                random_word = fake.word().capitalize()
                corrupted_gender = random_word
            return corrupted_gender

        # Apply the corruption function to the column.
        df[column_name] = df[column_name].apply(corrupt_gender)
        return df

    @staticmethod
    def introduce_authority_corruption(df, column_name, corruption_level):
        """ Function that specifies the issuing authority column to be corrupted, as well as the corruption level (1 is Fully Corrupted)."""
        def corrupt_authority(authority):
            """ Function that iterates through every row in the column containing the issuing authority to introduce corruption by returning any random word that is max 4 characters long."""
            if random.random() < corruption_level:
                new_authority = ''.join(random.choices(string.ascii_uppercase + string.digits, k=random.randint(1, 4)))
                return new_authority
            return authority

        # Apply the corruption function to the column.
        df[column_name] = df[column_name].apply(corrupt_authority)
        return df

    @staticmethod
    def introduce_drivernum_corruption(df, column_name, corruption_level):
        """ Function that specifies the driver number column to be corrupted, as well as the corruption level (1 is Fully Corrupted)."""
        def corrupt_drivernum(driver_num):
            """ Function that iterates through every row in the column containing the license number to introduce corruption by adding/deleting/replacing up to 3 characters."""
            if random.random() < corruption_level:
                num_corruptions = random.randint(1, 3)  # Number of corruptions (1 to 3 digits).
                for _ in range(num_corruptions):
                    action = random.random()
                    if action < 0.33:  # 33% chance of adding a digit/letter.
                        driver_num += random.choice(string.ascii_uppercase + string.digits)
                    elif action < 0.66:  # 33% chance of deleting a digit/letter.
                        if len(driver_num) > 0:
                            index_to_delete = random.randint(0, len(driver_num) - 1)
                            driver_num = driver_num[:index_to_delete] + driver_num[index_to_delete + 1:]
                    else:  # 33% chance of replacing a digit/letter.
                        if len(driver_num) > 0:
                            index_to_replace = random.randint(0, len(driver_num) - 1)
                            driver_num = driver_num[:index_to_replace] + random.choice(string.ascii_uppercase + string.digits) + driver_num[index_to_replace + 1:]
            return driver_num
        
        # Apply the corruption function to the column.
        df[column_name] = df[column_name].apply(corrupt_drivernum)
        return df

    @staticmethod
    def introduce_address_corruption(df, column_name, corruption_level):
        """ Function that specifies the address column to be corrupted, as well as the corruption level (1 is Fully Corrupted)."""
        def corrupt_address(address):
            """ Function that iterates through every row in the column containing the address and corrupts it by deleting some of the components, like city name or post code."""
            if random.random() < corruption_level:
                components = address.split(', ')    # Split address into separate components. 
                num_components = len(components)
                remaining_components = random.randint(0, num_components)  # Determine how many components remain.
                if remaining_components == 0:
                    return ''  # Return an empty string if no component remains.
                else:
                    return ', '.join(components[:remaining_components])
            return address
        
        # Apply the corruption function to the column.
        df[column_name] = df[column_name].apply(corrupt_address)
        return df
        
    @staticmethod
    def introduce_corruptions(df, corruption_level):
        """ Function that calls all the previous corruption methods together for all columns in the license dataframe, and lets you specify one corruption level for all columns."""
        # Call the appropriate corruption function for each column.
        df = Corrupt.introduce_name_corruption(df, 'First Name', corruption_level)
        df = Corrupt.introduce_name_corruption(df, 'Last Name', corruption_level)
        df = Corrupt.introduce_date_corruption(df, 'Date of Birth', corruption_level)
        df = Corrupt.introduce_name_corruption(df, 'Place of Birth', corruption_level)
        df = Corrupt.introduce_gender_corruption(df, 'Gender', corruption_level)
        df = Corrupt.introduce_date_corruption(df, 'Date of Issue', corruption_level)
        df = Corrupt.introduce_date_corruption(df, 'Date of Expiry', corruption_level)
        df = Corrupt.introduce_authority_corruption(df, 'Issuing Authority', corruption_level)
        df = Corrupt.introduce_drivernum_corruption(df, 'License Number', corruption_level)
        df = Corrupt.introduce_address_corruption(df, 'Address', corruption_level)
        return df
    
class Validate:
    """This is a class containing functions to validate license data that may have been corrupted. Note that for attributes dependent on prior attributes, like
    License Number, if the prior attributes are corrupt the dependent attribute will also be marked as corrupt."""
    @staticmethod
    def validate_name(df, column_name):
        """ Function that specifies a name column in a database to be validated."""
        # Create a new column for corruption status.
        new_column_name = f"{column_name} Corruption"
        column_index = df.columns.get_loc(column_name)
        df.insert(column_index + 1, new_column_name, 0)  # Inserting next to the specified column.
        
        # Define a regular expression pattern to match only letters.
        pattern = re.compile(r'^[a-zA-Z]+$')
        
        # Iterate through each row to validate the names.
        for index, row in df.iterrows():
            name = str(row[column_name])  # Ensure it's treated as a string.
            if not name or not pattern.match(name):
                df.at[index, new_column_name] = 1  # Marking corruption as 1 if criteria not met.
                
        return df
        
    @staticmethod
    def validate_birthdate(df, column_name):
        """ Function that specifies the date of birth column to be validated as per the constrains specified in the License class."""
        # Create a new column for corruption status.
        new_column_name = f"{column_name} Corruption"
        column_index = df.columns.get_loc(column_name)
        df.insert(column_index + 1, new_column_name, 0)  # Inserting next to the specified column.
       
        # Define constraints for date validation.
        today = datetime.today()
        earliest_dob = datetime(1950, 1, 1)
        latest_dob = today - timedelta(days=17 * 365)
        
        # Iterate through each row to validate the dates.
        for index, row in df.iterrows():
            try:
                dob = datetime.strptime(str(row[column_name]), '%d.%m.%Y')
                if not earliest_dob <= dob <= latest_dob:
                    df.at[index, new_column_name] = 1  # Marking corruption as 1 if criteria not met.
            except ValueError:
                df.at[index, new_column_name] = 1  # Marking corruption as 1 if date format is invalid.
                
        return df
    
    @staticmethod
    def validate_birthplace(df, column_name):
        """ Function that specifies the place of birth column in a database to be validated."""
        # Create a new column for corruption status.
        new_column_name = f"{column_name} Corruption"
        column_index = df.columns.get_loc(column_name)
        df.insert(column_index + 1, new_column_name, 0)  # Inserting next to the specified column.
        
        # Define a regular expression pattern to match letters and spaces.
        pattern = re.compile(r'^[a-zA-Z\s]+$')
        
        # Iterate through each row to validate the birthplaces.
        for index, row in df.iterrows():
            birthplace = str(row[column_name])  # Ensure it's treated as a string
            
            # Exclude empty strings and ensure the birthplace matches the pattern.
            if not birthplace or not pattern.match(birthplace):
                df.at[index, new_column_name] = 1  # Marking corruption as 1 if criteria not met.
                
        return df
    
    @staticmethod
    def validate_gender(df, column_name):
        """ Function that specifies the gender column to be validated."""
        # Create a new column for corruption status.
        new_column_name = f"{column_name} Corruption"
        column_index = df.columns.get_loc(column_name)
        df.insert(column_index + 1, new_column_name, 0)  # Inserting next to the specified column.

        # Define allowed genders.
        allowed_genders = {'Male', 'Female'}

        # Iterate through each row to validate the genders.
        for index, row in df.iterrows():
            gender = str(row[column_name])
            if gender not in allowed_genders:
                df.at[index, new_column_name] = 1  # Marking corruption as 1 if criteria not met.
          
        return df

    @staticmethod
    def validate_issuedate(df, column_name, dob_column):
        """ Function that specifies the date of issue column to be validated as per the constrains specified in the License class."""
        # Create a new column for corruption status.
        new_column_name = f"{column_name} Corruption"
        column_index = df.columns.get_loc(column_name)
        df.insert(column_index + 1, new_column_name, 0)  # Inserting next to the specified column.

        # Iterate through each row to validate the dates.
        for index, row in df.iterrows():
            date_of_birth = row[dob_column]
            try:
                # Specify constraints based on date of birth.
                dob = datetime.strptime(date_of_birth, '%d.%m.%Y')
                earliest_issue = dob + timedelta(days=17*365)
                latest_issue = datetime.today()

                # Check date format.
                date_of_issue = datetime.strptime(str(row[column_name]), '%d.%m.%Y')

                if not (earliest_issue <= date_of_issue <= latest_issue):
                    df.at[index, new_column_name] = 1  # Marking corruption as 1 if criteria not met.
            except (ValueError, KeyError):
                df.at[index, new_column_name] = 1  # Marking corruption as 1 if date format is invalid or missing.
                
        return df

    @staticmethod
    def validate_expirydate(df, column_name, issue_column):
        """ Function that specifies the date of expiry column to be validated as per the constrains specified in the License class."""
        # Create a new column for corruption status.
        new_column_name = f"{column_name} Corruption"
        column_index = df.columns.get_loc(column_name)
        df.insert(column_index + 1, new_column_name, 0)  # Inserting next to the specified column.

        # Iterate through each row to validate the dates
        for index, row in df.iterrows():
            date_of_issue = row[issue_column]
            try:
                date_of_issue = datetime.strptime(date_of_issue, '%d.%m.%Y')
                date_of_expiry = datetime.strptime(str(row[column_name]), '%d.%m.%Y')

                expected_expiry = date_of_issue + timedelta(days=10*365)
                if date_of_expiry != expected_expiry:
                    df.at[index, new_column_name] = 1  # Marking corruption as 1 if criteria not met.
            except (ValueError, KeyError):
                df.at[index, new_column_name] = 1  # Marking corruption as 1 if date format is invalid or missing.
                
        return df


    @staticmethod
    def validate_authority(df, column_name):
        """ Function that specifies the issuing authority column to be validated to ensure it is "DA1"."""
        # Create a new column for corruption status.
        new_column_name = f"{column_name} Corruption"
        column_index = df.columns.get_loc(column_name)
        df.insert(column_index + 1, new_column_name, 0)  # Inserting next to the specified column.

        # Iterate through each row to validate the issuing authority
        for index, row in df.iterrows():
            issuing_authority = str(row[column_name])  # Ensure it's treated as a string.
            if issuing_authority != "DA1":
                df.at[index, new_column_name] = 1  # Marking corruption as 1 if criteria not met.
                
        return df
    
    @staticmethod
    def validate_drivernum(df, column_name, first_name, last_name, gender, date_of_birth):
        """ Function that specifies the license number column to be validated as per the constrains specified in the License class."""
        def generate_expected_driver_num(first_name, last_name, gender, date_of_birth):
            """ Function that generates a driver number using the same formulae as the function in the class License."""
            l_name = last_name.upper().replace("MAC", "MC").ljust(5, '9')[:5]
            decade_digit = date_of_birth[8]
            month_digit = str(int(date_of_birth[3:5])).zfill(2)
            if gender.lower() == 'female':
                month_digit = str(int(month_digit) + 50).zfill(2)
            day_digit = date_of_birth[:2].zfill(2)
            year_digit = date_of_birth[9]
            first_initial = first_name[0].upper() + '99'
            random_letters = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=2))

            return f'{l_name}{decade_digit}{month_digit}{day_digit}{year_digit}{first_initial}{random_letters}'
        
        # Create a new column for corruption status.
        new_column_name = f"{column_name} Corruption"
        column_index = df.columns.get_loc(column_name)
        df.insert(column_index + 1, new_column_name, 0)  # Inserting next to the specified column.

        # Define a pattern to ensure there are no special characters or lower case letters. 
        letters_pattern = re.compile(r'^[A-Z]+$')

        # Iterate through each row to validate the driver number by comparing it to what the generated driver number should be.
        for index, row in df.iterrows():
            expected_driver_num = generate_expected_driver_num(
                row[first_name], row[last_name], row[gender], row[date_of_birth]
            )
            driver_num = str(row[column_name])  # Ensure it's treated as a string.
            
            if driver_num[:14] != expected_driver_num[:14] or not letters_pattern.match(driver_num[14:]):
                df.at[index, new_column_name] = 1  # Marking corruption as 1 if criteria not met.
                
        return df

    
    @staticmethod
    def validate_address(df, column_name):
        """ Function that specifies the address column to be validated as per the constrains specified in the License class."""   
        # Create a new column for corruption status.
        new_column_name = f"{column_name} Corruption"
        column_index = df.columns.get_loc(column_name)
        df.insert(column_index + 1, new_column_name, 0)  # Inserting next to the specified column.

        # Define regex patterns for address components
        street_pattern = re.compile(r'^\d{1,3}\s[A-Za-z]+\s[A-Za-z]+$')
        city_pattern = re.compile(r'^[A-Za-z]+(?:\s[A-Za-z]+)?$')
        postcode_pattern = re.compile(r'^[A-Za-z]{1,2}\d[A-Za-z0-9]?\s\d[A-Za-z]{2}$')
        
        # Iterate through each row to validate the address components.
        for index, row in df.iterrows():
            address = str(row[column_name])  # Ensure it's treated as a string.
            address_components = address.split(', ') if address else []

            # Check if all address components are present.
            if len(address_components) != 3:
                df.at[index, new_column_name] = 1  # Marking corruption as 1 if any component is missing
                continue
            
            # Validate street address, city, and postcode formats.
            street_address, city, postcode = address_components
            
            if not street_pattern.match(street_address) or not city_pattern.match(city) or not postcode_pattern.match(postcode):
                df.at[index, new_column_name] = 1  # Marking corruption as 1 if any component format is invalid. 
                
        return df
        
    @staticmethod
    def validate(df):
        """ Function that calls all the previous validation methods together for all columns in the license dataframe."""
        # Call the appropriate corruption function for each column.
        df = Validate.validate_name(df, 'First Name')
        df = Validate.validate_name(df, 'Last Name')
        df = Validate.validate_birthdate(df, 'Date of Birth')
        df = Validate.validate_birthplace(df, 'Place of Birth')
        df = Validate.validate_gender(df, 'Gender')
        df = Validate.validate_issuedate(df, 'Date of Issue', 'Date of Birth')
        df = Validate.validate_expirydate(df, 'Date of Expiry', 'Date of Issue')
        df = Validate.validate_authority(df, 'Issuing Authority')
        df = Validate.validate_drivernum(df, 'License Number', 'First Name', 'Last Name', 'Gender',  'Date of Birth')
        df = Validate.validate_address(df, "Address")
        return df
    
