import os
from bs4 import BeautifulSoup
from fastapi import Depends
from sqlalchemy.orm import Session 
from typing import Optional
from typing import Optional
import requests, csv
import settings
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, date
from models import transaction as model # ORM 

COLUMN_HEADERS = ['X', 'Filling Date', 'Trade Date', 'Ticker', 'Company Name', 'Insider Name','Title', 'Trade Type', 'Price', 'Qty', 'Owned', 'Delta_owned', 'Value']

def parse_float(value):
  """ Remove '$' and ',' from price and convert to float """
  if value:
      return float(value.replace("$", "").replace(",", ""))
  return None

def parse_int(value):
    """ Remove ',' and convert to int """
    if value:
        return int(value.replace(",", ""))
    return None

def parse_timestamp(value):
    """ Convert string to datetime object """
    if value:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")  # Correct format
    return None

def parse_date(value):
    """ Convert string to date object """
    if value:
        return date.fromisoformat(value)  # Format: 'YYYY-MM-DD'
    return None

def clear_data(db: Session): 
  """
  Deletes all records from the Transaction table.
  Parameters: db (Session) which is the database session.
  Returns: None
  Raises: Exception for any issues
  """
  try:
    db.query(model.Transaction).delete()  # Delete all records
    db.commit()  # Commit the changes
    print("All transaction records have been deleted.")
  except Exception as e:
    db.rollback()  # Rollback in case of an error
    print(f"Error clearing transaction data: {str(e)}")
    raise

def archive_files():
  try:
    # Create archive folder name with today's date
    today = datetime.now()
    archive_dir = os.path.join(settings.OUTPUT_DIR,f"archive_openinsider_{today:%Y_%m_%d}")
    os.makedirs(os.path.dirname(archive_dir), exist_ok=True)
    # List files to archive
    files = os.listdir(settings.OUTPUT_DIR)
    files = [f for f in files if f.startswith("openinsider_") and f.endswith(".csv")]
    for file in files:
      src_path = os.path.join(settings.OUTPUT_DIR, file)
      dst_path = os.path.join(archive_dir, file)
      os.rename(src_path, dst_path)  # Move file to archive directory
  except Exception as e:
    print(f"Error archiving files: {str(e)}")
    raise 

def bootstrap_data(db: Session, start_year: int, daily_sync):
  """
  Initializes the data extraction process.
  Parameters: db (Session) which is the database session.
  Returns: None
  """
  try: 
    if extract_data(start_year, daily_sync): # Extract data from the source and write them to CSV files, if it returns True, then we proceed to import the data into the database, otherwise we skip the import step since there is no data extracted
      print("Importing data into the database...")
      import_data(db, daily_sync) # Import data into the database
    print("Bootstrap completed successfully!")
  except Exception as e:
    print(f"Bootstrap failed with the error: {e}.")
    raise

def extract_data(start_year: int, daily_sync: bool = False):
  """
  Extract the data from openinsider.com. end date is computed to be always the previous day.
  Parameters: 
  start_year (int): The year to start the data extraction from. It should be a valid year (e.g., 2013).
  daily_sync (bool): A flag indicating whether to perform a daily sync (True) or a full bootstrap (False). Default is False.
  Returns: True if the extraction was successful, False otherwise. 
  Raises:
    ValueError: If there is an issue with parsing the data
    IOError: If there is an issue with writing to the file.
  """
  current_year = datetime.now().year
  current_month = datetime.now().month
  futures = []
  try:
    if start_year > current_year:
      raise ValueError(f"Invalid start_year {start_year}. It cannot be in the future.")
    # we use ThreadPoolExecutor to scrape data concurrently for different date ranges (months), which can significantly speed up the extraction process, especially when dealing with a large date range. Each thread will handle the scraping for a specific month, allowing us to efficiently utilize system resources and reduce the overall time taken for data extraction. By default, the number of workers is set to 3, but it can be adjusted based on the system's capabilities and the expected load. The as_completed function is used to process the results as they become available, allowing for better error handling and efficient resource management.
    with ThreadPoolExecutor(max_workers=int(settings.MAX_WORKERS)) as executor:
      for year in range(start_year, current_year + 1):
        start_month = 1 if year != 2013 else 3 # this is hardcoded to start from March 2013, to accomodate the data available on openinsider.com
        end_month = current_month if year == current_year else 12 # end_month is current month if it is the current year, otherwise it is December
        if daily_sync and year == current_year: # for daily sync only
          start_month = current_month
        for month in range(start_month, end_month + 1): # for each month in the year, we will scrape the data for that month, and we will do this concurrently for different months using ThreadPoolExecutor
          if daily_sync and year == current_year and month == current_month: # for daily sync only
            yesterday = datetime.now() - timedelta(days=1)  # for daily sync, we only scrape data for yesterday
            start_date = end_date = datetime(yesterday.year, yesterday.month, yesterday.day).strftime('%m/%d/%Y') # formatting as MM/DD/YYYY
          else:
            # for bootstrapping by month
            start_date = datetime(year, month, 1).strftime('%m/%d/%Y') # 1st day of the month of the year formatted as MM/DD/YYYY
            end_date = datetime.now() - timedelta(days=1) if month == end_month else (datetime(year, month, 1) + timedelta(days=32)).replace(day=1) - timedelta(days=1) # if current month is the end_month, then the end_date is current_day - 1 (previous day), otherwise it is the last day of the month, which is calculated by getting the first day of the next month and subtracting one day from it
            end_date = end_date.strftime('%m/%d/%Y') # formatting as MM/DD/YYYY

          # after getting start_date and end_date, scrape the data and pass it to the thread, which means every thread will scrape data for a specific month and write to a separate CSV file for that month
          futures.append(executor.submit(scrape_data_by_date_range, start_date, end_date)) 

          # Process futures as they complete
          for future in as_completed(futures):
            try:
              result = future.result()
              if result is None:
                print(f"No data found for the date range {start_date} to {end_date}.")
                return False
            except Exception as e:
                print(f"Error occurred while processing data: {e}")
  except Exception as e:
    print(f"Unexpected error in extract_data: {str(e)}")
    raise
  return True  # return True if the extraction was successful

def scrape_data_by_date_range(start_date, end_date):
  """
  Scrapes insider trading data from openinsider.com for a given date range. This is very custom. 
  Parameters:
  start_date (str): The start date of the range in MM/DD/YYYY format.
  end_date (str): The end date of the range in MM/DD/YYYY format.
  Returns:
  list: A list of cleaned rows containing insider trading data.
  Raises:
  """
  # url = f'http://openinsider.com/screener?fd=-{fd}&fdr={start_date}+-+{end_date}&td={td}&cnt=5000&page=1' # sample
  url = f"{settings.BASE_URL}?fd=-{settings.DEFAULT_FILLING_DAYS}&fdr={start_date}+-+{end_date}&td={settings.TRADE_DATE_FILTER}&cnt={settings.MAX_ROWS}&page=1"
  print(f"Scraping data from {url}")
  res = requests.get(url)
  soup = BeautifulSoup(res.text, 'html.parser')
  try:
    rows = soup.find('table', {'class': 'tinytable'}).find('tbody').find_all('tr')
  except:
    print(f"Error: Failed to fetch data from {url}") 
    return
  cleaned_rows = []
  for row in rows:
    cols = row.find_all('td')
    if not cols:
      continue
    cleaned_row = []
    for idx, col_header in enumerate(COLUMN_HEADERS):
      ele = cols[idx].find('a').text.strip() if cols[idx].find('a') else cols[idx].text.strip()
      cleaned_row.insert(idx, ele)
    cleaned_rows.append(cleaned_row)
  if cleaned_rows:
    year_obj = datetime.strptime(start_date, '%m/%d/%Y').year
    month_obj = datetime.strptime(start_date, '%m/%d/%Y').month
    day_obj = datetime.strptime(start_date, '%m/%d/%Y').day
    filename = f"openinsider_{year_obj}_{month_obj:02d}_{day_obj:02d}.csv" 
    write_to_csv(cleaned_rows, os.path.join(settings.OUTPUT_DIR, filename),COLUMN_HEADERS) # write to CSV file
  return cleaned_rows

def write_to_csv(data, filename, headers):
  try: 
    with open(filename, 'w', newline='') as f:
      print("Writing to CSV file...")
      writer = csv.writer(f)
      writer.writerow(headers)
      writer.writerows(data)
      print(f"CSV file '{filename}' saved successfully!")
  except IOError as e:
    raise IOError(f"Error writing to CSV file: {str(e)}")

def import_data(db: Session, daily_sync: bool = False):
  """
  Imports necessary data into the system.
  Parameters: None
  Returns:
  bool: True if the import was successful, False otherwise.
  Raises:
    ValueError: If the import data format is incorrect.
    IOError: If there is an issue with reading from the source.
  """
  if not daily_sync:
    try:
      files = os.listdir(settings.OUTPUT_DIR)
    except FileNotFoundError:
      print(f"Directory '{settings.OUTPUT_DIR}' not found.")
      return []
    # Filter files based on the naming convention
    files = [f for f in files if f.startswith("openinsider_") and f.endswith(".csv")]
  else: # for daily sync, we only import the latest file
    yesterday = datetime.now() - timedelta(days=1)
    filename = f"openinsider_{yesterday.year}_{yesterday.month:02d}_{yesterday.day:02d}.csv"
    files = [filename] # set the filest to be imported to be the file for yesterday, which is generated by the daily sync data extraction

  for file in files: # todo: should we be ordering them by date to make sure the data is imported in the correct order?
    file_name = os.path.join(settings.OUTPUT_DIR, file)
    with ThreadPoolExecutor(max_workers=int(settings.MAX_WORKERS)) as executor:
      future = executor.submit(import_file_db, db, file_name)
      try:
        result = future.result()  # Wait for the thread to complete
        if result:
          print(f"Successfully imported data from {file_name}")
      except Exception as e:
        print(f"Error importing data from {file_name}: {str(e)}")
    
def import_file_db(db: Session, file_name: str):
  try:
    with open(file_name, newline="", encoding="utf-8") as f:
      reader = csv.DictReader(f)  # Reads CSV with column names
      transactions = []
      for row in reader:
          transactions.append(model.Transaction(
              x=row["X"],
              filing_date=(parse_timestamp(row["Filling Date"])),
              trade_date=(parse_date(row["Trade Date"])),
              ticker=row["Ticker"],
              company_name=row["Company Name"],
              insider_name=row["Insider Name"],
              insider_title=row["Title"],
              trade_type=row["Trade Type"],
              price=float(parse_float(row["Price"])) if row["Price"] else None,
              qty=int(parse_int(row["Qty"])) if row["Qty"] else None,
              owned=int(parse_int(row["Owned"])) if row["Owned"] else None,
              delta_owned=row["Delta_owned"],
              value=float(parse_float(row["Value"])) if row["Value"] else None,
          ))
    db.bulk_save_objects(transactions)
    db.commit()
    return True
  except ValueError as ve:
      # Handle invalid data format
      raise ValueError(f"Invalid data format: {str(ve)}")
  except IOError as ioe:
      # Handle I/O errors
      raise IOError(f"Error reading the data source: {str(ioe)}")

def force_refresh(db: Session, start_year: int):
  """
  Clears any existing data and proceeds with bootstrapping the system.
  This function wipes any existing data and initiates the bootstrapping 
  process to initialize the system.
  Parameters: None
  Returns: None
  Raises: Exception If the system fails during the refresh process.
  """
  try:
    clear_data(db)                              # Wipe data clean from the database
    archive_files()                             # Archive the files in the output directory after the data is cleared from the database
    bootstrap_data(db, start_year, False)       # Bootstrapping the data       
  except Exception as e:                        # Handle exceptions that might occur during the refresh
    print(f"Failed to force refresh: {str(e)}")
    raise Exception(f"Failed to force refresh: {str(e)}")

def get_ticker(db: Session, ticker_id: str):
  return db.query(model.Transaction).filter(model.Transaction.ticker==ticker_id).first()

def retrieve_by_ticker(db: Session, ticker_id:str):
  # check if ticker exists in the database 
  existing_ticker = get_ticker(db, ticker_id)
  if not existing_ticker: # not in the database
    return None # not found then, return None
  return existing_ticker

def retrieve_transactions(db: Session, ticker_id: str, from_date: Optional[date] = None, to_date: Optional[date] = None, trade_type = None, skip: int = 0, limit: int = 100):
  # If from_date is not provided, set it to the default: earliest date 
  if not from_date:
    from_date = datetime.today() # todo: to change to the earliest date

  # If to_date is not provided, set it to today's date
  if not to_date:
    to_date = datetime.today()

  # If trade_type is not provided, set it to None
  if not trade_type:
    trade_type = None
  else:
    trade_type = trade_type.value

  if ticker_id != "" and trade_type == None: # if ticker_id is provided and trade_type is not provided
    return db.query(model.Transaction)\
              .filter(model.Transaction.ticker == ticker_id)\
              .filter(model.Transaction.trade_date >= from_date)\
              .filter(model.Transaction.trade_date <= to_date)\
              .order_by(model.Transaction.trade_date.desc())\
              .offset(skip)\
              .limit(limit)\
              .all()
  elif ticker_id != "" and trade_type != None: # if ticker_id and trade_type are provided
    return db.query(model.Transaction)\
              .filter(model.Transaction.ticker == ticker_id)\
              .filter(model.Transaction.trade_date >= from_date)\
              .filter(model.Transaction.trade_date <= to_date)\
              .filter(model.Transaction.trade_type == trade_type)\
              .order_by(model.Transaction.trade_date.desc())\
              .offset(skip)\
              .limit(limit)\
              .all()
  elif ticker_id == "" and trade_type == None: # trade dates are provided and trade_type is not provided
    return db.query(model.Transaction)\
              .filter(model.Transaction.trade_date >= from_date)\
              .filter(model.Transaction.trade_date <= to_date)\
              .order_by(model.Transaction.trade_date.desc())\
              .offset(skip)\
              .limit(limit)\
              .all()
  else: # trade dates and trade_type are provided
    return db.query(model.Transaction)\
              .filter(model.Transaction.trade_date >= from_date)\
              .filter(model.Transaction.trade_date <= to_date)\
              .filter(model.Transaction.trade_type == trade_type)\
              .order_by(model.Transaction.trade_date.desc())\
              .offset(skip)\
              .limit(limit)\
              .all()