
### Description
This project provides API endpoints to retrieve insider transactions (SEC Form 4 Insider Trading activities) based on the ticker, trade type, and date range. I decided to quickly build this to integrate with my own hobby project as I could not find any other easily accessible sources for insider trades. The data is scraped (using BeautifulSoup) from the openinsider.com website for SEC Form 4 Insider Trading Transactions. I may add more features in the future. This project is built with FastAPI framework, BeautifulSoup, and SQLAchemy with SQLite3.

### Functionalities

#### API 
Swagger documentation: [to-link] 
Filter trades by
- [ ] Ticker: 
- [ ] Trade Type:  
- [ ] Date Range:  
- [X] Ticker and Date Range:

#### Admin Feature (login required)
- [X] Force refresh (Wipe the data clean if there is any, and proceed with the bootstrapping)
- [ ] Daily Sync (enable/disable with the timer)
- [ ] Dump the data into csv
- [ ] Load the data from csv (Be careful as this action overwrites the existing data)

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
├── models/                   # Database models      
│   └── transaction.py        
├── schemas/                  # Request & response schemas for Pydantic, OpenAPI Generation  
│   └── transaction.py        
├── routers/                  # API route handlers       
│   └── transaction.py    
├── services/                 # Fetch, preprocess and prepare the data       
│   └── transaction.py         
├── internal/                 # Internal/private routes for the admin module      
│   └── admin.py              
├── requirements.txt          # Libraries Dependencies
├── Dockerfile                # Docker configuration
├── .env                      # Environment variables
├── .dockerignore             # Ignore unnecessary files in Docker build
├── .gitignore                # Ignore unnecessary files in Git
├── build.sh                  # shell script to run the app locally
└── README.md                 # Documentation
```

### References
This project follows the best practice of (the Twelve-Factor App)[https://12factor.net/logs] amd treat logs as event streams. 
