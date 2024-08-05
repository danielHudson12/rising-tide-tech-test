import pytest
from unittest import mock
from unittest.mock import patch
from datetime import datetime

from uk_number_plate_generator import UKNumberPlateGenerator

@pytest.mark.parametrize("datetime, expected_year_code", [
    (datetime(year = 2010, month = 4, day = 3), "10"),
    (datetime(year = 2001, month = 9, day = 25), "51"),
    (datetime(year = 2007, month = 3, day = 1), "07")
])
def test_generate_age_identifier(datetime, expected_year_code):
    assert UKNumberPlateGenerator('plates.csv').generate_age_identifier(datetime) == expected_year_code
   
   
@pytest.mark.parametrize("number_plate_prefix, start_index, existing_plates, return_string", [
    ("YA07", 0, set(), "AAA"),
    ("YA07", 0, {"YA07 AAA", "YA07 AAB"}, "AAC"),
    ("AB57", 12166, set(), "YYY"),
    ("AB57", 0, {"AB57 YYY"}, "AAA")
])
def test_generate_available_random_string(number_plate_prefix, start_index, existing_plates, return_string):
    with patch('random.randint', return_value=start_index):
        generator = UKNumberPlateGenerator('test.csv')
        generator.existing_generated_plates = existing_plates
        assert generator.generate_available_random_string(number_plate_prefix) == return_string
        
        
def test_generate_available_random_string_raises_error():
    with pytest.raises(ValueError) as err_info:
        generator = UKNumberPlateGenerator('test.csv')
        generator.existing_generated_plates = set(["DH14 "+combo for combo in UKNumberPlateGenerator.all_possible_random_strings])
        generator.generate_available_random_string("DH14")
        
    assert str(err_info.value) == 'No more unique strings available'
    

@pytest.mark.parametrize("dvla_memory_tag, date_created_str, random_start_index, existing_plates, expected_generated_plate, expected_end_plate_set", [
    ("YR", "03/11/2017", 5, set(), "YR67 AAF", {"YR67 AAF"}),
    ("ER", "08/01/2009", 0, {"ER59 AAA", "ER59 AAB"}, "ER59 AAC", {"ER59 AAA", "ER59 AAB", "ER59 AAC"}),
    ("GH", "06/07/2021", 645, set(), "GH21 BFB", {"GH21 BFB"}),
])    
def test_generate_numberplate(dvla_memory_tag, date_created_str, random_start_index, existing_plates, expected_generated_plate, expected_end_plate_set):
    with patch('random.randint', return_value=random_start_index):
        generator = UKNumberPlateGenerator('test.csv')
        generator.existing_generated_plates = existing_plates.copy()
        assert generator.generate_numberplate(dvla_memory_tag, date_created_str) == expected_generated_plate
        assert generator.existing_generated_plates == expected_end_plate_set
        
        
@pytest.mark.parametrize("dvla_memory_tag, date_created_str, expected_error_message", [
    ("YQ", "03/11/2017", 'I, Q, Z not allowed in UK number plates'),
    ("IK", "03/11/2017", 'I, Q, Z not allowed in UK number plates'),
    ("ZT", "03/11/2017", 'I, Q, Z not allowed in UK number plates'),
    ("A", "03/11/2017", 'DVLA memory tag must be 2 characters in length'),
    ("ABC", "03/11/2017", 'DVLA memory tag must be 2 characters in length'),
    ("AB", "00/11/2017", "time data '00/11/2017' does not match format '%d/%m/%Y'"),
    ("AB", "03-11-2017", "time data '03-11-2017' does not match format '%d/%m/%Y'"),
])    
def test_generate_numberplate_raises_error(dvla_memory_tag, date_created_str, expected_error_message):
    with pytest.raises(ValueError) as err_info:
        generator = UKNumberPlateGenerator('test.csv')
        generator.generate_numberplate(dvla_memory_tag, date_created_str)
        
    assert str(err_info.value) == expected_error_message


def test_load_from_csv():
    mock_data = '\n'.join(["YP10 UNK", "YP10 SHU", "YP10 EHW"])
    m = mock.mock_open(read_data=mock_data)
    with mock.patch('builtins.open', m):
        generator = UKNumberPlateGenerator('test.csv')
        data = generator.load_from_csv()
        assert len(data) == 3
        assert data == {"YP10 UNK", "YP10 SHU", "YP10 EHW"}
        
        
def test_save_to_csv():
    mock_file = mock.mock_open(read_data=None)
    with mock.patch('builtins.open', mock_file):
        generator = UKNumberPlateGenerator('test.csv')
        generator.existing_generated_plates = {"YP10 UNK", "YP10 SHU", "YP10 EHW"}
        generator.save_to_csv()
        mock_file.assert_called_once_with('test.csv', mode='w', newline='', encoding='utf-8')
        
        handle = mock_file()
        handle.write.assert_any_call('YP10 UNK\r\n')
        handle.write.assert_any_call('YP10 SHU\r\n')
        handle.write.assert_any_call('YP10 EHW\r\n')
        

def test_init():
    mock_data = '\n'.join(["YP10 UNK", "YP10 SHU", "YP10 EHW"])
    m = mock.mock_open(read_data=mock_data)
    with mock.patch('builtins.open', m):
        generator = UKNumberPlateGenerator('test.csv')
        assert generator.existing_generated_plates == set()
        
        with mock.patch('os.path.isfile', return_value=True):
            generator = UKNumberPlateGenerator('test.csv')
            assert generator.existing_generated_plates == {"YP10 UNK", "YP10 SHU", "YP10 EHW"}
            
    with pytest.raises(ValueError) as err_info:
        generator = UKNumberPlateGenerator('testcsv')
        assert str(err_info.value) == "File must be a .csv file"