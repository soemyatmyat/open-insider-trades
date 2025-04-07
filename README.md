# Open Insider Trades API

## Description
This project provides API endpoints to retrieve insider trading transactions (SEC Form 4 Insider Trading activities) based on the stock ticker, trade type, and date range. The data is scraped from [openinsider.com](http://openinsider.com) using BeautifulSoup and is stored in an SQLite database using SQLAlchemy. This project was created as a personal hobby project to integrate with my own tools, as I couldn’t find a suitable source for insider trades. Additional features may be added in the future.

**Technologies Used:**
- FastAPI
- BeautifulSoup
- SQLAlchemy
- SQLite3

## Features

### Basic Features
- [X] **JWT Authentication** – Secure API access using JWT tokens.
- [ ] **Rate Limiting** – Implemented to prevent overloading the API (to be added).
- [X] **HTTP Exception Handling** – Custom error handling for API responses.

### API Endpoints
Swagger/OpenAPI documentation: `{{base-url}}/docs#/`

- [X] **Retrieve Trades by Ticker**: `{{base-url}}/trades/ticker`  
  Allows you to retrieve insider trades by stock ticker. **Date range** and **transaction type** are optional parameters.

- [X] **Retrieve Trades by Date Range**: `{{base-url}}/trades`  
  Retrieve insider trades by a specified date range. **Transaction type** is optional.

### Admin Features (Login Required)
- [X] **Force Refresh / Bootstrapping** – Runs a web scraping script to refresh the data.
- [X] **Daily Sync** – Automatically fetches and processes new data daily.
- [ ] **Enable/Disable Daily Sync** – Enable or disable the daily sync (using Celery with Redis - is this an overkill?).
- [ ] **Dump Data to CSV** – Export the data into a CSV format.
- [ ] **Bulk Update** –  
  - [ ] Load data from a CSV file.
  - [ ] Validate CSV file contents.
  - [ ] Use an "all or nothing" approach for error handling (rollback if errors occur).

**Bootstrapping** will trigger the web scraping script on [openinsider.com](http://openinsider.com) and save the data into CSV files. These files are then processed and imported into the database in batches. By default, the earliest data extraction date is set to **2003-01-01** (YYYY-MM-DD), but this can be configured.

**Daily Sync** is enabled by default, meaning new data is fetched and processed every day at midnight GMT/UTC.

## How to Run Locally

1. Clone the repository:
  ```bash
  git clone <repo-url>
  cd open-insider-trades
  ```
2. Install the dependencies:
  ```bash
  pip install -r requirements.txt
  ```
3. Set up environment variables in a `.env` file (example):
  ```
  SQLALCHEMY_DATABASE_URL=sqlite:///./test.db
  ```
4. Run the application:
  ```bash
  uvicorn main:app --reload
  ```

The API will be available at `http://127.0.0.1:8000`.

### File Structure
```
open-insider-trades/     
├── main.py                   # FastAPI app entry point 
├── settings.py               # App settings & environment config
├── db.py                     # Database connection setup
├── models/                   # 1/ Database models      
│   └── client.py    
│   └── transaction.py        
├── routers/                  # 3/ API route handlers       
│   └── admin.py  
│   └── auth.py 
│   └── transaction.py    
│   └── utils 
│     └── exceptions.py       # http exception errors  
├── schemas/                  # 2/ Request & Response schemas for Pydantic and OpenAPI Generation  
│   └── auth.py         
│   └── transaction.py       
├── services/                 # 4/ Fetch, preprocess and prepare the data       
│   └── transaction.py      
│   └── auth.py       
│   └── utils 
│     └── token.py 
├── requirements.txt          # Libraries Dependencies
├── Dockerfile                # Docker configuration
├── .env                      # Environment variables
├── .dockerignore             # Ignore unnecessary files in Docker build
├── .gitignore                # Ignore unnecessary files in Git
├── build.sh                  # shell script to run the app locally
└── README.md                 # Documentation
```

## References
This project follows:
1. The best practices outlined by the [Twelve-Factor App](https://12factor.net), treating logs as event streams.
2. The [Style Guide for Python Code](https://peps.python.org/pep-0008/) to ensure clean, readable, and consistent code.
