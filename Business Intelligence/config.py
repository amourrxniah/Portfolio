import os
from dotenv import load_dotenv

load_dotenv()

class Config:
   #covid19.com endpoints
   COVID_API_BASE = "https://covid-api.com"

   #api endpoints for covid-api.com
   ENDPOINTS = {
      'reports': '/api/reports',
      'regions': '/api/regions',
      'reports_total': '/api/reports/total',
      'region': '/api/reports' #/api/reports?iso={country_code}
   }

   #dashboard settings
   UPDATE_INTERVAL = 300 #5min in sec
   CACHE_DURATION = 3600 #1hr in sec

   #kpi targets for demonstration
   TARGETS = {
      'case_per_million': 50000,
      'deaths_per_million': 500,
      'recovery_rate': 95, #percentage
      'active_cases_ratio': 10 #percentage
   }