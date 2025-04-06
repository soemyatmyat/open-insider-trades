
### Description
This project provides the API endpoints to retrieve insider transactions (SEC Form 4 Insider Trading activities) based on the ticker, trade type, and date range. I decided to quickly build this to integrate with my own hobby project as I could not find any other easily accessible sources for insider trades. The data is scraped (using BeautifulSoup) from the openinsider.com website for SEC Form 4 Insider Trading Transactions. I may add more features in the future. This project is built with FastAPI framework, BeautifulSoup, and SQLAchemy with SQLite3.

### Functionalities

#### Basic
- [X] JWT Authentication
- [ ] Implement Rate limit 
- [X] Encapsulate http exceptions 

#### API Endpoints
Swagger/OpenAPI documentation: {{base-url}}/docs#/
- [X] Retrieve trades by the ticker (Date Range and Transaction type are optional): {{base-url}}/trades/ticker (Retrieve By Ticker)
- [X] Retrieve trades by the date range  (Transaction type is optional): {{base-url}}/trades (Retrieve By Date Range)

#### Admin Feature (login required)
- [X] Force refresh/ Bootstrapping
- [X] Daily Sync 
- [ ] Enable/disable the daily sync (Celery with Redis - is it an overkill?)
- [ ] Dump the data into the csv
- [ ] Bulk update 
  - [ ] Load the data from the csv 
    - [ ] Validate the csv file 
    - [ ] Thrown errors with an all or nothing approach (rollback when there are any errors)

- **Bootstrapping** will run the webscrapping script on http://openinsider.com and save the data into the csv. The saved csv files are processed batch by batch into the database. By default, the earliest date for data extraction is set to '2003-01-01' (YYYY-MM-DD), but this can be a configurable parameter. 
- **Daily sync** is enabled, by default, and therefore, the new data is fetched and processed everyday at midnight GMT/UTC epoch time. 

### How to run locally
<placeholder>

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

### References
This project follows 
1. the best practice of [the Twelve-Factor App](https://12factor.net) and treat logs as event streams. 
2. This project follows the standard [Style Guide for Python Code](https://peps.python.org/pep-0008/).
