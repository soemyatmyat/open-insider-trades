from bs4 import BeautifulSoup
from . import schemas, models # import pydantic and db model 
from fastapi import Depends 
from sqlalchemy.orm import Session 
import requests, csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta


def clear_data():
    # Wipe any existing data from the database
    pass 

def bootstrap_data():
    # Define parameters and pass these values to extract_data
    pass 

def extract_data():
    """
    Extract the data from openinsider.com
    Parameters: TBD
    Returns: 
      bool: True if the extraction was successful, False otherwise.
    Raises:
      ValueError: 
      IOError: If there is an issue with writing to the file.
    """
    current_year = datetime.now().year
    current_month = datetime.now().month
    current_day = datetime.now().day
    data = []
    futures = []
    max_workers = 1
    start_year = 2025

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
      for year in range(start_year, current_year + 1):
        start_month = 1 if year != 2013 else 3
        end_month = current_month if year == current_year else 12
        for month in range(start_month, end_month + 1):
          start_date = datetime(year, month, 1).strftime('%m/%d/%Y') # formatting as MM/DD/YYYY
          # reset the date to the first day of the next month and subtract one day to get the last day of the original month
          # end_date = (datetime(year, month, 1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
          # change the end date
          end_date = datetime(year, month, current_day - 1) if month == end_month else (datetime(year, month, 1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
          end_date = end_date.strftime('%m/%d/%Y') # formatting as MM/DD/YYYY
          futures.append(executor.submit(scarp_data_by_date_range, 1, start_date, end_date, 0))

        # Process futures as they complete
        for future in as_completed(futures):
          if future.result() is not None:
            data.extend(future.result())

        # ===== todo: to redefine this ===== 
        # output_file = os.path.join('out.csv')
        # cols_headers=['X','Filling Date','Trade Date','Ticker','Company Name','Insider Name','Title','Trade Type','Price','Qty','Owned','Delta_owned','Value']

        # with open(output_file, 'w', newline='') as f:
        #     print("Writing to CSV...")
        #     writer = csv.writer(f)
        #     writer.writerow(cols_headers)
        #     writer.writerows(data)

        # print("CSV file saved successfully!")
    pass

def scarp_data_by_date_range(fd, start_date, end_date, td):
  cols_headers=['X','Filling Date','Trade Date','Ticker','Company Name','Insider Name','Title','Trade Type','Price','Qty','Owned','Delta_owned','Value'] # this is hard-coded value and should be moved to the config file
  fd = 1 # custom filling date and should be moved to the config file
  td = 0 # trade date = all dates 
  url = f'http://openinsider.com/screener?fd=-{fd}&fdr={start_date}+-+{end_date}&td={td}&cnt=5000&page=1' # this should be moved to the config file
  res = requests.get(url)
  soup = BeautifulSoup(res.text, 'html.parser')
  try:
    rows = soup.find('table', {'class': 'tinytable'}).find('tbody').findAll('tr')
  except:
    print(f"Error ==> This URL was not successful: {url}") # we don't do logging, instead the pod should manage the print errors
    return
  cleaned_rows = []
  for row in rows:
    cols = row.findAll('td')
    if not cols:
      continue
    cleaned_row = []
    for idx, col_header in enumerate(cols_headers):
      ele = cols[idx].find('a').text.strip() if cols[idx].find('a') else cols[idx].text.strip()
      cleaned_row.insert(idx,ele)
    cleaned_rows.append(cleaned_row)
  return cleaned_rows

def import_data():
    """
    Imports necessary data into the system.
    Parameters: None
    Returns:
    bool: True if the import was successful, False otherwise.
    Raises:
    ValueError: If the import data format is incorrect.
    IOError: If there is an issue with reading from the source.
    """
    try:
        # Example of importing data
        data = load_data_from_source()
        process_imported_data(data)
        
        return True
    except ValueError as ve:
        # Handle invalid data format
        raise ValueError(f"Invalid data format: {str(ve)}")
    except IOError as ioe:
        # Handle I/O errors
        raise IOError(f"Error reading the data source: {str(ioe)}")

def force_refresh():
    """
    Clears any existing data and proceeds with bootstrapping the system.
    This function wipes any existing data and initiates the bootstrapping 
    process to initialize the system.
    Parameters: None
    Returns: None
    Raises:
    Exception: If the system fails during the refresh process.
    """
    try:
        # Wipe data clean from the database
        clear_data()

        # Bootstrapping the data 
        bootstrap_data()
        
    except Exception as e:
        # Handle exceptions that might occur during the refresh
        raise Exception(f"Failed to force refresh: {str(e)}")





