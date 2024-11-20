import sqlite3
from datetime import datetime

from exceptions import Termination
from model.habit import Habit
from model.period import Period

HABIT_PRE_SELECT_STATMENT = """ 
                        SELECT habits.id, habits.description, periods.minutes, periods.hours,
                         periods.days, periods.weeks, periods.months, periods.years, periods.id, habits.current_streak, habits.maximum_streak"""


class Repository:
    habit_counter = 1
    period_counter = 1

    def __init__(self):
        self.connection = sqlite3.connect(":memory:")
        cursor = self.connection.cursor()
        cursor.execute("""
                    CREATE TABLE IF NOT EXISTS periods (
                        id INTEGER PRIMARY KEY,
                        minutes INTEGER,
                        hours INTEGER,
                        days INTEGER,
                        weeks INTEGER,
                        months INTEGER,
                        years INTEGER
                    )
                """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY,
                period_id INTEGER references pariods(id),
                description TEXT,
                current_streak INTEGER,
                maximum_streak INTEGER
            )
        """)

        cursor.execute("""
                    CREATE TABLE IF NOT EXISTS checked_dates (
                        datetime DATETIME,
                        habit_id INTEGER references habits(id)
                    )
                """)

    def execute_query(self, query, args, termination_handler, result_handler):
        cursor = self.connection.cursor()
        cursor.execute(query.format(*args))
        rows = cursor.fetchall()
        if termination_handler(rows):
            raise Termination("Corrupt data, session terminated")
        else:
            return result_handler(rows)

    def execute_update(self, query, args):
        cursor = self.connection.cursor()
        cursor.execute(query.format(*args))
        self.connection.commit()

    def termination_uniqueness_handler(self, rows):
        return len(rows) > 1

    def result_uniqueness_handler(self, rows):
        return len(rows) == 1

    def habit_exists(self, description, period_input):
        query = """
                    SELECT habits.id FROM habits, periods
                     WHERE habits.description = "{}"
                     AND periods.minutes = {}
                     AND periods.hours = {}
                     AND periods.days = {}
                     AND periods.weeks = {}
                     AND periods.months = {}
                     AND periods.years = {}
                     AND habits.period_id = periods.id"""
        args = (description, *period_input)
        return self.execute_query(query, args, self.termination_uniqueness_handler, self.result_uniqueness_handler)

    def get_period_id(self, period_input):
        query = """
                    SELECT periods.id FROM periods
                        WHERE periods.minutes = {}
                        AND periods.hours = {}
                        AND periods.days = {}
                        AND periods.weeks = {}
                        AND periods.months = {}
                        AND periods.years = {}"""
        result_handler = lambda rows : None if len(rows) == 0 else rows[0][0]
        return self.execute_query(query, period_input, self.termination_uniqueness_handler,
                                  result_handler)

    def create_period(self, period_input):
        query = """ 
        INSERT INTO periods VALUES ({}, {}, {}, {}, {}, {}, {}) """
        args = (self.period_counter, *period_input)
        self.execute_update(query, args)
        self.period_counter += 1
        return self.period_counter - 1

    def create_habit(self, description, period_id):
        query = """ 
                INSERT INTO habits (id, description, period_id) VALUES ({}, "{}", {}) """
        args = (self.habit_counter, description, period_id)
        self.execute_update(query, args)
        self.habit_counter += 1
        return self.habit_counter - 1

    def get_habits(self, period_id = 0):
        period_param = ""
        include_period_param = period_id != 0
        if include_period_param:
            period_param = " WHERE periods.id = {} "

        query = (HABIT_PRE_SELECT_STATMENT +
                 ", checked_dates.datetime FROM habits LEFT JOIN checked_dates ON checked_dates.habit_id = habits.id " +
                 "INNER JOIN periods ON periods.id = habits.period_id" + period_param
                 + " ORDER BY habits.id, checked_dates.datetime")
        args = (period_id,) if include_period_param else ()
        return self.to_habit_objects(query, args)

    def to_habit_objects(self, query, args):
        habits = []
        created_habit_ids = set()
        habit_temp = None
        temination_never_handler = lambda rows: False
        result_handler = lambda rows: rows
        rows = self.execute_query(query, args, temination_never_handler, result_handler)
        for row in rows:
            if row[0] not in created_habit_ids:
                habit_temp = Habit(row[0], row[1],
                                   Period(row[2], row[3], row[4], row[5], row[6], row[7], row[8]), row[9], row[10])
                habits.append(habit_temp)
                created_habit_ids.add(row[0])
            if len(row) == 12 and row[11] is not None:
                habit_temp.add_checked_date(datetime.fromisoformat(row[11]))
        return habits

    def get_all_habits(self):
        return self.get_habits()

    def add_date(self, habit_id, datetime):
        query = """ INSERT INTO checked_dates VALUES ("{}", {}) """
        args = (datetime, habit_id)
        self.execute_update(query, args)

    def save_habit(self, habit):
        query = """ UPDATE habits SET period_id = {}, description = "{}", current_streak = {}, maximum_streak = {} WHERE id = {} """
        args = (habit.period.id, habit.description, habit.current_streak, habit.maximum_streak, habit.id)
        self.execute_update(query, args)

    def delete_habit(self, habit_id):
        query = """ DELETE FROM habits WHERE id = {} """
        args = (habit_id,)
        self.execute_update(query, args)

    def get_all_habits_by_period_id(self, period_id):
        return self.get_habits(period_id)

    def get_habits_biggest_run_streak(self):
        query = (HABIT_PRE_SELECT_STATMENT +
                 """ FROM habits, periods WHERE habits.period_id = periods.id
                  AND habits.maximum_streak = (SELECT MAX(habits.maximum_streak) FROM habits)""")
        return self.to_habit_objects(query, ())

    def close_connection(self):
        self.connection.close()