#!/usr/bin/env python
from __future__ import division
import time
import sys
import csv
import serial
import serial.tools.list_ports

if __name__ == '__main__':
    # Get the port
    if len(sys.argv) < 2:
        print '   Please supply serial port:'
        print '   > power-recorder.py <serial-port>'
        sys.exit()

    # Open the port
    chosen_port = sys.argv[1]
    print 'Opening ' + chosen_port + ' ...'
    ser_port = serial.Serial(port=chosen_port, baudrate=9600, timeout=1)
    time.sleep(1)
    ser_port.flushInput()
    print 'Success!'

    # Time the frequency
    print 'Measuring sampling frequency...'
    start_time = time.time()
    samples = 0
    sample_time = 5
    while time.time() - start_time < sample_time:
        t = ser_port.readline()
        samples += 1
    sampling_frequency = samples/sample_time
    print 'Frequency is ' + str(sampling_frequency)

    # Figure out how many samples to record
    secs_to_record = None
    while secs_to_record is None:
        try:
            secs_to_record = float(raw_input('How many seconds do you want to record? '))
        except ValueError:
            print 'Please type a number of seconds.'
    n_samples = int(sampling_frequency * secs_to_record)
    print 'Will record ' + str(n_samples) + ' samples [' + str(len(t)*n_samples/1024/1024) + ' megabytes].'
    continue_choice = raw_input('Continue? <Y/n>: ')
    if continue_choice is 'n':
        sys.exit('Aborted capturing.')

    # Capture the data
    start_time = time.localtime()
    data = []
    ser_port.flushInput()
    # Discard the first line
    t = ser_port.readline()
    for i in xrange(n_samples):
        t = ser_port.readline()
        vals = map(float, t.split())
        data.append(vals)
    end_time = time.localtime()

    # Write to file
    filename = 'power-capture_' + time.strftime('%Y-%m-%d-%H:%M', start_time) + time.strftime('--%H:%M', end_time) + '.csv'
    with open(filename, 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerows(data)

    ser_port.close()
