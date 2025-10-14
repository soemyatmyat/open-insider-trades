# Open Insider Trades API

## Description
This project provides API endpoints to retrieve insider trading transactions (SEC Form 4 Insider Trading activities) based on the stock ticker, trade type, and date range. The data is scraped from [openinsider.com](http://openinsider.com) using BeautifulSoup and is stored in an SQLite database using SQLAlchemy. This project was created as a personal hobby project to integrate with my own tools, as I couldn’t find a suitable source for insider trades. Additional features may be added in the future.

**Technologies Used:**
- FastAPI – for building the API.
- BeautifulSoup – for web scraping from openinsider.com.
- SQLAlchemy – for ORM-based database interactions.
- SQLite3 – as the primary database.
- Redis – used for rate limiting and caching. Rate limit parameters are defined in the settings and are role-based, allowing different limits per user (useful when a user can create multiple keys). The rate limiting uses a sliding window approach:
Sliding Window Mechanism:
(1) Store timestamps of recent requests within the last n seconds.
For each incoming request:
(2) Remove timestamps older than n seconds.
(3) Count the remaining timestamps.
If the count is greater than or equal to the allowed limit, block the request. Otherwise, allow it and log the new timestamp.
- [JWT Authentication](https://datatracker.ietf.org/doc/html/rfc7519) with refresh_token
- [APScheduler](https://apscheduler.readthedocs.io/en/3.x/userguide.html) for cron job trigger embedded into the FastAPI. This is not a scalable approach. A better solution would be to containerize the cron jobs OR better yet, implement celery + redis. 

## Features

### Basic Features
| Feature                         | Status | Notes                                                                 |
|---------------------------------|--------|-----------------------------------------------------------------------|
| **JWT Authentication**          | ✅     | Access token in `Authorization` header; refresh token in cookie      |
| **Refresh Token in Cookie**     | ✅     | Stored in `HttpOnly` cookie to prevent JavaScript access             |
| **CSRF Protection**             | ✅     | CSRF token in cookie + `X-CSRF-Token` header                |
| **Rate Limiting (per client)**  | ✅     | Sliding window; Redis-backed with SQLite fallback                    |
| **Custom Error Handling**       | ✅     | Clean JSON error responses with consistent structure                 |

---

### User Endpoints (Login Required)

 **Docs**  
- Swagger / OpenAPI: `{{base-url}}/docs#/`
- Redoc: `{{base-url}}/redoc`

| Feature                                              | Status | Endpoint / Notes                                                                 |
|-------------------------------------------------------|--------|-----------------------------------------------------------------------------|
| **Get insider trades by ticker**               | ✅     | `GET /insider_trades/{{ticker_id}}`  - Retrieve insider trades by stock ticker. Optional: date range, type        |
| **Get insider trades by date range**           | ✅     | `GET /insider_trades`  - Retrieve insider trades by date range. Optional: transaction type          |

---

### Admin Features (Login Required)

| Feature                        | Status | Endpoint / Notes                                                                 |
|--------------------------------|--------|----------------------------------------------------------------------------------|
| **Force Refresh / Bootstrapping** | ✅     | `POST /admin/bootstrap` - Run scraping script to refresh data                  |
| **Generate Client ID**         | ✅     | `POST /admin/generate_client_id` - Returns a one-time-use ID and password      |
| **Daily Sync**                 | ✅     | Enabled by default - runs at midnight UTC (not exposed as an endpoint)         |
| **Enable/Disable Daily Sync** | ✅      | Toggle daily sync task                               |
| **Dump Data to CSV**           | 🚧     | Planned - export DB contents to CSV                                            |
| **Bulk Upload (CSV)**          | 🚧     | Planned - file limit ~5MB                                                      |
| &nbsp;&nbsp;&nbsp;• Validate CSV contents  | 🚧     | Check headers, format, and required fields                                     |
| &nbsp;&nbsp;&nbsp;• Load data from CSV     | 🚧     | Parse and ingest file contents into database                                   |
| &nbsp;&nbsp;&nbsp;• Rollback on failure    | 🚧     | "All or nothing" import behavior for data integrity                            |

---

### Security

#### JWT Authentication
- **Access Token** must be sent via the `Authorization: Bearer <token>` header for every requests.
- **Refresh Token** is send and receive in an `HttpOnly` cookie - this prevents access from JavaScript, helping mitigate **XSS attacks**.

#### CSRF Protection
- A **CSRF token** will be issued as a normal (non-HttpOnly) cookie.
- The requests must send this token back in the `X-CSRF-Token` header for `/auth/refresh`. This is to provent **Cross-Site Request Forgery** attacks.

#### Example using `curl` (adapt accordingly for client calls):
```bash
# authenticate and store the http cookies into txt
curl --verbose -c cookies.txt https://localhost:<port>/auth/token \
  -d 'username=<api-key>&password=<password>'

# Use stored cookie and send CSRF token in header
curl --verbose -b cookies.txt -c cookies.txt -X POST \
  https://localhost:<port>/auth/refresh \
  -H "X-CSRF-Token: <csrf-token>"
```

### Additional Notes

- **Bootstrapping** triggers scraping from [openinsider.com](http://openinsider.com) and imports data starting from `2003-01-01` (configurable). 
- **Daily Sync** runs every midnight (UTC) to pull and ingest new data automatically.

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
  BASE_URL="http://openinsider.com/screener"  # this is where data is scraped 
  SECRET_KEY="<your-secret-key>"
  ALGORITHM="<your-jwt-algorithm>"
  ACCESS_TOKEN_EXPIRE_MINUTES=30
  MAX_WORKERS=3                               # Number of threads for data extraction and import
  DEFAULT_FILLING_DAYS=1                      # Custom filling date
  TRADE_DATE_FILTER=0                         # Trade date = all dates
  OUTPUT_FILE="<your-output-filename>"        # File to save the extracted data
  MAX_ROWS=5000
  SUPER_ADMIN_ID="<uuid>"
  SUPER_ADMIN_SECRET="<passcode>"
  REDIS_URL="<redis-url>"                     # Optional: the hostname/IP address of your Redis server for caching. If not defined, cache falls back to SQLite. This is for rate-limiting. If redis is not available, rate-limit falls back to sql. 
  REDIS_PASSWORD="<redis-pass>"               # If Redis requires authentication, put the password here
  REDIS_PORT=6379
  REDIS_EX=600                                # Optional: Set the expiration time (in seconds) for Redis keys
  COOKIE_SECURE=True                          # Set to True if using HTTPS
  COOKIE_DOMAIN="" # Domain for the cookie
  ```
4. Run the application:
  ```bash
  uvicorn main:app --reload
  ```
  With local certs
  ```bash
  uvicorn main:app --host 127.0.0.1 --port 8000 --reload --ssl-keyfile=key.pem --ssl-certfile=cert.pem
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
│  ├── scheduler/                # 5/ For scheduling logic
│  │   └── scheduler.py          # configure and start APScheduler which triggers the daily
│  ├── requirements.txt          # Libraries Dependencies
│  ├── Dockerfile                # Docker configuration
│  ├── .env                      # Environment variables
│  ├── .dockerignore             # Files ignored during Docker build
│  └── out                       # Folder to store the scrapped data 
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
4. [FastAPI documentation](https://fastapi.tiangolo.com/)
5. [Beautiful Soup documentation](https://beautiful-soup-4.readthedocs.io/en/latest/)
