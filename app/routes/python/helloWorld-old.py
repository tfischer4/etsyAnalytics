#!/usr/bin/python

import sys, getopt

def main(argv):
   tag = ''
   mode = ''
   try:
      opts, args = getopt.getopt(argv,"ht:m:",["tag=","mode="])
   except getopt.GetoptError:
      print 'helloWorld.py -t <tag> -m <mode>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'helloWorld.py -t <tag> -m <mode>'
         sys.exit()
      elif opt in ("-t", "--tag"):
         tag = arg
      elif opt in ("-m", "--mode"):
         mode = arg
      else: 
         print 'helloWorld.py -t <tag> -m <mode>'
         sys.exit(2)
   print 'python: hello ' + tag

if __name__ == "__main__":
   main(sys.argv[1:])
