# Fujitsu IR done right (finally)

The main things in this repository are remote files for [SmartIR](https://github.com/smartHomeHub/SmartIR) that will let you control a Fujitsu ductless heat pump or air conditioner using a Broadlink IR transmitter.  The special feature of these files over other remotes is they send the "on" command with every temperature change so they "just work"--no need to leave the unit on or have a separate command to power on the unit.  Fujitsus have this peculiarity where the control string for every function is sent for any button press on the remote.  But for some odd reason, the "on" bit is only sent when the power button on the remote is turning the unit on.  There does not seem to be an ill effect from sending the "on" command" with every control string.  

Also included here is the code used to generate the files...so if we need to make improvements hopefully it is easy to regenerate everything.

This is based on my [previous work](https://github.com/mattjm/Fujitsu_IR/) and [dabram's excellent work](http://old.ercoupe.com/audio/FujitsuIR.pdf) (a copy of the PDF is in this GH repo in case it ever disappears from the web).  


## Files

**broadfromhexcode.py**:  Converts a Fujitsu hex control string into a base64 encoded Broadcom IR transmittter code.  Note this code is only tested to work with Fujitsu style hex codes.  There is no expectation it should work for anything else.  The output is the base64 encoded string that goes in a remote file for Home Assistant's SmartIR integration.  

**genfujitsuhex.py**:  Given some supported functions, calculates the appropriate control strings, converts them to IR codes using broadfromhexcode.py, and generates the "command" section of a remote file for the SmartIR integration.  



## Support

Tested with a Fujitsu ASU7RLF1 indoor unit.  The remote the work is based on is a Fujitsu AR-REG1U.  


## Errata

I found when first starting up HA with the remote file it "didn't work" until I explicitly set the various modes.

Heat goes as low as 16C, but the other modes only go down to 18C.  The file format only allows specifying one range.  If you try to set the temperature to 16 or 17 in a mode other than heat, nothing will happen.  


## Freedom Units

If your preferred temperature units are Fahrenheit you will see some odd behavior with the SmartIR integration and the regular remote file--temps will be shown in C but be marked as fahrenheit units.  This remote file has the temperatures in F instead of C.  This also requires having some duplicate commands for everything to work properly.  The other option was to go from 60-88 with increments of 2, but that puts you a full two degrees off by the time you reach 88.  


Each F temp corresponds to the closest C temp (convert F to C and round to the nearest integer):

```
 F   C
61  16
62  17
63  17
64  18
65  18
66  19
67  19
68  20
69  21
70  21
71  22
72  22
73  23
74  23
75  24
76  24
77  25
78  26
79  26
80  27
81  27
82  28
83  28
84  29
85  29
86  30
```








