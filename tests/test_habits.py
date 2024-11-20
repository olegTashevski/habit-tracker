import unittest
from datetime import datetime, timedelta
from model.period import Period
from model.habit import Habit
from service import Service
from repository import Repository
from exceptions import HabitExist, NoEntityExist, Termination


class TestPeriod(unittest.TestCase):
    def setUp(self):
        self.period = Period(30, 1, 0, 0, 0, 0)  # 30 minutes, 1 hour

    def test_period_initialization(self):
        self.assertEqual(self.period.minutes, 30)
        self.assertEqual(self.period.hours, 1)
        self.assertEqual(self.period.days, 0)

    def test_period_string_representation(self):
        self.assertIn("every 30 minute/s", str(self.period))
        self.assertIn(" and every 1 hour/s", str(self.period))


class TestHabit(unittest.TestCase):
    def setUp(self):
        self.period = Period(0, 0, 1, 0, 0, 0)  # Daily
        self.habit = Habit(1, "Exercise daily", self.period)

    def test_habit_initialization(self):
        self.assertEqual(self.habit.id, 1)
        self.assertEqual(self.habit.description, "Exercise daily")
        self.assertEqual(self.habit.current_streak, 0)
        self.assertEqual(self.habit.maximum_streak, 0)

    def test_check_date(self):
        current_time = datetime.now()
        self.habit.check_date(current_time)
        self.assertEqual(self.habit.current_streak, 1)
        self.assertEqual(self.habit.maximum_streak, 1)

    def test_is_available(self):
        current_time = datetime.now()
        self.assertTrue(self.habit.is_available(current_time))

        # Add a check date
        self.habit.check_date(current_time)

        # Should not be available immediately after check
        self.assertFalse(self.habit.is_available(current_time))

        # Should be available after period
        future_time = current_time + timedelta(days=1, minutes=1)
        self.assertTrue(self.habit.is_available(future_time))


class TestService(unittest.TestCase):
    def setUp(self):
        self.repository = Repository()
        self.service = Service(self.repository)

    def test_validate_number_input(self):
        self.assertTrue(self.service.validate_number_input("1", range(0, 5)))
        self.assertFalse(self.service.validate_number_input("abc", range(0, 5)))
        self.assertFalse(self.service.validate_number_input("6", range(0, 5)))

    def test_max_day_of_month(self):
        self.assertEqual(self.service.max_day_of_month(2023, 2), 28)  # February non-leap year
        self.assertEqual(self.service.max_day_of_month(2024, 2), 29)  # February leap year
        self.assertEqual(self.service.max_day_of_month(2023, 1), 31)  # January

    def test_create_habit(self):
        period_input = (0, 0, 1, 0, 0, 0)  # Daily
        description = "Test Habit"

        # First creation should succeed
        self.service.create_habit(period_input, description)

        # Second creation with same parameters should raise HabitExist
        with self.assertRaises(HabitExist):
            self.service.create_habit(period_input, description)

    def tearDown(self):
        self.service.close_connection()


class TestRepository(unittest.TestCase):
    def setUp(self):
        self.repository = Repository()

    def test_create_period(self):
        period_input = (30, 1, 0, 0, 0, 0)
        period_id = self.repository.create_period(period_input)
        self.assertIsNotNone(period_id)

    def test_create_habit(self):
        period_input = (30, 1, 0, 0, 0, 0)
        period_id = self.repository.create_period(period_input)
        habit_id = self.repository.create_habit("Test Habit", period_id)
        self.assertIsNotNone(habit_id)

    def test_get_all_habits(self):
        habits = self.repository.get_all_habits()
        self.assertIsInstance(habits, list)

    def tearDown(self):
        self.repository.close_connection()


if __name__ == '__main__':
    unittest.main()