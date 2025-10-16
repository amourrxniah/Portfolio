import requests
import pandas as pd
from datetime import datetime, timedelta
import time
from config import Config

class COVIDDataClient:
    def __init__(self):
        self.base_url = Config.COVID_API_BASE
        self.endpoints = Config.ENDPOINTS
        self.timeout = 5
        self.max_retries = 1

    def _make_requests(self, url, params=None):
        """helper method to make api requests with error handling"""
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.Timeout:
                print(f"Timeour error on attempt {attempt + 1}")
                if attempt == self.max_retries - 1:
                    return None
                time.sleep(1) #wait before retry
            except requests.exceptions.RequestException as e:
                print(f"Requests error: {e}")
                return None
            return None
    
    def get_reports_total(self, date=None):
        """get total global reports"""
        try:
            url = f"{self.base_url}{self.endpoints['reports_total']}"
            params = {}
            if date:
                params['date'] = date
                
            data = self._make_requests(url, params)
            if data and 'data' in data:
                return data.get('data', [])
            return None
        except Exception as e:
            print(f"Error fetching total reports: {e}")
            return None
    
    def get_all_reports(self, date=None, iso=None):
        """get all reports with optional date and country filtering"""
        try:
            url = f"{self.base_url}{self.endpoints['reports']}"
            params = {}
            if date:
                params['date'] = date
            if iso:
                params['iso'] = iso
                
            data = self._make_requests(url, params)
            if data and 'data' in data:
                return data.get('data', [])
            return None
        except Exception as e:
            print(f"Error fetching reports: {e}")
            return None
    
    def get_regions(self):
        """get list of all available regions/countries"""
        try:
            url = f"{self.base_url}{self.endpoints['regions']}"
            data = self._make_requests(url)
            if data and 'data' in data:
                return data.get('data', [])
            return None
        except Exception as e:
            print(f"Error fetching reports: {e}")
            return None
    
    def get_historical_data(self, iso, days=30):
        """get historical data for a specific country"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=min(days, 14))
            
            all_data = []
            current_date = start_date
            
            while current_date <= end_date and len(all_data) < 14:
                date_str = current_date.strftime('%Y-%m-%d')
                reports = self.get_all_reports(date=date_str, iso=iso)
                
                if reports:
                    #find the report for the specific country
                    for report in reports:
                        if report.get('region', {}).get('iso') == iso:
                            report['date'] = date_str
                            all_data.append(report)
                            break
                
                current_date += timedelta(days=1)
                time.sleep(0.2)  #be nice to the API
            
            return all_data
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return None
    
    def get_global_historical(self, days=20):
        """get global historical data"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=min(days, 14))
            
            all_data = []
            current_date = start_date
            
            while current_date <= end_date and len(all_data) < 14:
                date_str = current_date.strftime('%Y-%m-%d')
                total_data = self.get_reports_total(date=date_str)
                
                if total_data:
                    for item in total_data:
                        if item: #check if item is not None
                            item['date'] = date_str
                            all_data.append(item)
                
                current_date += timedelta(days=1)
                time.sleep(0.2)  #be nice to the API
            
            return all_data
        except Exception as e:
            print(f"Error fetching global historical data: {e}")
            return None

#test the API client
if __name__ == "__main__":
    client = COVIDDataClient()
    
    print("Testing COVID-API.com connection...")
    
    #test global data
    global_data = client.get_reports_total()
    if global_data:
        latest = global_data[0] if global_data else {}
        print("Global Data:")
        print(f"Date: {latest.get('date', 'N/A')}")
        print(f"Confirmed: {latest.get('confirmed', 'N/A'):,}")
        print(f"Deaths: {latest.get('deaths', 'N/A'):,}")
        print(f"Recovered: {latest.get('recovered', 'N/A'):,}")
        print(f"Active: {latest.get('active', 'N/A'):,}")
    else:
        print("Could not fetch global data")
    
    #test regions
    regions = client.get_regions()
    if regions:
        print(f"\nAvailable regions: {len(regions)}")
        print("Sample regions:")
        for region in regions[:5]:
            print(f"  - {region.get('name')} ({region.get('iso')})")
    else:
        print("Could not fetch regions")