#!/bin/python

from termcolor import colored

# I/O helper functions
INPUT_INDICATOR = '> '

def printError(msg):
   print "[ %s ] %s" % (colored('ERROR', 'red'), msg)

def printInfo(msg):
   print "[ %s ] %s" % (colored('INFO', 'green'), msg)

def printWarn(msg):
   print "[ %s ] %s" % (colored('WARN', 'yellow'), msg)

def make_prompt(string):
   return "[ %s ] %s" % (colored(string, 'magenta'), INPUT_INDICATOR)

def forever_raw_input(string):
   input_string = raw_input(string)
   while True:
      if input_string != '':
         return input_string
      input_string = raw_input(INPUT_INDICATOR)

