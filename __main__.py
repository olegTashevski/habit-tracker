import logging
from model.period import Period
from model.habit import Habit
from service import Service
from repository import Repository
from exceptions import Termination
from exceptions import BackExc
from exceptions import NoEntityExist

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()])
logger = logging.getLogger("MyLogger")
from datetime import datetime, timedelta


class Main:
    def __init__(self, service):
        self.service = service

    def get_user_period_option(self):
        print("Choose a periodicity")
        base = "Enter {} for a{} periodicity{}"
        evr = " of every "
        args = [["", evr + "minute"],["", evr + "hour"], ["", evr + "day"], ["", evr + "week"],
                ["", evr + "month"], ["", evr + "year"], [" custom", ""]]
        for i in range(0, 7):
            print(base.format(i, *args[i]))

        print("Enter 7 to go back")
        return input()

    def get_part_input(self, question: str, valid_inputs):
        while True:
            period_input = input(question)
            if self.service.validate_number_input(period_input, valid_inputs):
                return int(period_input)
            else:
                print("Bad input try again")

    def get_user_custom_period(self):
        base = "Can you please enter from 0 to {} {}"
        args = [[59, "minutes"], [23, "hours"], [6, "days"], [3, "weeks"], [11, "months"], [10, "years"]]
        custom_period = []
        for i in range(0, len(args)):
            custom_period.append(self.get_part_input(base.format( *args[i]), range(0, args[i][0] + 1)))
        return tuple(custom_period)

    def handle_period_option(self, option):
        period_input = [0, 0, 0, 0, 0, 0]
        if option == 6:
            period_input = self.get_user_custom_period()
        elif option != 7:
            period_input[option] = 1
            period_input = tuple(period_input)
        else:
            raise BackExc("You've gone back. Pick an another action")
        return period_input

    def get_period_input(self):
        return self.handle_input_option(self.get_user_period_option,
                                        self.handle_period_option, 0, 8)

    def create_habit(self):
        period_input = self.get_period_input()
        description = input("Please describe your new habit")
        self.service.create_habit(period_input, description)

    def handle_date_option(self, option_number: int):
        now = datetime.now()
        if option_number == 0:
            return now
        elif option_number == 2:
            raise BackExc("you have gone back")
        else:
            year = self.get_part_input("Enter the year", range(0, now.year + 2))
            is_current = datetime.now().year == year
            max_month = now.month if is_current else 12
            month = self.get_part_input("Can you please enter the month", range(0, max_month + 2))
            is_current = month == now.month and is_current

            max_day = now.day if is_current else self.service.max_day_of_month(year, month)
            day = self.get_part_input("Can you please enter the day", range(0, max_day + 2))
            is_current = is_current and day == now.day
            max_hour = now.hour if is_current else 23
            hour = self.get_part_input("Can you please enter the hour", range(0, max_hour + 2))
            is_current = is_current and hour == now.hour
            max_minute = now.minute if is_current else 59
            minute = self.get_part_input("Can you please enter the minutes", range(0, max_minute + 2))
            return datetime(year, month, day, hour, minute)

    def check_habit(self):
        question = "Enter 0 to use the current date and time or 1 to choose another or 2 to go back"
        date_input_option_getter = lambda : input(question)
        date = self.handle_input_option(date_input_option_getter,
                                        self.handle_date_option, 0, 3)
        habits = self.service.print_available_habits(date)
        habit_id = self.get_part_input("Enter the id of the habit to check it", self.service.get_habits_ids(habits))
        self.service.check_habit(habit_id, habits, date)


    def get_all_habits(self):
        self.service.print_all_habits()

    def get_all_habits_by_period(self):
        period_input = self.get_period_input()
        self.service.print_habits_by_period(period_input)

    def get_habits_biggest_run_streak(self):
        print("the habits with the biggest run streak are")
        self.service.print_habits_with_biggest_run_streak()

    def get_habit(self, question_part):
        habits = self.service.print_all_habits()
        valid_inputs = self.service.get_habits_ids(habits)
        valid_inputs.add(0)
        id = self.get_part_input("Enter the habit's id to " + question_part + " or 0 to go back",
                                 valid_inputs)
        if id == 0:
            raise BackExc("you have gone back")

        return service.find_habit_by_id(id, habits)

    def get_habit_run_streak(self):
        habit = self.get_habit("get his longest run streak")
        print("The longest run streak of the habit " + str(habit) + " is " + str(habit.maximum_streak))

    def edit_habit(self):
        habit = self.get_habit("edit it")
        new_description = input("Please enter the new description")
        period_input = self.get_period_input()
        service.edit_habit(habit, new_description, period_input)

    def delete_habit(self):
        habit = self.get_habit("delete it")
        service.delete_habit(habit)

    def handle_option(self, option_number: int):
        try:
            if option_number == 0:
                self.create_habit()
            elif option_number == 1:
                self.check_habit()
            elif option_number == 2:
                self.get_all_habits()
            elif option_number == 3:
                self.get_all_habits_by_period()
            elif option_number == 4:
                self.get_habits_biggest_run_streak()
            elif option_number == 5:
                self.get_habit_run_streak()
            elif option_number == 6:
                self.edit_habit()
            elif option_number == 7:
                self.delete_habit()
            else:
                raise Termination("Terminated")
        except (NoEntityExist, BackExc) as exc:
            print(exc.message)

    def get_user_option(self):
        print("What actions do you want to take?")
        print("Enter 0 for Option 1:Creating a new Habit")
        print("Enter 1 for Option 2:Checking an existing Habit")
        print("Enter 2 for Option 3:Getting all existing Habits")
        print("Enter 3 for Option 4:Getting all existing Habits by particular Period")
        print("Enter 4 for Option 5:Getting the habit with the longest run streak")
        print("Enter 5 for Option 6:Getting the longest run streak of a particular habit")
        print("Enter 6 for Option 7:editing a particular habit")
        print("Enter 7 for Option 8:deleting a particular habit")
        print("Enter 8 for termination")
        return input()

    def handle_input_option(self, option_input_getter, handler,
                            min_option, max_option):
        while True:
            option_input = option_input_getter()
            if self.service.validate_number_input(option_input,
                                              range(min_option, max_option)):
                return handler(int(option_input))
            else:
                logger.warning("Wrong option number entered")
                print("Please try again")

    def main(self):
        while True:
            try:
                self.handle_input_option(self.get_user_option, self.handle_option, 0, 9)
            except Termination as term:
                print(term.message)
                self.service.close_connection()
                break


repo = Repository()
service = Service(repo)
main = Main(service)

weekly_period_input = (0, 0, 0, 1, 0, 0)
daily_period_input = (0, 0, 1, 0, 0, 0)

habit_weekly_1  = service.create_habit(weekly_period_input, "Predefined Weekly 1")
habit_daily_1 = service.create_habit(daily_period_input, "Predefined Daily 1")
habit_weekly_2  = service.create_habit(weekly_period_input, "Predefined Weekly 2")
habit_daily_2 = service.create_habit(daily_period_input, "Predefined Daily 2")

habit_weekly_3  = service.create_habit(weekly_period_input, "Predefined Weekly 3")
habit_daily_3 = service.create_habit(daily_period_input, "Predefined Daily 3")

now = datetime.now()
habits  = service.print_available_habits(now)
service.check_habit(habit_weekly_3, habits, now)
service.check_habit(habit_daily_3, habits, now)

for i in range(3, -1, -1):
    service.check_habit(habit_weekly_1, habits, now - timedelta(weeks=i))
    if (i % 2) != 0:
        service.check_habit(habit_weekly_2, habits, now - timedelta(weeks=i))

for i in range(27, -1, -1):
    service.check_habit(habit_daily_1, habits, now - timedelta(days=i))
    if (i % 2) != 0:
        service.check_habit(habit_daily_2, habits, now - timedelta(days=i))

main.main()



