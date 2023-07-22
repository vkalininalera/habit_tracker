import argparse

from src.tracker import HabitTracker

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
