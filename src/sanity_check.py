from pipeline import run_pipeline

df, alerts = run_pipeline()

print(df.tail())
print(alerts.tail())