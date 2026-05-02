# Used Car Pricing in the Detroit 100-Mile Market

## Project Summary

This project analyzes used car listings within 100 miles of Detroit, Michigan using data collected from the MarketCheck Cars API. The analysis focuses on four high-volume brands: Toyota, Honda, Ford, and Chevrolet.

The main goals are to identify key predictors of listing price, test whether the relationship between mileage and price differs by brand, and examine whether vehicle attributes such as body type, drivetrain, and transmission still matter after controlling for age and mileage.

## Research Questions

1. What factors are most strongly associated with used car listing prices?
2. Does mileage affect price differently across Toyota, Honda, Ford, and Chevrolet?
3. Do vehicle characteristics such as body type, drivetrain, and transmission add explanatory value after controlling for age and mileage?

## Tools Used

- R / Quarto
- Python
- MarketCheck Cars API
- CSV
- Regression modeling
- Data visualization

## Files Included

- `UsedCarsFinalProject-Hijazi.qmd` — main Quarto report source file
- `UsedCarsFinalProject-Hijazi.html` — rendered HTML report
- `data/processed/used_cars_detroit_clean.csv` — cleaned dataset used in the analysis
- `etl/01_pull_all_brands.py` — Python script used to collect listing data
- `screencast_link.txt` — link to the project screencast

## How to View the Project

Open `UsedCarsFinalProject-Hijazi.html` in a web browser to read the final report.

## How to Rerun the Project

1. Open the project folder in RStudio or VS Code.
2. Make sure the required R packages are installed:
   - `dplyr`
   - `readr`
   - `forcats`
   - `ggplot2`
   - `scales`
   - `gt`
   - `broom`
   - `car`
3. Render `UsedCarsFinalProject-Hijazi.qmd` to HTML.

## Data Notes

- The cleaned CSV is included so the report can be rerun without making new API calls.
- Raw API response files are included for transparency and reproducibility.
- Data was collected using the MarketCheck Cars API free tier, which has a monthly request limit.
- The API key is not included for security reasons.
- To rerun the data collection script, create a local `.env` file or set a `MARKETCHECK_API_KEY` environment variable.

## Main Findings

- Mileage and vehicle age were the strongest predictors of used car listing price.
- Toyota and Honda listings showed slower price declines with mileage compared with Ford and Chevrolet.
- SUVs, pickups, and certain drivetrain types tended to carry price premiums after controlling for age and mileage.
- Modeling log(price) improved interpretability and helped address right-skewness in listing prices.

## Notes

- Developed and tested in R 4.4.x with Quarto 1.4+.
- All file paths in the report are relative to the project root.