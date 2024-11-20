from xmlrpc.client import Fault


class Period:
    def __init__(self, minutes, hours, days, weeks, months, years, id = None):
        self.id = id
        self.minutes = minutes
        self.hours = hours
        self.days = days
        self.weeks = weeks
        self.months = months
        self.years = years

    def __str__(self):
        multiple = False
        return (f"{("" if multiple == False and (multiple := True) else " and " ) + "every " + str(self.minutes) + " minute/s" if self.minutes > 0 else ""}" +
                f"{("" if multiple == False and (multiple := True) else " and " ) + "every " + str(self.hours) + " hour/s"if self.hours > 0 else ""}" +
                f"{("" if multiple == False and (multiple := True) else " and " ) + "every " + str(self.days) + " day/s" if self.days > 0 else ""}" +
                f"{("" if multiple == False and (multiple := True) else " and " ) + "every " + str(self.weeks) + " week/s" if self.weeks > 0 else ""}" +
                f"{("" if multiple == False and (multiple := True) else " and " ) + "every " + str(self.months) + " month/s" if self.months > 0 else ""}" +
                f"{("" if multiple == False and (multiple := True) else " and " ) + "every " + str(self.years) + " year/s" if self.years > 0 else ""}")