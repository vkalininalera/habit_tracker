# tests_
import datetime
import unittest
from sqlite3 import IntegrityError

from Project_Habit_Tracker.tracker import HabitTracker
import random
import string

tracker_instance = HabitTracker()


def generate_random_string(length):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))


class TestHabitTracker(unittest.TestCase):

    def setUp(self) -> None:
        self.habit_name = generate_random_string(8)
        self.valid_habit_periodicity = 'daily'
        tracker_instance.conn.execute('DELETE FROM habits_table')
        tracker_instance.conn.execute('DELETE FROM check_off_table')
        tracker_instance.conn.commit()

    def test_add_nonexistent_habit_successfully(self):
        # execution
        tracker_instance.add_habit(self.habit_name, self.valid_habit_periodicity)

        # check
        found_habits = tracker_instance.conn.execute('SELECT count(*) FROM habits_table WHERE name = ?',
                                                     (self.habit_name,)).fetchone()
        self.assertEqual(1, found_habits[0])

    def test_existed_habit_is_not_added_to_db(self):
        tracker_instance.add_habit(self.habit_name, 'daily')
        tracker_instance.add_habit(self.habit_name, 'weekly')

        found_habits = tracker_instance.conn.execute('SELECT periodicity FROM habits_table WHERE name = ?',
                                                     (self.habit_name,)).fetchone()
        self.assertEqual('daily', found_habits[0])

    def test_add_daily_nonexistent_periodicity(self):
        habit_periodicity = "daily"
        tracker_instance.add_habit(self.habit_name, habit_periodicity)
        found_habits = tracker_instance.conn.execute('SELECT count(*) FROM habits_table WHERE name = ?',
                                                     (self.habit_name,)).fetchone()
        self.assertEqual(1, found_habits[0])

    def test_add_weekly_nonexistent_periodicity(self):
        habit_periodicity = "weekly"
        tracker_instance.add_habit(self.habit_name, habit_periodicity)
        found_habits = tracker_instance.conn.execute('SELECT count(*) FROM habits_table WHERE name = ?',
                                                     (self.habit_name,)).fetchone()
        self.assertEqual(1, found_habits[0])

    def test_add_incorrect_periodicity(self):
        habit_periodicity = "yearly"
        self.assertRaises(IntegrityError, lambda: tracker_instance.add_habit(self.habit_name, habit_periodicity))

    def test_existed_habit_is_deleted(self):
        tracker_instance.add_habit(self.habit_name, self.valid_habit_periodicity)

        tracker_instance.delete_habit(self.habit_name)
        found_habits = tracker_instance.conn.execute('SELECT count(*) FROM habits_table WHERE name = ?',
                                                     (self.habit_name,)).fetchone()
        self.assertEqual(0, found_habits[0])

    def test_nothing_happened_when_delete_nonexisted_habit(self):
        actual_result = tracker_instance.delete_habit('something that doest exist')
        self.assertIsNone(actual_result)

    def test_habit_deletion_successful(self):
        tracker_instance.add_habit(self.habit_name, self.valid_habit_periodicity)

        tracker_instance.delete_habit(self.habit_name)

        found_habits = tracker_instance.conn.execute('SELECT count(*) FROM habits_table WHERE name = ?',
                                                     (self.habit_name,)).fetchone()
        self.assertEqual(0, found_habits[0])

    def test_change_name_for_existed_habit(self):
        tracker_instance.add_habit(self.habit_name, self.valid_habit_periodicity)

        new_name = generate_random_string(8)
        tracker_instance.change_name(self.habit_name, new_name)

        found_habits = tracker_instance.conn.execute('SELECT count(*) FROM habits_table WHERE name = ?',
                                                     (new_name,)).fetchone()
        self.assertEqual(1, found_habits[0])

    def test_change_periodicity_for_existed_habit(self):
        periodicity = 'daily'
        tracker_instance.add_habit(self.habit_name, periodicity)

        new_periodicity = 'weekly'
        tracker_instance.change_periodicity(self.habit_name, new_periodicity)

        found_habits = tracker_instance.conn.execute(
            'SELECT count(*) FROM habits_table WHERE name = ? AND periodicity = ?',
            (self.habit_name, new_periodicity)).fetchone()
        self.assertEqual(1, found_habits[0])

    def test_check_off_daily_successful(self):
        habit_id = tracker_instance.add_habit(self.habit_name, 'daily')

        tracker_instance.check_off(self.habit_name)

        check_off = tracker_instance.conn.execute('SELECT * FROM check_off_table WHERE habit_id = ?',
                                                  (habit_id,)).fetchone()
        actual_check_off_date = check_off[2]
        expected = datetime.date.today().strftime('%Y-%m-%d')
        current_streak = tracker_instance.conn.execute('SELECT current_streak FROM habits_table WHERE habit_id = ?',
                                                       (habit_id,)).fetchone()

        self.assertEqual(actual_check_off_date, expected)
        self.assertEqual(current_streak[0], 1)

    def test_check_off_weekly_successful(self):
        habit_id = tracker_instance.add_habit(self.habit_name, 'weekly')

        tracker_instance.check_off(self.habit_name)

        check_off = tracker_instance.conn.execute('SELECT * FROM check_off_table WHERE habit_id = ?',
                                                  (habit_id,)).fetchone()
        actual_check_off_date = check_off[2]
        expected = datetime.date.today().strftime('%Y-%m-%d')
        current_streak = tracker_instance.conn.execute('SELECT current_streak FROM habits_table WHERE habit_id = ?',
                                                       (habit_id,)).fetchone()

        self.assertEqual(actual_check_off_date, expected)
        self.assertEqual(current_streak[0], 1)

    def test_two_daily_check_offs(self):
        habit_id = tracker_instance.add_habit(self.habit_name, 'daily')

        tracker_instance.check_off(self.habit_name)

        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        yesterday_str = yesterday.strftime('%Y-%m-%d')
        tracker_instance.conn.execute('UPDATE check_off_table SET date = ? WHERE habit_id = ?',
                                      (yesterday_str, habit_id))

        tracker_instance.check_off(self.habit_name)

        check_offs = tracker_instance.conn.execute('SELECT date FROM check_off_table WHERE habit_id = ?',
                                                   (habit_id,)).fetchall()
        # [('26-06-2023', ), ('27-06-2023', )] -> ['26-06-2023', '27-06-2023']
        actual_dates = sorted(map(lambda x: x[0], check_offs))

        expected_dates = sorted([datetime.date.today().strftime('%Y-%m-%d'), yesterday_str])

        self.assertEqual(actual_dates, expected_dates)

    def test_two_weekly_check_offs(self):
        habit_id = tracker_instance.add_habit(self.habit_name, 'weekly')

        tracker_instance.check_off(self.habit_name)

        today = datetime.date.today()
        eight_days_ago = today - datetime.timedelta(weeks=1) - datetime.timedelta(days=1)
        eight_days_ago_str = eight_days_ago.strftime('%Y-%m-%d')
        tracker_instance.conn.execute('UPDATE check_off_table SET date = ? WHERE habit_id = ?',
                                      (eight_days_ago_str, habit_id))

        tracker_instance.check_off(self.habit_name)

        check_offs = tracker_instance.conn.execute('SELECT date FROM check_off_table WHERE habit_id = ?',
                                                   (habit_id,)).fetchall()
        actual_dates = sorted(map(lambda x: x[0], check_offs))

        expected_dates = sorted([datetime.date.today().strftime('%Y-%m-%d'), eight_days_ago_str])

        self.assertEqual(actual_dates, expected_dates)

    def test_check_off_nonexisted_habit(self):
        actual_result = tracker_instance.check_off(self.habit_name)

        check_offs = tracker_instance.conn.execute('SELECT count(*) FROM check_off_table').fetchone()

        self.assertEqual(actual_result, None)
        self.assertEqual(0, check_offs[0])

    def test_check_off_already_checked_daily(self):
        habit_id = tracker_instance.add_habit(self.habit_name, 'daily')

        tracker_instance.check_off(self.habit_name)
        tracker_instance.check_off(self.habit_name)

        check_offs = tracker_instance.conn.execute('SELECT date FROM check_off_table WHERE habit_id = ?',
                                                   (habit_id,)).fetchall()
        # [('26-06-2023', ), ('27-06-2023', )] -> ['26-06-2023', '27-06-2023']
        actual_dates = list(map(lambda x: x[0], check_offs))

        expected_dates = [datetime.date.today().strftime('%Y-%m-%d')]

        self.assertEqual(actual_dates, expected_dates)

    def test_check_off_already_checked_weekly(self):
        habit_id = tracker_instance.add_habit(self.habit_name, 'weekly')

        tracker_instance.check_off(self.habit_name)

        today = datetime.date.today()
        three_days_ago = today - datetime.timedelta(days=3)
        three_days_ago_str = three_days_ago.strftime('%Y-%m-%d')
        tracker_instance.conn.execute('UPDATE check_off_table SET date = ? WHERE habit_id = ?',
                                      (three_days_ago_str, habit_id))

        tracker_instance.check_off(self.habit_name)

        check_offs = tracker_instance.conn.execute('SELECT date FROM check_off_table WHERE habit_id = ?',
                                                   (habit_id,)).fetchall()
        actual_dates = list(map(lambda x: x[0], check_offs))

        expected_dates = [three_days_ago_str]

        self.assertEqual(actual_dates, expected_dates)

    def test_check_off_breaking_habit_daily(self):
        habit_id = tracker_instance.add_habit(self.habit_name, 'weekly')

        tracker_instance.check_off(self.habit_name)

        today = datetime.date.today()
        fifteen_days_ago = today - datetime.timedelta(weeks=2) - datetime.timedelta(days=1)
        fifteen_days_ago_str = fifteen_days_ago.strftime('%Y-%m-%d')
        tracker_instance.conn.execute('UPDATE check_off_table SET date = ? WHERE habit_id = ?',
                                      (fifteen_days_ago_str, habit_id))

        tracker_instance.check_off(self.habit_name)

        check_offs = tracker_instance.conn.execute('SELECT date FROM check_off_table WHERE habit_id = ?',
                                                   (habit_id,)).fetchall()
        actual_dates = list(map(lambda x: x[0], check_offs))
        current_streak = tracker_instance.conn.execute('SELECT current_streak FROM habits_table WHERE habit_id = ?',
                                                       (habit_id,)).fetchone()

        expected_dates = sorted([datetime.date.today().strftime('%Y-%m-%d'), fifteen_days_ago_str])

        self.assertEqual(expected_dates, actual_dates)
        self.assertEqual(1, current_streak[0])

    def test_check_off_breaking_habit_weekly(self):
        habit_id = tracker_instance.add_habit(self.habit_name, 'daily')

        tracker_instance.check_off(self.habit_name)

        today = datetime.date.today()
        two_days_ago = today - datetime.timedelta(days=2)
        two_days_ago_str = two_days_ago.strftime('%Y-%m-%d')
        tracker_instance.conn.execute('UPDATE check_off_table SET date = ? WHERE habit_id = ?',
                                      (two_days_ago_str, habit_id))

        tracker_instance.check_off(self.habit_name)

        check_offs = tracker_instance.conn.execute('SELECT date FROM check_off_table WHERE habit_id = ?',
                                                   (habit_id,)).fetchall()
        actual_dates = list(map(lambda x: x[0], check_offs))
        current_streak = tracker_instance.conn.execute('SELECT current_streak FROM habits_table WHERE habit_id = ?',
                                                       (habit_id,)).fetchone()

        expected_dates = sorted([datetime.date.today().strftime('%Y-%m-%d'), two_days_ago_str])

        self.assertEqual(actual_dates, expected_dates)
        self.assertEqual(1, current_streak[0])

    def test_check_off_on_streak_daily(self):
        habit_id = tracker_instance.add_habit(self.habit_name, 'daily')

        tracker_instance.check_off(self.habit_name)

        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        yesterday_str = yesterday.strftime('%Y-%m-%d')
        tracker_instance.conn.execute('UPDATE check_off_table SET date = ? WHERE habit_id = ?',
                                      (yesterday_str, habit_id))

        tracker_instance.check_off(self.habit_name)

        current_streak = tracker_instance.conn.execute('SELECT current_streak FROM habits_table WHERE habit_id = ?',
                                                       (habit_id,)).fetchone()

        self.assertEqual(2, current_streak[0])

    def test_check_off_on_streak_weekly(self):
        habit_id = tracker_instance.add_habit(self.habit_name, 'weekly')

        tracker_instance.check_off(self.habit_name)

        today = datetime.date.today()
        eight_days_ago = today - datetime.timedelta(weeks=1) - datetime.timedelta(days=1)
        eight_days_ago_str = eight_days_ago.strftime('%Y-%m-%d')
        tracker_instance.conn.execute('UPDATE check_off_table SET date = ? WHERE habit_id = ?',
                                      (eight_days_ago_str, habit_id))

        tracker_instance.check_off(self.habit_name)

        current_streak = tracker_instance.conn.execute('SELECT current_streak FROM habits_table WHERE habit_id = ?',
                                                       (habit_id,)).fetchone()

        self.assertEqual(2, current_streak[0])

    def test_get_all_successful(self):
        tracker_instance.add_habit(self.habit_name, self.valid_habit_periodicity)

        all_habits = tracker_instance.get_all_habits()

        self.assertTrue(len(all_habits) > 0)

    def test_get_all_no_habits(self):
        tracker_instance.conn.execute('DELETE FROM habits_table')

        all_habits = tracker_instance.get_all_habits()

        self.assertTrue(len(all_habits) == 0)

    def test_get_all_by_periodicity_successful(self):
        tracker_instance.add_habit(self.habit_name, self.valid_habit_periodicity)

        found_habits = tracker_instance.get_all_by_periodicity(self.valid_habit_periodicity)

        self.assertTrue(len(found_habits) > 0)

    def test_get_all_by_periodicity_not_found(self):
        tracker_instance.conn.execute('DELETE FROM habits_table')

        all_habits = tracker_instance.get_all_by_periodicity(self.valid_habit_periodicity)

        self.assertTrue(len(all_habits) == 0)

    def test_get_current_longest_streak_successful(self):
        habit_name_1 = generate_random_string(8)
        habit_name_2 = generate_random_string(8)
        tracker_instance.add_habit(habit_name_1, 'daily')
        habit_id_2 = tracker_instance.add_habit(habit_name_2, 'daily')

        tracker_instance.check_off(habit_name_1)

        tracker_instance.check_off(habit_name_2)
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        yesterday_str = yesterday.strftime('%Y-%m-%d')
        tracker_instance.conn.execute('UPDATE check_off_table SET date = ? WHERE habit_id = ?',
                                      (yesterday_str, habit_id_2))
        tracker_instance.check_off(habit_name_2)

        current_longest_streak = tracker_instance.get_current_longest_streak()

        self.assertEqual(1, len(current_longest_streak))
        self.assertEqual(current_longest_streak[0], (habit_id_2, habit_name_2))

    def test_get_current_longest_streak_two_equal(self):
        habit_name_1 = generate_random_string(8)
        habit_name_2 = generate_random_string(8)
        tracker_instance.add_habit(habit_name_1, 'daily')
        tracker_instance.add_habit(habit_name_2, 'daily')

        tracker_instance.check_off(habit_name_1)
        tracker_instance.check_off(habit_name_2)

        current_longest_streak = tracker_instance.get_current_longest_streak()

        self.assertEqual(2, len(current_longest_streak))

    def test_get_current_longest_streak_zero(self):
        habit_id = tracker_instance.add_habit(self.habit_name, 'daily')

        current_streak = tracker_instance.conn.execute('SELECT current_streak FROM habits_table WHERE habit_id = ?',
                                                       (habit_id,)).fetchone()

        self.assertEqual(current_streak[0], 0)

    def test_longest_streak_of_all_time_successful(self):
        habit_id = tracker_instance.add_habit(self.habit_name, 'daily')

        tracker_instance.check_off(self.habit_name)

        # making streak eq to 2
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        yesterday_str = yesterday.strftime('%Y-%m-%d')
        tracker_instance.conn.execute('UPDATE check_off_table SET date = ? WHERE habit_id = ?',
                                      (yesterday_str, habit_id))
        tracker_instance.check_off(self.habit_name)

        # breaking the habit
        check_offs = tracker_instance.conn.execute('SELECT id, date FROM check_off_table WHERE habit_id = ?',
                                                   (habit_id,)).fetchall()
        for check_off in check_offs:
            check_off_id = check_off[0]
            check_off_date = check_off[1]
            check_off_date = datetime.datetime.strptime(check_off_date, '%Y-%m-%d')
            check_off_date = check_off_date - datetime.timedelta(days=2)
            check_off_date_str = check_off_date.strftime('%Y-%m-%d')
            tracker_instance.conn.execute('UPDATE check_off_table SET date = ? WHERE id = ?',
                                          (check_off_date_str, check_off_id))

        tracker_instance.check_off(self.habit_name)

        longest_streak_of_all_time = tracker_instance.get_longest_streak()

        self.assertEqual(1, len(longest_streak_of_all_time))
        self.assertEqual(2, longest_streak_of_all_time[0][0])

    def test_longest_streak_of_all_time_two_equal(self):
        tracker_instance.add_habit(self.habit_name, 'daily')

        longest_streak_of_all_time = tracker_instance.get_longest_streak()

        self.assertEqual(1, len(longest_streak_of_all_time))
        self.assertEqual(0, longest_streak_of_all_time[0][0])

    def test_longest_streak_of_all_time_zero(self):
        habit_name_1 = generate_random_string(8)
        habit_name_2 = generate_random_string(8)
        tracker_instance.add_habit(habit_name_1, 'daily')
        tracker_instance.add_habit(habit_name_2, 'daily')

        tracker_instance.check_off(habit_name_1)
        tracker_instance.check_off(habit_name_2)

        longest_streak_of_all_time = tracker_instance.get_longest_streak()

        self.assertEqual(2, len(longest_streak_of_all_time))
        self.assertEqual(1, longest_streak_of_all_time[0][0])
        self.assertEqual(1, longest_streak_of_all_time[1][0])


if __name__ == '__main__':
    unittest.main()
