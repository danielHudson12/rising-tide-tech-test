from datetime import datetime
from itertools import product
from typing import Set
import string
import random
import csv
import os

class UKNumberPlateGenerator:
    """A UK number plate generator
    
    generates unique, non repeating number plates from dvla memory tags and manufacture dates. results loaded from csv file, must be saved explicitly
    """
    
    # define the suitable chars to use, I, Q, Z not allowed
    allowed_plate_chars = [char for char in string.ascii_uppercase if char not in 'IQZ']
    all_possible_random_strings = [''.join(combo) for combo in product(allowed_plate_chars, repeat = 3)]
    
    def __init__(self, save_file_path: str):
        """Inits UKNumberPlateGenerator and loads any existing data from the save_file_path

        Args:
            save_file_path (str): the location to load (if exists) and save the results to, must be a .csv file

        Raises:
            ValueError: if the file path is not .csv
        """
        self.save_file_path = save_file_path
        
        if(save_file_path[-4:] != ".csv"):
            raise ValueError("File must be a .csv file")
        
        try:
            # check file exists, or else create it
            if(os.path.isfile(self.save_file_path)):
                self.existing_generated_plates = self.load_from_csv()
            else:
                self.existing_generated_plates = set()
        except IOError as err:
            print("Failed to load existing generated plates due to {err}")
    
    
    def load_from_csv(self) -> Set[str]:
        """load the existing generated plates from a csv file

        Returns:
            Set[str]: the existing generated plates
        """
        csv_rows = []
        with open(self.save_file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if row:  # ensure the row is not empty
                    csv_rows.append(row[0])
        print(f"successfully loaded {len(csv_rows)} rows from '{self.save_file_path}'")
        return set(csv_rows) # make sure there are no duplicates

    
    def save_to_csv(self) -> None:
        """save the generated and loaded results to the csv file 
        """
        with open(self.save_file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for string in self.existing_generated_plates:
                writer.writerow([string])
        print(f"Successfully saved {len(self.existing_generated_plates)} existing generated plates to '{self.save_file_path}'")
        
    
    def generate_numberplate(self, dvla_memory_tag: str, date_created_str: str) -> str:
        """generate a valid available number plate from the memory tag and date supplied

        Args:
            dvla_memory_tag (str): 2 character memory tag not including I, Q, Z
            date_created_str (str): date car was manufactured in dd/mm/YYYY format

        Raises:
            ValueError: if I, Q, Z is included in dvla_memory_tag
            ValueError: if dvla_memory_tag is not 2 chars long
            ValueError: if no available random strings left

        Returns:
            generated_number_plate (str): a valid uk number plate
        """
        # created date string must be in dd/mm/YYYY format
        date_created = datetime.strptime(date_created_str, "%d/%m/%Y")
        
        # I, Q, Z not allowed in UK number plates
        dvla_memory_tag = dvla_memory_tag.upper()
        if (any(invalid_char in dvla_memory_tag for invalid_char in ("I", "Q", "Z"))):
            raise ValueError("I, Q, Z not allowed in UK number plates")
        
        # dvla memory tag must be of length 2
        if (len(dvla_memory_tag) != 2):
            raise ValueError("DVLA memory tag must be 2 characters in length")
        
        age_identifier = self.generate_age_identifier(date_created)
        number_plate_prefix = f"{dvla_memory_tag}{age_identifier}"
        random_string = self.generate_available_random_string(number_plate_prefix)
        generated_number_plate = f"{number_plate_prefix} {random_string}"
        
        # save in memory but only in file if explicitly called
        self.existing_generated_plates.add(generated_number_plate)
        
        return generated_number_plate
    
    
    def generate_age_identifier(self, date_created: datetime) -> str:
        """Generate 2 digit year code from car created date

        Args:
            date_created (datetime): date the car was manufactured

        Returns:
            age_identifier (str): 2 digit age identifier
        """
        year = date_created.year
        month = date_created.month
        
        # cars manufactured from march to august use their year, otherwise, add 50
        if 3 <= month <= 8:
            return str(year)[-2:]
        return str(year + 50)[-2:]
    
    
    def generate_available_random_string(self, number_plate_prefix: str) -> str:
        """Get an available number plate random string

        Args:
            number_plate_prefix (str): the prefix of the number plate

        Raises:
            ValueError: if no available random strings left

        Returns:
            random_string (str): a random string of length 3
        """
        # Get a random starting index
        start_index = random.randint(0, len(self.all_possible_random_strings) - 1)
        
        # Loop through the list starting from the random index, return the first available string
        for i in range(len(self.all_possible_random_strings)):
            index = (start_index + i) % len(self.all_possible_random_strings) # make sure to loop back around
            random_string = self.all_possible_random_strings[index]
            if(f"{number_plate_prefix} {random_string}" not in self.existing_generated_plates):
                return random_string
            
        raise ValueError("No more unique strings available")


if __name__ == "__main__":
    generator = UKNumberPlateGenerator('plates.csv')

    plate = generator.generate_numberplate("YP", "01/04/2010")
    plate2 = generator.generate_numberplate("YP", "03/04/2010")
    plate3 = generator.generate_numberplate("YP", "03/04/2010")
    plate4 = generator.generate_numberplate("YP", "03/04/2010")
    print(plate)
    print(plate2)
    print(plate3)

    generator.save_to_csv()

