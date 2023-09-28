from datetime import datetime

def get_schedule_date_key(exact_date:datetime) -> str:
    return f"{exact_date.year}_{exact_date.month}_{exact_date.day}_{exact_date.hour}"