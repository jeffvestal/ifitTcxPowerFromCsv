# ifitTcxPowerFromCsv
Add Watts power reading to tcx file from csv file exports

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

    the basename of the ifit export. 
    NOTE: the tcx and csv are assumed to have the same basename, just different file extensions
    The csv and tcx files can be manually exported from the workout summary screen on iFit's website. 
        
Output:

    1. File named: basename-combined.tcx
    2. Dump of any skipped trackpoints just for reference

Running
`./ifitTcxPowerFromCsv <workoutbasename>`
