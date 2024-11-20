from exceptions import HabitExist, NoEntityExist
from model.period import Period


class Service:
    def __init__(self, repository):
        self.repository = repository

    def get_habits_ids(self, habits):
        habit_ids = set()
        for habit in habits:
            habit_ids.add(habit.id)
        return habit_ids

    def max_day_of_month(self, year, month):
        if month == 2:
            is_leap = (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0))
            if is_leap:
                return 29
            else:
                return 28
        else:
            days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            return days_in_month[month - 1]

    def print_habits(self, habits):
        if len(habits) == 0:
            raise NoEntityExist("The are no habits")
        for habit in habits:
            print(habit)

    def find_habit_by_id(self, id, habits):
        habit = next((habit for habit in habits if habit.id == id), None)
        if habit is None:
            raise NoEntityExist("The habit with id " + str(id) + " does not exist in the provided habits")

        return habit

    def validate_number_input(self, option_input,
                              valid_inputs):
        return option_input.isdigit() and int(option_input) in valid_inputs

    def create_habit(self, period_input, description):
        if self.repository.habit_exists(description, period_input):
            raise HabitExist("the habit already exists")

        period_id = self.get_period_id(period_input)
        return self.repository.create_habit(description, period_id)

    def get_period_id(self, period_input):
        period_id = self.repository.get_period_id(period_input)
        if period_id is None:
            return self.repository.create_period(period_input)
        else:
            return period_id

    def print_available_habits(self, datetime):
        habits = set()
        for habit in self.repository.get_all_habits():
            if habit.is_available(datetime):
                habits.add(habit)
                print(habit)
        if len(habits) == 0:
            raise NoEntityExist("there aren't any habits available to be checked with the date and time:" + str(datetime))

        return habits

    def check_habit(self, habit_id, habits, datetime):
        habit = None
        for habit_temp in habits:
            if habit_temp.id == habit_id:
                habit = habit_temp
                break
        habit.check_date(datetime)
        self.repository.add_date(habit_id, datetime)
        self.repository.save_habit(habit)

    def print_all_habits(self):
        habits = self.repository.get_all_habits()
        self.print_habits(habits)
        return habits

    def print_habits_by_period(self, period_input):
        period_id = self.repository.get_period_id(period_input)
        if period_id is None:
            raise NoEntityExist("no habits exists with that period")
        habits = self.repository.get_all_habits_by_period_id(period_id)
        self.print_habits(habits)
        return habits

    def print_habits_with_biggest_run_streak(self):
        self.print_habits(self.repository.get_habits_biggest_run_streak())

    def edit_habit(self, habit, new_description, period_input):
        period_id = self.get_period_id(period_input)
        habit.period = Period(*period_input, period_id)
        habit.description = new_description
        self.repository.save_habit(habit)

    def delete_habit(self, habit):
        self.repository.delete_habit(habit.id)

    def close_connection(self):
        self.repository.close_connection()