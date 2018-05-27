#!/usr/bin/env python

import argparse
import time
from toggl_tools import Toggl


toggl = Toggl()


### Timezone (??)
# UTC is 0
timezone = 1


def read_api_key():
    config = open('config', 'r')
    api_key = config.readline().rstrip()
    config.close()
    return(api_key)


# Setting the API key. Need to reformat.
toggl.set_api_key(read_api_key())


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
    
    run_time_str = ("%02d" % hours) + ':' + ("%02d" % minutes) + ':' + ("%02d" % seconds)
    
    return start_time, run_time_str


def running_description(entry):
        entry_data = entry['data']
        description = entry_data['description']
        return description


def print_running():
    
    entry = toggl.running_entry()
    if entry == None:
        print("No Toggl entry is running.")
    else:
        description = running_description(entry)
        start_time, run_time = get_time(entry)

        print('>>> Running:      ' + description)
        print('>>> Start time:   ' + start_time)
        print('>>> Running for:  ' + run_time)
        
    # Decoding time.
    # Formatting everything.

def start_toggl(description):
    
    # Check if a task is running. If it is, print it.
    
    toggl.start_entry(description)
    print('>>> Starting:     ' + description)
    
    
def stop_toggl():
    entry = toggl.running_entry()
    if entry == None:
        print("No Toggl entry is running.")
    else:
        entry_data = entry['data']

        description = entry_data['description']
        creation_date = entry_data['start']
        duration = entry_data['duration']

        start_time, run_time = get_time(creation_date, duration)


        toggl.stop_entry()
        print('>>> Stopped       ' + description)
        print('>>> Start time:   ' + start_time)
        print('>>> Run time:     ' +     run_time)
    

def main():
    
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()

    group.add_argument('-n', '--new', type=str,
                       help="Create a new Toggl entry.")
    group.add_argument('-s', '--stop', action='store_true',
                       help="Stop the running Toggl entry.")

    parser.add_argument('-t', '--tag', nargs='+',
                        help="Set tags for the new Toggl entry.")
    
    parser.add_argument('-r', '--running', default=True,
                        help="Check running Toggl entry.",
                        action='store_true')

    args = parser.parse_args()

    if args.running:
        print_running()
    
    if args.tag and not args.new:
        print("Incorrect usage.")
        exit()
    
    elif args.new:
        start_toggl(str(args.new))
        
    elif args.stop:
        stop_toggl()



    
if __name__ == '__main__':
    main()
