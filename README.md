# MonarchParser

This python script will edit a GCODE file removing incompatitlbe codes that cannot be processed by an older CNC machine as well as adjust the feed rates of the program for the CNC dependant on the negative Z axis.  Although open source, this script is mostly ment for single instance only but provided so that customizations can be made to fit any CNC machine.  

### CheckText.txt
This file is used to remove bad lines within the file being parsed.  If it finds any occurance of any of the data inside the checktext file, it skips to the next line of the file being parsed.

### Header.txt
This file will add the text within this file to the top of the code after the original header.

### Tool_Prefix.txt
Like the header, This will add everything within this file BEFORE each tool change.  Leaving blank is not recommended.

### Tool_Suffix.txt
Identical to Tool_Prefix.txt with the exception it adds it AFTER each tool change.

With this code, adaptions to each cnc can be easily made.  

# Programmed Functions:
- Change G23 to G03
- Change G22 to G02
- Remove lines with "( )"
- Remove feed rates already attached to code
- Change M05 to M06E0
- Change Tool change command

# Passive Functions
- Grabs tool total from code
- Displays only amount of tools within code
- Skips lines if identical to previous write
- Adds jog height
