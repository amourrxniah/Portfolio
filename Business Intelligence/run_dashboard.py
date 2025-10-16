from dashboard.app import RealTimeBIDashboard

if __name__ == "__main__":
    print("🚀 Starting Real-Time COVID-19 Dashboard...")
    print("🌍 Using live data from COVID-API.com")
    print("📊 Dashboard will open in your web browser")
    print("🔄 Data updates automatically every 5 minutes")
    print("⏳ Please wait while initializing...")
    
    dashboard = RealTimeBIDashboard()
    dashboard.run()