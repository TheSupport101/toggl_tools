#!/usr/bin/env python

import argparse
import time
import os
from toggl_tools import Toggl
import sys


toggl = Toggl()

# TODO: Easier timezone behaviour.
# UTC is 0
timezone = 1

RESUME_NUMBER = 10


def read_api_key():
    """Read the user's API key from the config file."""
    script_path = os.path.dirname(os.path.realpath(__file__))
    config = open(script_path + '/config', 'r')
    api_key = config.readline().rstrip()
    config.close()
    return(api_key)


# Setting the API key. Need to reformat.
toggl.set_api_key(read_api_key())


### Auxiliary Functions ###
def get_time(entry):
    """ Turns the date into a readable format."""
    entry_data = entry['data']
    time_str = entry_data['start']
    duration = entry_data['duration']

    # time_str example string:
    # 2018-05-25T18:21:13+00:00
    date = time_str[:10]

    # Adds the timezone to the given hour.
    start_hour = int(time_str[11:13]) + timezone
    start_time = str(start_hour) + time_str[13:19]

    # Calculates running duration.
    run_time = time.time() + duration
    hours = int(run_time // 3600)
    minutes = int((run_time // 60) - hours * 60)
    seconds = int(run_time % 60)

    # TODO: Reformat - line string too long.
    run_time_str = ("%02d" % hours) + ':' + ("%02d" % minutes) + ':' + ("%02d" % seconds)

    return start_time, run_time_str


def entry_in_list(entry, a_list):
    """Checks if an entry with the same description exists in given list."""
    for item in a_list:
        if entry['description'] == item['description']:
            return True
    return False


def entry_epoch_time(entry):
    """Returns an entry's epoch time."""
    return time.mktime(time.strptime(entry['start'][:-6],
                                     '%Y-%m-%dT%H:%M:%S'))


def sort_entries(entries_list):
    """Order a list of entries according to its date."""
    entries_list.sort(key=entry_epoch_time, reverse=True)


def running_description(entry):
    entry_data = entry['data']
    description = entry_data['description']
    return description


def running_tags(entry):
    entry_data = entry['data']
    tags = entry_data['tags']
    if tags == []:
        return None
    else:
        return tags


### ###
def print_running(entry):
    if entry is None:
        print("No Toggl entry is running.")
    else:
        description = running_description(entry)
        tags = running_tags(entry)
        start_time, run_time = get_time(entry)
        print('>>> Running:      ' + description)
        if tags is not None:
            print('>>> Tags:         ' + ",".join(tags))
        print('>>> Start time:   ' + start_time)
        print('>>> Running for:  ' + run_time)

    # Decoding time.
    # Formatting everything.


def check_running():
    entry = toggl.running_entry()
    if entry is None:
        return False
    else:
        return True


def start_toggl(description, tags):
    # TODO: Check if a task is running. If it is, print it.
    toggl.start_entry(description, tags=tags)
    print('>>> Starting:     ' + description)


def stop_toggl():
    entry = toggl.running_entry()
    if entry is None:
        print("No Toggl entry is running.")
    else:
        description = running_description(entry)
        start_time, run_time = get_time(entry)

        toggl.stop_entry()
        print('>>> Stopped       ' + description)
        print('>>> Start time:   ' + start_time)
        print('>>> Run time:     ' + run_time)


def resume():
    """Resumes a recent entry with all its properties."""
    entry = toggl.running_entry()
    if entry is not None:
        print("An entry is already running:")
        print_running(entry)
        return False
    # We now retrieve all entries in the previous month.
    # Getting the current date and the date from a month before.
    time_year = time.localtime()[0]
    time_month = time.localtime()[1]
    time_day = time.localtime()[2]
    if time_month == 1:
        prev_time_month = 12
        prev_time_year = time_year - 1
    else:
        prev_time_month = time_month - 1
        prev_time_year = time_year

    # TODO: Reformat this barbarity.
    cur_date = str(time_year) + '-' + ('%02d' % time_month) + '-' + ('%02d' % time_day)
    prev_date = str(prev_time_year) + '-' + ('%02d' % prev_time_month) + '-' + ('%02d' % time_day)

    # We retrieve all entries from the last month. We then order them by date
    # so, when eliminating ones with the same description, we're left with the
    # most recent instance of each.
    entries = toggl.entries_between(prev_date, cur_date)
    sort_entries(entries)
    entry_list = []

    for entry in entries:
        if entry_in_list(entry, entry_list) is False:
            entry_list.append(entry)

    # We print a certain number of entries.
    # That number is defined by RESUME_NUMBER. Default is 10.

    # TODO: Make RESUME_NUMBER depend on an option or configuration.
    # TODO: Add last run information to each entry.

    print(">>> You can resume the following entries:")
    for n, entry in enumerate(entry_list, 1):
        tags = []
        if 'tags' in entry:
            [tags.append(i) for i in entry['tags']]
        print('> {} - {} [{}]'.format(str(n),
                                      entry['description'],
                                      ",".join(tags)))
        if n == RESUME_NUMBER:
            break

    try:
        choice = int(input(">>> Type an entry number: "))
    except KeyboardInterrupt:
        print("\nClosing...")
        sys.exit(0)

    if choice >= 1 and choice <= len(entry_list):
        res_entry = entry_list[choice-1]
        start_toggl(res_entry['description'], res_entry['tags'])
    else:
        print("You typed an unavailable number.")

    """
    >>> You can resume the following entries:
    > 1 - test [tag]
    > 2 - another [different_tag]
    >>> Type an entry number:
    """


def add_entry(description, tags, duration):
    """Create a finished entry with a set duration."""
    time_year = time.localtime(time.time() - duration)[0]
    time_month = time.localtime(time.time() - duration)[1]
    time_day = time.localtime(time.time() - duration)[2]
    time_hour = time.localtime(time.time() - duration)[3]
    time_min = time.localtime(time.time() - duration)[4]
    time_sec = time.localtime(time.time() - duration)[5]

    # TODO: Reformat this barbarity.
    start_time = str(time_year) + '-' + ('%02d' % time_month) + '-' + ('%02d' % time_day) + 'T' + ('%02d' % time_hour) + ':' + ('%02d' % time_min) + ':' + str(time_sec) + '+' + ('%02d:00' % timezone)

    toggl.create_entry(description, start_time=start_time, duration=duration, tags=tags)

    print('>>> Created: ' + description)


### MAIN ###
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()

    group.add_argument('-n', '--new', type=str,
                       help="Create a new Toggl entry.")
    group.add_argument('-s', '--stop', action='store_true',
                       help="Stop the running Toggl entry.")
    group.add_argument('-r', '--resume', action='store_true',
                       help="Resume a previous Toggl entry.")
    group.add_argument('-a', '--add', type=str,
                       help="Add a Toggl entry.")

    parser.add_argument('-d', '--duration',
                        help="Set duration for a done entry.")
    parser.add_argument('-t', '--tag', nargs='+',
                        help="Set tags for the new Toggl entry.")

    parser.add_argument('--running', default=False,
                        help="Check running Toggl entry.",
                        action='store_true')

    args = parser.parse_args()

    # TODO: Reformat this barbarity.
    if args.running:
        entry = toggl.running_entry()
        print_running(entry)

    elif args.tag and args.new:
        start_toggl(str(args.new), args.tag)

    elif args.tag and args.duration and args.add:
        add_entry(str(args.add), args.tag, int(args.duration))

    elif args.resume:
        resume()

    elif args.stop:
        stop_toggl()

    # Default behaviour is to show running entries.
    else:
        entry = toggl.running_entry()
        print_running(entry)
    '''
    if args.tag and not args.new:
        print("Incorrect usage.")
        exit()

    elif args.new:
        start_toggl(str(args.new))
    '''

    read_api_key()
