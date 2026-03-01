# NCAA Women's Lacrosse Offensive Efficiency Dashboard

This project tracks offensive efficiency across NCAA Division 1 women's lacrosse teams using live data scraped from NCAA statistics pages.

## Metrics Built

- Estimated Possession = Shots + Turnovers
- Offensive Efficiency = Goals / Possessions
- Shot Efficiency = Goals / Total Shots
- Turnover Rate = Turnover / Possessions
- Pace = Possessions / Games Played

## Features

- Automated scraping pipeline
- Data cleaning and merging
- Efficiency modeling
- Interactive Potly dashboards
- Season-updating workflow

## How To Run

1. Install dependencies:
   pip install -r requirements.txt

2. Run the notebook:
   notebooks/dashboard.ipynb

## Future Improvements

- Strength-of-schedule adjustment
- Rolling efficiency trends
- Conference filtering
- Deployment via Streamlit
