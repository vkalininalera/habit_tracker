# Habit Tracker

This Python script provides a simple Habit Tracker using SQLite as 
the database backend. It allows you to add, delete, edit, 
and track habits with daily or weekly periodicity. Additionally, 
you can check-off habits, view all habits, view habits by periodicity, 
and get information about the longest streaks.

## Requirements

- Python
- SQLite

## Setup

To use the Habit Tracker, follow these steps:

1. Install python version 3.11. You can download it [here](https://www.python.org/downloads/).
2. Clone the repository.
3. Open your terminal and go to the folder of the cloned repository
```commandline
cd /path/to/habit_tracker
```
4. Install dependencies.
```commandline
python -m pip install -r requirements.txt
```
3. Run the script in your terminal.
```commandline
python main.py --help
```
4. You should see the following text on your screen
```txt
Habit Tracker
options:
	-help, --help        show this help message and exit
subcommands:
	Available commands
habit-add        Add a new habit
habit-delete     Delete an existed habit
habit-edit       Edit a habit
habit-check-off  Check-off a habit
get-all          Prints a list of all current habits
get-all-by-periodicity
								 Prints a list of habits with daily/weekly periodicity
current-longest-streak
								 Prints the current longest streak
longest-streak-for-all-time
								 Prints the longest streak for all the time
longest-streak-by-name
								 Prints the longest streak for all the time for the particular habit
```



## Usage

The following commands are available for the Habit Tracker:

### Adding a Habit

Add a new habit with the provided name and periodicity.

```bash
python main.py habit-add --name <HABIT_NAME> --periodicity <daily|weekly>
```

Example of output:

```shell
Habit 'running' with periodicity 'daily' is added to the table
```

### Deleting a Habit

Delete an existing habit by providing its name.

```bash
python main.py habit-delete --name <HABIT_NAME>
```
Example of output:

```shell
Habit 'running' is deleted
```

### Editing a Habit

Edit an existing habit by providing its name and optional new name and/or periodicity.

```bash
python main.py habit-edit --name <HABIT_NAME> [--new-name <NEW_HABIT_NAME>] [--new-periodicity <daily|weekly>]
```
Example of output:

```shell
Habit name changed from 'running' to 'reading'
No habit found with the name 'running'
```

### Checking-off a Habit

Check-off a habit for the current day, updating streak information if applicable.

```bash
python main.py habit-check-off --name <HABIT_NAME>
```
Example of output:
```shell
Habit 'running' is checked-off. Congrats, you are doing great!
Habit 'running' is on streak
```
### Viewing All Habits

Print a list of all current habits.

```bash
python main.py get-all
```
Example of output:
```shell
Name - swimming; periodicity - weekly, created - 2023-07-02 13:02:53
Name - walking; periodicity - daily, created - 2023-07-02 14:07:06
Name - reading; periodicity - daily, created - 2023-07-02 14:10:55
```
### Viewing Habits by Periodicity

Print a list of habits with the specified periodicity.


```bash
python main.py get-all-by-periodicity --periodicity <daily|weekly>
```
Example of output:
```shell
python tracker.py get-all-by-periodicity --periodicity weekly
python tracker.py get-all-by-periodicity --periodicity daily
```
### Viewing Current Longest Streak

Print the current longest streak among all habits.

```bash
python main.py current-longest-streak
```
Example of output:
```shell
Current longest streak 2, habit name 'swimming'
```

### Viewing Longest Streak for All Time

Print the longest streak for all habits throughout their history.


```bash
python main.py longest-streak-for-all-time
```
Example of output:
```shell
Longest streak for all the time is equal to 2, habit name 'swimming'
```
### Viewing Longest Streak for a Specific Habit

Print the longest streak for the specified habit.


```bash
python main.py longest-streak-by-name --name <HABIT_NAME>
```
Example of output:
```shell
Longest streak for 'reading' habit is equal to 0
```

## How to run tests

Unit tests are implemented with `unittest` library. 
To run tests execute the following command:

```shell
python -m unittest tests/test_tracker.py
```