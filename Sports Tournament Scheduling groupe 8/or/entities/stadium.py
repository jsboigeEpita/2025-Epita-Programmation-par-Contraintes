from datetime import datetime, timedelta

class Stadium:
    def __init__(self, name, unavailable_dates=None):
        self.name = name
        self.unavailable_dates = set()
        if unavailable_dates:
            for date in unavailable_dates:
                if isinstance(date, str):
                    self.unavailable_dates.add(datetime.fromisoformat(date).date())
                elif isinstance(date, datetime):
                    self.unavailable_dates.add(date.date())
                else:
                    try:
                        self.unavailable_dates.add(date)
                    except:
                        pass

    def is_available_on(self, date):
        d = date.date() if isinstance(date, datetime) else date
        return d not in self.unavailable_dates