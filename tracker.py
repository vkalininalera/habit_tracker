# todo message about incorrect periodicity
# todo message about UNIQUE constraint failed: habits_table.name


import sqlite3
import datetime
import argparse
from sqlite3 import IntegrityError


class HabitTracker:
    def __init__(self):
        # Connecting to SQLite
        self.conn = sqlite3.connect("habits_table.db")

        # Creating a cursor object using the cursor() method for both tables in order to operate on them respectively
        self.habits_cursor = self.conn.cursor()
        self.check_off_cursor = self.conn.cursor()

        # Creating a table 'Habits_table'
        self.habits_cursor.execute('''CREATE TABLE IF NOT EXISTS habits_table
                               (
                               habit_id INTEGER PRIMARY KEY, 
                               name TEXT NOT NULL,
                               periodicity TEXT CHECK (periodicity IN ("daily","weekly")),
                               creation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                               current_streak INT DEFAULT 0,
                               longest_streak INT DEFAULT 0,
                               UNIQUE (name)
                               )''')
        # Creating a table 'Check-off'
        self.check_off_cursor.execute('''CREATE TABLE IF NOT EXISTS check_off_table 
                                (
                                id INTEGER PRIMARY KEY, 
                                habit_id INT,
                                date DATE,
                                FOREIGN KEY (habit_id) REFERENCES habits_table(habit_id)
                                )''')
        self.conn.commit()

    def add_habit(self, name, periodicity):
        """
        Adds a habit with the provided parameters if it doesn't exist.
        If it exists - throws an error.

        :param name: habit name
        :param periodicity: habit periodicity
        :return: habit-id
        """
        insert_query = """INSERT INTO habits_table (name, periodicity) VALUES(?,?)"""
        values = name, periodicity
        try:
            self.habits_cursor.execute(insert_query, values)
            habit_id = self.habits_cursor.lastrowid
            self.conn.commit()
            print("Habit '{}' with periodicity '{}'is added to the table".format(name, periodicity))
            return habit_id
        except IntegrityError as sql_err:
            if 'habits_table.name' in str(sql_err):
                print('Habit with name "{}" already exists'.format(name))
            else:
                raise sql_err
        except Exception as error:
            raise error

    def delete_habit(self, name):
        """
        Deleting of an existed habit from the habits table. If habit does not exist it prints a message indicating so.
        :param name: The habits name to delete
        :return: None
        """
        self.habits_cursor.execute("SELECT COUNT(*) FROM habits_table WHERE name = ?", (name,))
        count = self.habits_cursor.fetchone()[0]
        if count == 0:
            print("You don't have this habit")
        elif count == 1:
            self.habits_cursor.execute("DELETE FROM habits_table WHERE name = ?", (name,))
            self.conn.commit()
            print("Habit '{}' is deleted".format(name))

    def change_name(self, old_name, new_name):
        """
        Changing the name of an existed habit in the habits table
        :param old_name: The current name of the habit to change.
        :param new_name: The new name to assign to the habit.
        :return:None
        """
        update_query = "UPDATE habits_table SET name = ? WHERE name = ?"
        values = (new_name, old_name)
        self.habits_cursor.execute(update_query, values)
        self.conn.commit()
        if self.habits_cursor.rowcount > 0:
            print("Habit name changed from '{}' to '{}'.".format(old_name, new_name))
        else:
            print("No habit found with the name '{}'.".format(old_name))

    def change_periodicity(self, name, new_periodicity):
        """
        Changing the periodicity of an existing habit in the habits table
        :param name: The name of the habit to edit periodicity
        :param new_periodicity: The new periodicity value to set for the habit
        :return:None
        """
        self.habits_cursor.execute('SELECT periodicity FROM habits_table WHERE name = ?', (name,))
        periodicity_info = self.habits_cursor.fetchone()
        if periodicity_info:
            old_periodicity = periodicity_info[0]
            self.habits_cursor.execute("UPDATE habits_table SET periodicity = ? WHERE name = ?",
                                       (new_periodicity, name))
            self.conn.commit()
            print("Habit periodicity changed from '{}' to '{}'.".format(old_periodicity, new_periodicity))
        else:
            print("No habit found with the name '{}'.".format(name))

    def check_off(self, name):
        """
        Check-off the habit in the check-off table.
        If the habit does not exist it prints a message respectively.
        If the habit exists, it checks-off in the table check-off, moreover it checks if the habit is on streak.
        If the habit is on streak it adds 1 point to the current streak in the table habits table.
        If the habit is not on streak, it breaks the habit.
        Also, it updates the longest streak value if it is bigger than a current streak.
        If the habit is already checked-off it prints a message respectively.

        :param name: The name of the habit to check-off.
        :return: None
        """
        date_today = datetime.date.today()
        self.habits_cursor.execute('SELECT habit_id, periodicity FROM habits_table WHERE name = ?', (name,))
        habit_info = self.habits_cursor.fetchone()
        if habit_info is None:
            print('Habit with name {} does not exist'.format(name))
            return
        habit_id = habit_info[0]

        self.check_off_cursor.execute('SELECT date FROM check_off_table WHERE habit_id = ?', (habit_id,))
        check_off_info = self.check_off_cursor.fetchone()

        habit_periodicity = habit_info[1]

        if habit_info is not None:
            if check_off_info:
                last_check_off = check_off_info[0]
                last_check_off_date = datetime.datetime.strptime(last_check_off, "%Y-%m-%d").date()
                diff = date_today - last_check_off_date

                if habit_periodicity == 'daily' and diff.days == 0:
                    print("You have check the habit today already")
                    return
                elif habit_periodicity == 'weekly' and last_check_off_date.isocalendar()[1] == date_today.isocalendar()[
                    1]:
                    print("You have check the habit today already")
                    return

            if habit_periodicity == "daily":
                is_on_streak = self.daily_on_streak(habit_id)
            else:
                is_on_streak = self.weekly_on_streak(habit_id)

            if is_on_streak:
                self.habits_cursor.execute('SELECT current_streak, longest_streak FROM habits_table WHERE habit_id = ?',
                                           (habit_id,))
                streak_info = self.habits_cursor.fetchone()
                current_streak = streak_info[0]
                longest_streak = streak_info[1]
                updated_streak = current_streak + 1
                self.habits_cursor.execute('UPDATE habits_table SET current_streak = ? WHERE habit_id = ?',
                                           (updated_streak, habit_id,))
                if updated_streak > longest_streak:
                    self.habits_cursor.execute('UPDATE habits_table SET longest_streak = ? WHERE habit_id = ?',
                                               (updated_streak, habit_id,))
                self.conn.commit()
                print("Habit '{}' is on streak".format(name))
            else:
                self.habits_cursor.execute('UPDATE habits_table SET current_streak = 1 WHERE habit_id = ?',
                                           (habit_id,))
                self.conn.commit()
                print("BROKEN STREAK of the '{}' habit it is equal to 1 ".format(name))
            insert_query = """INSERT INTO check_off_table (habit_id, date) VALUES (?, ?)"""
            values = (habit_id, date_today)
            self.check_off_cursor.execute(insert_query, values)
            self.conn.commit()

            print("Habit '{}' is checked off. Congrats, you are doing great!".format(name))
        else:
            print("Habit '{}' doesn't exist.".format(name))

    def daily_on_streak(self, habit_id):
        """
        Check if the habit with daily periodicity is on streak.
        :param habit_id: The id of the habit to check.
        :return: Boolean. True if the habit is on streak, False otherwise.
        """
        today = datetime.date.today()
        # today = datetime.date(2023, 6, 3)
        self.check_off_cursor.execute('SELECT date FROM check_off_table WHERE habit_id = ? ORDER BY date DESC',
                                      (habit_id,))
        habit_info = self.check_off_cursor.fetchone()
        if habit_info is None:
            return True
        habit_str = habit_info[0]
        habit_last_date = datetime.datetime.strptime(habit_str, "%Y-%m-%d").date()
        difference = today - habit_last_date
        if difference.days == 1:
            return True
        else:
            return False

    def weekly_on_streak(self, habit_id):
        """
        Check if the habit with weekly periodicity is currently on streak.
        :param habit_id: The id of the habit to check.
        :return: Boolean. True if the habit is on streak, False otherwise.
        """
        today = datetime.date.today()
        week_num = today.isocalendar()[1]
        self.check_off_cursor.execute('SELECT date FROM check_off_table WHERE habit_id = ? ORDER BY date DESC',
                                      (habit_id,))
        check_off = self.check_off_cursor.fetchone()
        if check_off is None:
            return True
        date_str = check_off[0]
        habit_last_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        week_num_last = habit_last_date.isocalendar()[1]
        difference = week_num - week_num_last
        if difference == 1:
            return True
        else:
            return False

    def get_all_habits(self):
        """
        Retrieves information about all habits from the habits table.
        :return: A list of tuples containing habit information.
        """
        self.habits_cursor.execute('SELECT name, periodicity, creation_date FROM habits_table')
        habit_info = self.habits_cursor.fetchall()
        # Print the retrieved habit information
        for habit in habit_info:
            print("Name - {}; periodicity - {}, created - {}".format(habit[0], habit[1], habit[2]))
        return habit_info

    def get_all_by_periodicity(self, periodicity):
        """
        Retrieves information about habits with specified periodicity from habits table.
        :param periodicity: The periodicity value to filter the habits by.
        :return: A list of tuples containing habit information.
        """
        self.habits_cursor.execute('SELECT name, periodicity, creation_date FROM habits_table WHERE periodicity = ?',
                                   (periodicity,))
        habit_info = self.habits_cursor.fetchall()
        if not habit_info:
            print('No habits were found with "{}" periodicity'.format(periodicity))
        else:
            # Print the retrieved habit information
            for habit in habit_info:
                print("Name - {}; periodicity - {}; creation date - {}".format(habit[0], habit[1], habit[2]))
        return habit_info

    def get_current_longest_streak(self):
        """
        Retrieves information about current longest streak of the habit.
        :return: A list of tuples containing habit information, including the current longest streak and name.
        """
        self.habits_cursor.execute("""SELECT current_streak, name FROM habits_table
                                        JOIN (SELECT MAX(current_streak) AS max_value
                                        FROM habits_table) AS subquery
                                        ON habits_table.current_streak = subquery.max_value""")
        longest_streak = self.habits_cursor.fetchall()
        if not longest_streak:
            print("You don't have habits")
            return
        for habit in longest_streak:
            print("Current longest streak {}, name {}".format(habit[0], habit[1]))
        return longest_streak

    def get_longest_streak(self):
        """
        Retrieves information about the habit with the longest streak of all time from the habits table.
        :return: A list of tuples containing habit information, including the longest streak and name.
        """
        self.habits_cursor.execute("""SELECT longest_streak, name FROM habits_table
                                                JOIN (SELECT MAX(longest_streak) AS max_value
                                                FROM habits_table) AS subquery
                                                ON habits_table.longest_streak = subquery.max_value""")
        longest_streak = self.habits_cursor.fetchall()
        if not longest_streak:
            print("You don't have habits")
            return
        for habit in longest_streak:
            print('Longest streak for all time is equal to {}, habit name "{}"'.format(habit[0], habit[1]))
        return longest_streak

    def get_longest_streak_by_name(self, name):
        """
        Retrieve the longest streak for a specific habit by its name from the habits table.
        :param name: The name of the habit to retrieve the longest streak for.
        :return: None.
        """
        self.habits_cursor.execute('SELECT longest_streak FROM habits_table WHERE name = ?', (name,))
        streak_info = self.habits_cursor.fetchone()
        if not streak_info:
            print('You do not have habit with name "{}"'.format(name))
        else:
            print('Longest streak for "{}" habit is equal to {}'.format(name, streak_info[0]))


if __name__ == '__main__':
    habit_tracker = HabitTracker()

    parser = argparse.ArgumentParser(description="Habit Tracker")
    subparsers = parser.add_subparsers(dest="command", description="Available commands", )

    # Subparser for 'habit-add' command
    habit_add_parser = subparsers.add_parser("habit-add", description="Add a new habit", help="Add a new habit")
    habit_add_parser.add_argument("--name", required=True, help="Type the name of the habit")
    habit_add_parser.add_argument("--periodicity", required=True, choices=['daily', 'weekly'],
                                  help="Type the periodicity of the habit weekly/daily")

    # subparser for habit-delete command
    habit_delete_parser = subparsers.add_parser("habit-delete", description="Delete an existed habit",
                                                help="Delete an existed habit")
    habit_delete_parser.add_argument("--name", required=True, help="Type the name of a habit to delete")

    # subparser for habit-edit command
    habit_edit_parser = subparsers.add_parser("habit-edit", description="Edit a habit", help="Edit a habit")
    habit_edit_parser.add_argument("--name", required=True, help="Type the name of a habit to edit")
    habit_edit_parser.add_argument("--new-name", required=False, help="Type the new name of a habit")
    habit_edit_parser.add_argument("--new-periodicity", required=False, help="Type the new periodicity of a habit")

    # subparser for check-off of a habit
    habit_check_off_parser = subparsers.add_parser("habit-check-off", description="Check-off a habit",
                                                   help="Check-off a habit")
    habit_check_off_parser.add_argument("--name", required=True, help="Type the name of a habit to check-off")

    # subparser for get-all
    habit_get_all_parser = subparsers.add_parser("get-all", help="Prints a list of all current habits",
                                                 description="Prints a list of all current habits")

    # subparser for get-all-by-periodicity
    habit_get_all_by_periodicity = subparsers.add_parser("get-all-by-periodicity",
                                                         help="Prints a list of habits with daily/weekly periodicity",
                                                         description="Prints a list of habits with daily/weekly periodicity")
    habit_get_all_by_periodicity.add_argument("--periodicity", required=True, help="Type the periodicity")

    # subparser for get-current-longest-streak
    habit_get_current_longest_streak = subparsers.add_parser("current-longest-streak",
                                                             help="Prints the current longest streak",
                                                             description="Prints the current longest streak")

    # subparser for get-longest-streak
    habit_get_longest_streak = subparsers.add_parser("longest-streak-for-all-time",
                                                     help="Prints the longest streak for all the time",
                                                     description="Prints the longest streak for all the time")

    # subparser for get-longest-streak-name
    habit_get_longest_streak_by_name = subparsers.add_parser("longest-streak-by-name",
                                                             description="Prints the longest streak for all the time for the particular habit",
                                                             help="Prints the longest streak for all the time for the particular habit")
    habit_get_longest_streak_by_name.add_argument("--name", required=True, help="Type the name of a habit")

    arguments = parser.parse_args()

    if arguments.command == "habit-add":
        habit_tracker.add_habit(arguments.name, arguments.periodicity)
    elif arguments.command == 'habit-delete':
        habit_tracker.delete_habit(arguments.name)
    elif arguments.command == 'habit-edit':
        if arguments.new_name:
            habit_tracker.change_name(arguments.name, arguments.new_name)
        if arguments.new_periodicity:
            habit_tracker.change_periodicity(arguments.name, arguments.new_periodicity)
    elif arguments.command == 'habit-check-off':
        habit_tracker.check_off(arguments.name)
    elif arguments.command == 'get-all':
        habit_tracker.get_all_habits()
    elif arguments.command == 'get-all-by-periodicity':
        habit_tracker.get_all_by_periodicity(arguments.periodicity)
    elif arguments.command == 'current-longest-streak':
        habit_tracker.get_current_longest_streak()
    elif arguments.command == 'longest-streak-for-all-time':
        habit_tracker.get_longest_streak()
    elif arguments.command == 'longest-streak-by-name':
        habit_tracker.get_longest_streak_by_name(arguments.name)
    else:
        parser.print_help()
