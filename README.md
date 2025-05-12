# Open Insider Trades API

## Description
This project provides API endpoints to retrieve insider trading transactions (SEC Form 4 Insider Trading activities) based on the stock ticker, trade type, and date range. The data is scraped from [openinsider.com](http://openinsider.com) using BeautifulSoup and is stored in an SQLite database using SQLAlchemy. This project was created as a personal hobby project to integrate with my own tools, as I couldn’t find a suitable source for insider trades. Additional features may be added in the future.

**Technologies Used:**
- FastAPI – for building the API.
- BeautifulSoup – for web scraping from openinsider.com.
- SQLAlchemy – for ORM-based database interactions.
- SQLite3 – as the primary database.
- Redis – for rate limiting and caching. 

## Features

### Basic Features
- [X] **JWT Authentication**: Secure API access using JWT tokens.
- [X] **Rate Limiting per user/client**: Implemented to prevent overloading the API, with **sliding window mechanism**. 
  - [X] Redis as primary for rate limiting.
  - [X] SQLite as fallback if Redis is unavailable.
- [X] **HTTP Exception Handling**: Custom error handling for API responses.

### API Endpoints (Login Required)
- Swagger/OpenAPI documentation: `{{base-url}}/docs#/`
- Redoc: `{{base-url}}/redoc`
- [X] **Retrieve Trades by Ticker**: `{{base-url}}/insider_trades/{{ticker_id}}`  
  Allows you to retrieve insider trades by stock ticker. **Date range** and **transaction type** are optional parameters.

- [X] **Retrieve Trades by Date Range**: `{{base-url}}/insider_trades`  
  Retrieve insider trades by a specified date range. **Transaction type** is optional.

### Admin Features (Login Required)
- [X] **Force Refresh / Bootstrapping**: `{{base-url}}/admin/generate_client_id` 
  Runs a web scraping script to refresh the data.
- [X] **Generate Client Id**: `{{base-url}}/admin/generate_client_id` 
  Create a new client id and password (display only once)
- [X] **Daily Sync**: 
  Not available as an endpoint. 
- [ ] **Enable/Disable Daily Sync**: 
  Enable or disable the daily sync (using Celery with Redis - is this an overkill?).
- [ ] **Dump Data to CSV**: 
  Export the data into a CSV format.
- [ ] **Bulk Upload**: 
  - File size limit: ~5 MB 
  - [ ] Validate CSV file contents
  - [ ] Load data from a CSV file
  - [ ] Use "all or nothing" for error handling: Rollback on failure

**Bootstrapping** will trigger the web scraping script on [openinsider.com](http://openinsider.com) and save the data into CSV files. These files are then processed and imported into the database in batches. By default, the earliest data extraction date is set to **2003-01-01** (YYYY-MM-DD), but this can be configured.

**Daily Sync** is enabled by default, meaning once the system is live, new data is fetched and processed every day at midnight GMT/UTC.

## How to Run Locally

1. Clone the repository:
  ```bash
  git clone <repo-url>
  cd open-insider-trades/server 
  ```
2. Create a python virtual environment and activate it:
  ```bash
  python3 -m venv venv
  . venv/bin/activate
  ```
2. Install the dependencies:
  ```bash
  pip install -r requirements.txt
  ```
3. Set up environment variables in a `.env` file (example):
  ```
  SQLALCHEMY_DATABASE_URL=sqlite:///./<your-sqlite3>.db
  BASE_URL="http://openinsider.com/screener"
  SECRET_KEY="<your-secret-key>"
  ALGORITHM="<your-jwt-algorithm>"
  ACCESS_TOKEN_EXPIRE_MINUTES=30
  MAX_WORKERS=3  # Number of threads for data extraction
  DEFAULT_FILLING_DAYS=1  # Custom filling date
  TRADE_DATE_FILTER=0  # Trade date = all dates
  OUTPUT_FILE="<your-output-filename>"  # File to save the extracted data
  MAX_ROWS=5000
  SUPER_ADMIN_ID="<uuid>"
  SUPER_ADMIN_SECRET="<passcode>"
  REDIS_URL="<redis-url>" # or the hostname/IP address of your Redis server
  REDIS_PASSWORD="<redis-pass>" # If Redis requires authentication, put the password here
  REDIS_PORT=6379
  REDIS_EX=600 # Optional: Set the expiration time (in seconds) for Redis keys
  ```
4. Run the application:
  ```bash
  uvicorn main:app --reload
  ```

The API will be available at `http://127.0.0.1:8000`.

### File Structure
```
open-insider-trades/
├── server      
│  ├── main.py                    # FastAPI app entry point 
│  ├── settings.py                # App settings & environment config
│  ├── db.py                      # Database connection setup
│  ├── models/                    # 1/ Database models      
│  │   ├── client.py    
│  │   └── transaction.py        
│  ├── routers/                   # 2/ API route handlers       
│  │   ├── admin.py  
│  │   ├── auth.py 
│  │   ├── transaction.py    
│  │   └── utils 
│  │       └── exceptions.py     # Custom error responses
│  ├── schemas/                  # 3/ Request & Response schemas for Pydantic and OpenAPI  
│  │   ├── auth.py         
│  │   └── transaction.py       
│  ├── services/                 # 4/ Fetch, preprocess and prepare the data       
│  │   ├── transaction.py   
│  │   ├── ratelimiter.py     
│  │   ├── auth.py       
│  │   └── utils 
│  │       └── token.py 
│  ├── requirements.txt          # Libraries Dependencies
│  ├── Dockerfile                # Docker configuration
│  ├── .env                      # Environment variables
│  └── .dockerignore             # Files ignored during Docker build
├── .gitignore                   # Git ignored files
├── build.sh                     # Shell script to run the app locally
├── .env                         # Redis environment variables
├── docker-compose.yml  
└── README.md                    # Documentation

```

## References
This project follows:
1. The best practices outlined by the [Twelve-Factor App](https://12factor.net), treating logs as event streams.
2. The [Style Guide for Python Code](https://peps.python.org/pep-0008/) to ensure clean, readable, and consistent code.
3. The data validation library for Python: [Pydantic](https://docs.pydantic.dev/latest/)
