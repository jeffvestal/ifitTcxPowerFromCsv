#! env python

'''
Author : Jeff Vestal - github.com/jeffvestal

iFit refuses to include Watts in the workout export tcx file for some reason
Watts is included in the csv but that can't be used for Strava or other fitness sites
This script :
    1. creates a dictionary of time(offset from start) : Watts for lookup
    2. Converts the tcx (xml) file to a dict for ease of use in python
    3. For each trackpoint:
        1. Calculate the offset from the start
        2. use that offset to lookup the watts reading
        3. add an Extensions dict that includes Watts to the trackpoing
    4. Write the updated data back to a file in tcx (xml) format

Input:
    the basename of the ifit export. NOTE:
        the tcx and csv are assumed to have the same basename, just different file extensions

Output:
    1. File named: basename-combined.tcx
    2. Dump of any skipped trackpoints just for reference
'''

import sys
import  xmltodict
import datetime as dt
from collections import OrderedDict
from pprint import pprint
from copy import deepcopy



def buildPowerFromCsv(csvFile):
    '''Create a dict of elapsedTime:watts'''

    csv = open(csvFile + '.csv')
    time2power = {}
    for line in csv:
        if line.startswith('Stages') or line.startswith('English') or line.startswith('Time'):
            # Skip over header rows
            # could be smarter here and check which column watts is in incase it changes at some point.
            pass
        else:
            l = line.split(',')
            time2power[l[0]] = l[3]

    return time2power


def loadTcx (tcxFile):
    '''
    Load tcx file and convert to dict
    Return tcxDict and first trackpoint time as datetime obj
    '''

    f = open(tcxFile + '.tcx')
    tcx = xmltodict.parse(f.read())
    start = dt.datetime.strptime(tcx['TrainingCenterDatabase']['Activities']['Activity']['Lap']['Track']['Trackpoint'][0]['Time'], '%Y-%m-%dT%H:%M:%S.%fZ')

    return (tcx, start)


def addWattsFromCsv(tpD, t2p, start):
    '''add watts to trackpoint'''

    count = 0
    skippedPoints = []
    Extensions = OrderedDict([('TPX', OrderedDict([('@xmlns', 'http://www.garmin.com/xmlschemas/ActivityExtension/v2'), ('Watts', '0')]))])

    for pos, point in enumerate(tpD['TrainingCenterDatabase']['Activities']['Activity']['Lap']['Track']['Trackpoint']):
        # Loop through each trackpoint, calculate the elapsedTime, use that to pull the Watts from the csv

        end  = dt.datetime.strptime(point['Time'], '%Y-%m-%dT%H:%M:%S.%fZ')
        if start == end:
            #Handle the first trackpoint
            csvTime = '00:00'
            elapsedTime = '00:00'
        else:
            elapsedSeconds = int((end-start).total_seconds())
            elapsedTime = str(dt.timedelta(seconds=elapsedSeconds))

            et = elapsedTime.split(':')
            csvTime = ':'.join(['%02d' % (int(et[0])*60 + int(et[1])), et[2]])

        try:
            # Pull watts from csv
            watts = t2p[csvTime]
        except KeyError:
            skippedPoints.append([end, elapsedTime])
            continue

        # Need to deep copy the Extensions dict then pull the Watts from the csv
        extCopy = deepcopy(Extensions)
        extCopy['TPX']['Watts'] = str(watts)
        tpD['TrainingCenterDatabase']['Activities']['Activity']['Lap']['Track']['Trackpoint'][pos]['Extensions'] = extCopy

    return (tpD, skippedPoints)


def ouputTcx(tcx, filename):
    '''write combined tcx file'''

    combinedName = filename + '-combined.tcx'
    f = open(combinedName, 'w')
    xmltodict.unparse(tcx, f)

    return combinedName


def addWattsToTcx(fileBaseName):
    '''assume extentionless name is given
    TODO something smarter to ensure just the basename is given
    '''

    time2power = buildPowerFromCsv(inputFile)
    tcxDict, startDT = loadTcx(fileBaseName)
    updatedTCX, skippedPts = addWattsFromCsv(tcxDict, time2power, startDT)
    combinedFile = ouputTcx(updatedTCX, fileBaseName)

    print('Adding Watts to tcx file complete.\nOutput -> %s' % combinedFile)
    print('\nSkipped points: %s' % skippedPts)


if __name__ == '__main__':

    inputFile = sys.argv[1]
    addWattsToTcx(inputFile)


