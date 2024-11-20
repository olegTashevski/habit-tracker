from datetime import timedelta

class Habit:

    def __init__(self, id, description, period, current_streak = 0, maximum_streak = 0):
        self.id = id
        self.description = description
        self.period = period
        self.current_streak = current_streak if current_streak is not None else 0
        self.maximum_streak = maximum_streak if maximum_streak is not None else 0
        self.checked_datetimes = []


    def __str__(self):
        return f"id:{self.id}, description : {self.description}, periodicity:{str(self.period)}, current_streak:{self.current_streak}"

    def get_last_datetime_after_period(self):
        if len(self.checked_datetimes) == 0:
            return None
        last_datetime = self.checked_datetimes[-1]
        days = self.period.days + 30 * self.period.months + 365 * self.period.years
        return last_datetime + timedelta(minutes=self.period.minutes, hours=self.period.hours,
                                                          days=days, weeks=self.period.weeks)

    def is_available(self, datetime):
        datetime_after_period = self.get_last_datetime_after_period()
        return datetime_after_period is None or datetime_after_period <= datetime

    def check_date(self, datetime):
        datetime_after_period = self.get_last_datetime_after_period()
        if (datetime_after_period is not None
                and datetime.year == datetime_after_period.year
                and datetime.month == datetime_after_period.month
                and datetime.day == datetime_after_period.day
                and datetime.hour == datetime_after_period.hour
                and datetime.minute == datetime_after_period.minute):
            self.current_streak += 1
        else:
            self.current_streak = 1

        if self.current_streak >= self.maximum_streak:
            self.maximum_streak = self.current_streak

        self.add_checked_date(datetime)

    def add_checked_date(self, date):
        self.checked_datetimes.append(date)