from homeassistant.const import Platform
from datetime import datetime, timedelta

DOMAIN = "florida_fire_danger_index"
ONE_DAY = timedelta(days=1)
PLATFORMS = [Platform.SENSOR]
TABLE_DATAFRAME = "table#T_30215.dataframe tbody tr"
COUNTY_COL_INDEX = "td:nth-of-type(1)"
FDI_COL_INDEX = "td:nth-of-type(2)"
FLORIDA_FDI_URL = "https://weather.fdacs.gov/FDI/fdi-report.html"
LOCATIONS = [ "Alachua", "Baker", "Bay", "Bradford", "Brevard", "Broward","Calhoun",
              "Charlotte", "Citrus", "Clay", "Collier", "Columbia", "DeSoto", "Dixie",
              "Duval", "Escambia", "Flagler", "Franklin", "Gadsden", "Gilchrist", "Glades",
              "Gulf", "Hamilton", "Hardee", "Hendry", "Hernando", "Highlands", "Hillsborough",
              "Holmes", "Indian River", "Jackson", "Jefferson", "Lafayette", "Lake", "Lee", 
              "Leon", "Levy", "Liberty", "Madison", "Manatee", "Marion", "Martin", "Miami-Dade",
              "Monroe", "Nassau", "Okaloosa", "Okeechobee", "Orange", "Osceola", "Palm Beach",
              "Pasco", "Pinellas", "Polk", "Putnam", "St. Johns", "St. Lucie", "Santa Rosa",
              "Sarasota", "Seminole", "Sumter", "Suwanee", "Taylor", "Union", "Volusia", "Wakulla",
              "Walton", "Washington" ]
