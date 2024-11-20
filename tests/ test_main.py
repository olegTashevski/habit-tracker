import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from service import Service
from repository import Repository
from exceptions import BackExc, Termination, NoEntityExist
from __main__ import Main


class TestMain(unittest.TestCase):
    def setUp(self):
        self.repository = Repository()
        self.service = Service(self.repository)
        self.main = Main(self.service)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_get_user_period_option(self, mock_print, mock_input):
        # Test normal input
        mock_input.return_value = "1"
        result = self.main.get_user_period_option()
        self.assertEqual(result, "1")

        # Verify proper printing of options
        self.assertTrue(mock_print.called)

    @patch('builtins.input')
    def test_get_part_input(self, mock_input):
        # Test valid input
        mock_input.return_value = "5"
        result = self.main.get_part_input("Enter number:", range(0, 10))
        self.assertEqual(result, 5)

        # Test invalid input followed by valid input
        mock_input.side_effect = ["abc", "5"]
        result = self.main.get_part_input("Enter number:", range(0, 10))
        self.assertEqual(result, 5)

    def test_handle_period_option(self):
        # Test standard period option
        result = self.main.handle_period_option(1)
        self.assertEqual(result, (0, 1, 0, 0, 0, 0))

        # Test back option
        with self.assertRaises(BackExc):
            self.main.handle_period_option(7)

    @patch('builtins.input')
    def test_get_user_custom_period(self, mock_input):
        # Simulate user entering all zeros
        mock_input.side_effect = ["0", "0", "0", "0", "0", "0"]
        result = self.main.get_user_custom_period()
        self.assertEqual(result, (0, 0, 0, 0, 0, 0))

    @patch('builtins.input')
    @patch('builtins.print')
    def test_create_habit(self, mock_print, mock_input):
        # Test creating a new habit
        mock_input.side_effect = ["1", "Test Habit"]  # Period option 1 (hourly) and description
        self.main.create_habit()
        # Verify habit was created
        habits = self.service.repository.get_all_habits()
        self.assertTrue(any(h.description == "Test Habit" for h in habits))

    @patch('builtins.input')
    def test_handle_date_option(self, mock_input):
        # Test current date option
        result = self.main.handle_date_option(0)
        self.assertIsInstance(result, datetime)

        # Test back option
        with self.assertRaises(BackExc):
            self.main.handle_date_option(2)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_check_habit(self, mock_print, mock_input):
        # First create a habit
        period_input = (0, 1, 0, 0, 0, 0)  # hourly
        self.service.create_habit(period_input, "Test Habit")

        # Test checking the habit
        mock_input.side_effect = ["0", "1"]  # Use current time and select first habit
        self.main.check_habit()

    @patch('builtins.input')
    def test_get_user_option(self, mock_input):
        # Test valid option
        mock_input.return_value = "1"
        result = self.main.get_user_option()
        self.assertEqual(result, "1")

    @patch('builtins.input')
    @patch('builtins.print')
    def test_main_loop(self, mock_print, mock_input):
        # Test normal termination
        mock_input.return_value = "6"
        self.main.main()

        # Test operation and then termination
        mock_input.side_effect = ["2", "6"]  # Get all habits, then terminate
        self.main.main()

    def test_handle_option(self):
        # Test termination option
        with self.assertRaises(Termination):
            self.main.handle_option(6)

        # Test invalid option
        with self.assertRaises(Termination):
            self.main.handle_option(7)

    def test_handle_input_option(self):
        # Test valid input
        result = self.main.handle_input_option("1", lambda x: x * 2, 0, 5)
        self.assertEqual(result, 2)

        # Test invalid input
        result = self.main.handle_input_option("invalid", lambda x: x * 2, 0, 5)
        self.assertIsNone(result)

    def tearDown(self):
        self.service.close_connection()


class TestMainIntegration(unittest.TestCase):
    def setUp(self):
        self.repository = Repository()
        self.service = Service(self.repository)
        self.main = Main(self.service)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_full_habit_workflow(self, mock_print, mock_input):
        # Simulate complete workflow: Create habit -> Check habit -> View habits -> Exit
        mock_input.side_effect = [
            "0",  # Create hourly habit
            "1",  # Hourly period
            "Test Habit Hourly", # Habit description
            "0",  # create daily habit
            "2",  # daily period
            "Test Habit Daily",  # Habit description
            "0",  # create weekly habit
            "3",  # weekly period
            "Test Habit Weekly",  # Habit description
            "0",  # create second weekly habit
            "3",  # weekly period
            "Test Habit Weekly2",  # Habit description
            "0",  # create monthly habit that you will convert to yearly
            "4"   # monthly period
            "Montly to be editted"
            "0",  # create third weekly habit To delete
            "3",  # weekly period
            "Test Habit WeeklyToDelete",  # Habit description
            "1",  # check habit hourly
            "0",  # Use current time
            "1",  # Select first habit
            "6"   # Edit the monthly habit
            "Test Habit Yearly" # Habit description
            "5"   # yearly period
            "8"   # Exit
        ]

        self.main.main()

        # Verify habit were created, and that one was checked, one was edited and one was delted
        habits = self.service.repository.get_all_habits()
        self.assertTrue(len(habits) == 5)
        test_habit1 = next((h for h in habits if h.id == 1), None)
        self.assertTrue(test_habit1.description == "Test Habit Hourly")
        self.assertIsNotNone(test_habit1)
        self.assertTrue(len(test_habit1.checked_datetimes) == 1)
        test_habit2 = next((h for h in habits if h.id == 5), None)
        self.assertTrue(test_habit2.description == "Test Habit Yearly")
        #verify that there are two weekly habits
        habits_weekly = self.service.print_habits_by_period((0, 0, 0, 1, 0, 0))
        self.assertTrue(len(habits) == 2)

        # verify that the longest runstreak is from the hourly habit
        longest_run_streak_habits = self.service.repository.get_habits_biggest_run_streak()
        self.assertTrue(test_habit1.description == longest_run_streak_habits[0].description)
        self.assertTrue(len(longest_run_streak_habits) == 1)

    def tearDown(self):
        self.service.close_connection()


if __name__ == '__main__':
    unittest.main()