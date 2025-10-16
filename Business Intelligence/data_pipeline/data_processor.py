import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .api_client import COVIDDataClient
import threading

class DataProcessor:
    def __init__(self):
        self.client = COVIDDataClient()
        self.cache = {}
        self.cache_timestamp = {}
        self.use_real_data = True #flay to toggle real vs stimulated data
    
    def get_cached_data(self, key, max_age=3600):
        """get cached data if not expired"""
        current_time = datetime.now().timestamp()
        if (key in self.cache and 
            key in self.cache_timestamp and
            current_time - self.cache_timestamp[key] < max_age):
            return self.cache[key]
        return None
    
    def set_cached_data(self, key, data):
        """store data in cache"""
        self.cache[key] = data
        self.cache_timestamp[key] = datetime.now().timestamp()
    
    def get_global_kpis(self):
        """get global COVID-19 KPIs - use simulated data first for speed"""
        cache_key = 'global_kpis'
        cached_data = self.get_cached_data(cache_key, 300)
        
        if cached_data:
            return cached_data
        
        #try real API data with timeout
        real_data = None
        if self.use_real_data:
            try:
                #use short timeout for API call
                import signal
                
                def timeout_handler(signum, frame):
                    raise TimeoutError("API call timed out")
                
                # Set timeout for API call
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(5)  # 5 second timeout
                
                real_data = self.client.get_reports_total()
                signal.alarm(0)  # Cancel timeout
                
            except (TimeoutError, Exception) as e:
                print(f"API call failed, using simulated data: {e}")
                self.use_real_data = False  # Fall back to simulated data
                real_data = None
        
        if real_data:
            latest = real_data[0] if real_data else {}
            confirmed = latest.get('confirmed', 0)
            deaths = latest.get('deaths', 0)
            recovered = latest.get('recovered', 0)
            active = latest.get('active', 0)
            
            death_rate = (deaths / confirmed * 100) if confirmed > 0 else 0
            recovery_rate = (recovered / confirmed * 100) if confirmed > 0 else 0
            
            kpis = {
                'total_cases': confirmed,
                'total_deaths': deaths,
                'total_recovered': recovered,
                'active_cases': active,
                'death_rate': death_rate,
                'recovery_rate': recovery_rate,
                'last_updated': datetime.now().isoformat(),
                'data_source': 'COVID-API.com (Real Data)'
            }
        else:
            kpis = self._get_simulated_global_kpis()
        
        self.set_cached_data(cache_key, kpis)
        return kpis
    
    def get_country_comparison(self, top_n=10):
        """get comparison data for top countries"""
        cache_key = f'country_comparison_{top_n}'
        cached_data = self.get_cached_data(cache_key, 600)  #10min cache
        
        if cached_data:
            return cached_data
        
        #get latest reports for all countries
        reports = self.client.get_all_reports()
        if not reports:
            return self._get_simulated_country_data(top_n)
        
        #process country data
        country_data = []
        for report in reports:
            region = report.get('region', {})
            if region and region.get('name') and region.get('name') != 'Global':
                country_info = {
                    'country': region.get('name'),
                    'iso': region.get('iso'),
                    'cases': report.get('confirmed', 0),
                    'deaths': report.get('deaths', 0),
                    'recovered': report.get('recovered', 0),
                    'active': report.get('active', 0),
                    'deaths_per_million': 0,  #calculate if population data available
                    'cases_per_million': 0    #calculate if population data available
                }
                
                #calculate rates
                if country_info['cases'] > 0:
                    country_info['death_rate'] = (country_info['deaths'] / country_info['cases'] * 100)
                    country_info['recovery_rate'] = (country_info['recovered'] / country_info['cases'] * 100)
                else:
                    country_info['death_rate'] = 0
                    country_info['recovery_rate'] = 0
                
                country_data.append(country_info)
        
        #convert to DataFrame for sorting
        df = pd.DataFrame(country_data)
        
        if df.empty:
            return self._get_simulated_country_data(top_n)
        
        #get top countries by cases
        top_countries = df.nlargest(top_n, 'cases')
        
        result = {
            'top_by_cases': top_countries.to_dict('records'),
            'summary_stats': {
                'total_countries': len(df),
                'global_cases': df['cases'].sum(),
                'global_deaths': df['deaths'].sum(),
                'average_death_rate': df['death_rate'].mean()
            }
        }
        
        self.set_cached_data(cache_key, result)
        return result
    
    def get_historical_trends(self, country='global', days=30):
        """get historical trends with type safety"""
        #ensure parameters are correct types
        if country is None:
            country = 'global'
        if days is None:
            days = 30

        #convert to proper types if needed
        country = str(country)
        days = int(days)
        
        cache_key = f'historical_{country}_{days}'
        cached_data = self.get_cached_data(cache_key, 600)
        
        if cached_data:
            return cached_data
        
        if country == 'global':
            data = self.client.get_global_historical(days)
        else:
            #get country ISO code first
            reports = self.client.get_all_reports()
            iso_code = None

            #check if reports is not None before iterating
            if reports:
                for report in reports:
                    if report: #check if report is not None
                        region = report.get('region', {})
                        if region.get('name') == country:
                            iso_code = region.get('iso')
                            break
            
            if iso_code:
                data = self.client.get_historical_data(iso_code, days)
            else:
                data = None
        
        if not data:
            return self._get_simulated_historical_data(days)
        
        #process historical data
        processed_data = []
        for item in data:
            if item: #check if item is not None
                date = item.get('date', '')
                confirmed = item.get('confirmed', 0)
                deaths = item.get('deaths', 0)
                recovered = item.get('recovered', 0)
                active = item.get('active', 0)
            
                processed_data.append({
                    'date': date,
                    'confirmed': confirmed,
                    'deaths': deaths,
                    'recovered': recovered,
                    'active': active
                })
        
        #calculate daily changes
        df = pd.DataFrame(processed_data)
        if not df.empty:
            df = df.sort_values('date')
            df['new_cases'] = df['confirmed'].diff().fillna(df['confirmed'])
            df['new_deaths'] = df['deaths'].diff().fillna(df['deaths'])
            df['7day_avg_cases'] = df['new_cases'].rolling(window=7).mean()
            df['7day_avg_deaths'] = df['new_deaths'].rolling(window=7).mean()
        
        result = df.to_dict('records') if not df.empty else []
        self.set_cached_data(cache_key, result)
        return result
    
    def get_available_countries(self):
        """get list of available countries"""
        cache_key = 'available_countries'
        cached_data = self.get_cached_data(cache_key, 3600)  #1hr cache
        
        if cached_data:
            return cached_data
        
        reports = self.client.get_all_reports()
        if not reports:
            return ['USA', 'India', 'Brazil', 'France', 'Germany', 'UK', 'Italy', 'Spain', 'Russia', 'Japan']
        
        countries = []
        if reports:
            for report in reports:
                if report:
                    region = report.get('region', {})
                    name = region.get('name')
                    if name and name != 'Global' and name not in countries:
                        countries.append(name)
        
        countries.sort()
        self.set_cached_data(cache_key, countries)
        return countries
    
    #fallback simulated data methods
    def _get_simulated_global_kpis(self):
        """generate realistic simulated global KPIs"""
        return {
            'total_cases': 700000000,
            'total_deaths': 7000000,
            'total_recovered': 650000000,
            'active_cases': 43000000,
            'death_rate': 1.0,
            'recovery_rate': 92.8,
            'active_rate': 6.2,
            'cases_per_million': 87500,
            'deaths_per_million': 875,
            'last_updated': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'data_source': 'Simulated Data (API Unavailable)'
        }
    
    def _get_simulated_country_data(self, top_n=10):
        """generate simulated country data"""
        countries = [
            {'country': 'USA', 'cases': 100000000, 'deaths': 1100000, 'recovered': 98000000, 'death_rate': 1.1},
            {'country': 'India', 'cases': 45000000, 'deaths': 530000, 'recovered': 44400000, 'death_rate': 1.18},
            {'country': 'Brazil', 'cases': 37000000, 'deaths': 700000, 'recovered': 36000000, 'death_rate': 1.89},
            {'country': 'France', 'cases': 38000000, 'deaths': 160000, 'recovered': 37700000, 'death_rate': 0.42},
            {'country': 'Germany', 'cases': 38000000, 'deaths': 170000, 'recovered': 37700000, 'death_rate': 0.45},
            {'country': 'UK', 'cases': 24000000, 'deaths': 220000, 'recovered': 23700000, 'death_rate': 0.92},
            {'country': 'Italy', 'cases': 26000000, 'deaths': 190000, 'recovered': 25700000, 'death_rate': 0.73},
            {'country': 'Russia', 'cases': 23000000, 'deaths': 400000, 'recovered': 22500000, 'death_rate': 1.74},
            {'country': 'Turkey', 'cases': 17000000, 'deaths': 101000, 'recovered': 16900000, 'death_rate': 0.59},
            {'country': 'Spain', 'cases': 14000000, 'deaths': 120000, 'recovered': 13800000, 'death_rate': 0.86}
        ]
        
        return {
            'top_by_cases': countries[:top_n],
            'summary_stats': {
                'total_countries': 200,
                'global_cases': 700000000,
                'global_deaths': 7000000,
                'average_death_rate': 1.5
            }
        }
    
    def _get_simulated_historical_data(self, days=30):
        """generate simulated historical data"""
        dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') 
                for i in range(days, 0, -1)]
        
        data = []
        base_cases = 1000000
        for date in dates:
            new_cases = max(int(np.random.normal(50000, 20000)), 1000)
            base_cases += new_cases
            
            data.append({
                'date': date,
                'confirmed': base_cases,
                'new_cases': new_cases,
                '7day_avg_cases': new_cases + np.random.normal(0, 5000),
                'deaths': int(base_cases * 0.01),
                'new_deaths': int(new_cases * 0.01),
                '7day_avg_deaths': int(new_cases * 0.01) + np.random.normal(0, 50)
            })
        
        return data

#test the data processor
if __name__ == "__main__":
    processor = DataProcessor()
    
    print("Testing COVID-API.com data processor...")
    
    kpis = processor.get_global_kpis()
    print("Global KPIs:")
    for key, value in kpis.items():
        print(f"{key}: {value}")
    
    countries = processor.get_available_countries()
    print(f"\nAvailable countries: {len(countries)}")
    print("Sample:", countries[:5])