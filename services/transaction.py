from bs4 import BeautifulSoup
from fastapi import Depends
from sqlalchemy.orm import Session 
from typing import Optional
from typing import Optional
import requests, csv
import settings
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, date
from schemas import transaction as schemas # pydantic 
from models import transaction as models # ORM 

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
        db.query(models.Transaction).delete()  # Delete all records
        db.commit()  # Commit the changes
        print("All transaction records have been deleted.")
    except Exception as e:
        db.rollback()  # Rollback in case of an error
        print(f"Error clearing transaction data: {str(e)}")
        raise

def bootstrap_data(db: Session, start_year: int):
  """
  Initializes the data extraction process.
  Parameters: db (Session) which is the database session.
  Returns: None
  """
  try: 
    if extract_data(start_year):
      import_data(db)
    print("Bootstrap completed successfully!")
  except Exception as e:
    print(f"Bootstrap failed with the error: {e}.")
    raise

def extract_data(start_year: int):
  """
  Extract the data from openinsider.com
  Parameters: None
  Returns: True if the extraction was successful, False otherwise. 
  Raises:
    ValueError: If there is an issue with parsing the data
    IOError: If there is an issue with writing to the file.
  """
  current_year = datetime.now().year
  current_month = datetime.now().month
  current_day = datetime.now().day  
  data = []
  futures = []
  try:
    if start_year > current_year:
      raise ValueError(f"Invalid start_year {start_year}. It cannot be in the future.")
    with ThreadPoolExecutor(max_workers=int(settings.MAX_WORKERS)) as executor:
      for year in range(start_year, current_year + 1):
        start_month = 1 if year != 2013 else 3
        end_month = current_month if year == current_year else 12
        for month in range(start_month, end_month + 1):
          start_date = datetime(year, month, 1).strftime('%m/%d/%Y') # formatting as MM/DD/YYYY
          end_date = datetime(year, month, current_day - 1) if month == end_month else (datetime(year, month, 1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
          end_date = end_date.strftime('%m/%d/%Y') # formatting as MM/DD/YYYY
          futures.append(executor.submit(scrape_data_by_date_range, start_date, end_date))

          # Process futures as they complete
          for future in as_completed(futures):
            try:
              result = future.result()
              if result is not None:
                data.extend(result)
            except Exception as e:
                print(f"Error occurred while processing data: {e}")

        # Write to CSV
        try: 
          with open(settings.OUTPUT_FILE, 'w', newline='') as f:
            print("Writing to CSV file...")
            writer = csv.writer(f)
            writer.writerow(COLUMN_HEADERS)
            writer.writerows(data)
          print(f"CSV file '{settings.OUTPUT_FILE}' saved successfully!")
        except IOError as e:
          raise IOError(f"Error writing to CSV file: {str(e)}")
  except Exception as e:
    print(f"Unexpected error in extract_data: {str(e)}")
    return False
  return True 

def scrape_data_by_date_range(start_date, end_date):
  # url = f'http://openinsider.com/screener?fd=-{fd}&fdr={start_date}+-+{end_date}&td={td}&cnt=5000&page=1' # this should be moved to the config file
  url = f"{settings.BASE_URL}?fd=-{settings.DEFAULT_FILLING_DAYS}&fdr={start_date}+-+{end_date}&td={settings.TRADE_DATE_FILTER}&cnt={settings.MAX_ROWS}&page=1"
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
      cleaned_row.insert(idx,ele)
    cleaned_rows.append(cleaned_row)
  return cleaned_rows

def import_data(db: Session):
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
    with open(settings.OUTPUT_FILE, newline="", encoding="utf-8") as file:
      reader = csv.DictReader(file)  # Reads CSV with column names
      transactions = []
      for row in reader:
          transactions.append(models.Transaction(
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
    clear_data(db)                      # Wipe data clean from the database
    bootstrap_data(db, start_year)      # Bootstrapping the data       
  except Exception as e:                # Handle exceptions that might occur during the refresh
    print(f"Failed to force refresh: {str(e)}")
    raise Exception(f"Failed to force refresh: {str(e)}")

def get_ticker(db: Session, ticker_id: str):
  return db.query(models.Transaction).filter(models.Transaction.ticker==ticker_id).first()

def retrieve_by_ticker(db: Session, ticker_id:str):
  # check if ticker exists in the database 
  existing_ticker = get_ticker(db, ticker_id)
  if not existing_ticker: # not in the database
    return None # not found then, return None
  return existing_ticker

def retrieve_transactions(db: Session, ticker_id: str, from_date: Optional[datetime] = None, to_date: Optional[datetime] = None, skip: int = 0, limit: int = 100):
  # If from_date is not provided, set it to today's date
  if not from_date:
    from_date = datetime.today()

  # If to_date is not provided, set it to today's date
  if not to_date:
    to_date = datetime.today()

  return db.query(models.Transaction)\
            .filter(models.Transaction.ticker == ticker_id)\
            .filter(models.Transaction.trade_date >= from_date)\
            .filter(models.Transaction.trade_date <= to_date)\
            .order_by(models.Transaction.trade_date.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()


