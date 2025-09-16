import pandas as pd
import numpy as np

input_file = r"C:\Users\Windows\Desktop\Portfolio\Programming\Sales Dashboard\supermarket_sales_new.csv"
output_file = r"C:\Users\Windows\Desktop\Portfolio\Programming\Sales Dashboard\Supermarket_Sales_New.csv"

df = pd.read_csv(input_file)

date_range_start = pd.to_datetime("2021-01-01")
date_range_end = pd.to_datetime("2025-12-31")

df["Date"] = pd.to_datetime(
    np.random.randint(
        date_range_start.value // 10**9,
        date_range_end.value // 10**9,
        size=len(df),
    ), unit="s"
)

df.to_csv(output_file, index=False)
print(f"File saved as {output_file} with Date column added.")
