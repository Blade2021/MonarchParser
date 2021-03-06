import fileinput
import sys
import configparser

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

# Initialise arrays for parsing
# Array sizes will be increased as needed
slowRateArray = ['', '']
fastRateArray = ['', '']
toolArray = ['', '']
# Main Window
root = tk.Tk()
root.title("GCode File Parser - By Matt W.")
root.resizable(width=False, height=False)  # Disable resizing
indx = 0
jogVariable = ''
skipCount = 8
slowRateLabel = ["", ""]
fastRateLabel = ["", ""]
toolLabelArray = ['', '']
output = ""
tprefix = ""
file_path = filedialog.askopenfilename()

# Grab tool amount from file
def toolAmount():
    tools = 0
    linenumber = 0
    try:
        global output
        output = ""
        with fileinput.input(files="tool_suffix.txt") as tfile:
            for line in tfile:
                output = output + line
        output = output + "\n"
        fileinput.close()
    except IOError:
        sys.stdout.write("File not found")
        exit(442)
    try:
        global tprefix
        tprefix = ""
        with fileinput.input(files="tool_prefix.txt") as tfile:
            for line in tfile:
                tprefix = tprefix + line
        tprefix = tprefix + "\n"
        fileinput.close()
    except IOError:
        sys.stdout.write("File not found")
        exit(442)
    try:
        with fileinput.input(files=file_path, inplace=0) as file:
            for line in file:
                # Keep Track of Line # for debugging & output
                linenumber += 1
                # Look for lines that begin with "("
                parentCheck = line.find("(")
                if parentCheck != -1:  # Ignore the first line of the program
                    # If first character is '(' skip line
                    if parentCheck == 0:
                        continue
                    else:
                        # Remove commented section of code
                        line = line[0:parentCheck]
                        line = line + "\n"
                # Look for T code to signal tool change
                toolCheck = line.find('T.')
                if toolCheck >= 1:
                    # Increase tool amount
                    tools += 1
                    sys.stdout.write("Tool found on line #:" + str(linenumber) + '\n')
        # No tools found
        if tools < 0:
            sys.stdout.write("No tools found\n\n")
            sys.stdout.write("System exit code: 483\n")
            exit(8)
        else:
            return tools
    except IOError:
        print("File not found")
        print("System exit code: 392")
        exit(4)


tools = toolAmount() # Trigger tool find function
sys.stdout.write("###     File Parser found " + str(tools) + " tools     ###\n\n")
joglengthLabel = tk.Label(root, text="Jog Height", font='Times 12', borderwidth=3, width=12)
# Initialise rate labels
while indx < tools:
    if (indx >= len(slowRateLabel)) or (indx >= len(fastRateLabel)):
        slowRateLabel.extend(["", ""])
        fastRateLabel.extend(["", ""])
        toolLabelArray.extend(["", ""])

    slowRateLabel[indx] = tk.Label(root, text=("Slow Rate " + str(indx+1)), font='Times 12', borderwidth=3, width=12)
    slowRateLabel[indx].grid(row=indx+1, column=3)

    fastRateLabel[indx] = tk.Label(root, text=("Fast Rate " + str(indx+1)), font='Times 12', borderwidth=3, width=12)
    fastRateLabel[indx].grid(row=indx + 1, column=5)

    toolLabelArray[indx] = tk.Label(root, text=("Tool ID " + str(indx+1)), font='Times 12', borderwidth=3, width=12)
    toolLabelArray[indx].grid(row=indx+1, column=0)
    indx += 1
    root.focus_force()

# Execute Function: Runs values entered or from datafile to parse the file.
def execute():
    root.withdraw()
    linenum = 0
    rate = 0  # Rate control (Keeps from adding feed rate to every line)
    value = "Z-"
    toolIndex = -1  # (-1 = Skip first tool line (initial tool)) ( 0 - disable skip )
    indx = 0
    checkText = ['', '', '']
    lastline = ""
    global output
    global tprefix
    # Load checkText array with checks
    try:
        with fileinput.input(files='checkText.txt', inplace=0) as checkdata:
            for cline in checkdata:
                # Use TRY method to only extend if needed
                try:
                    cline = cline.rstrip('\n')
                    checkText[checkdata.filelineno()-1] = cline
                except IndexError:
                    if checkdata.filelineno() >= len(checkText):
                        checkText.extend([""])
                    cline = cline.rstrip('\n')
                    checkText[checkdata.filelineno() - 1] = cline
        checkdata.close()
        sys.stdout.write("Searching document for:\n" + str(checkText) + '\n')
    except FileNotFoundError:
        print("\nERROR: Could not find checktext.txt file.  Please add file before retrying\n\n")
        exit(440)

    skipTrigger = 0

    # Add F key before the feed rate
    while indx < tools:
        slowRateArray[indx] = str('F' + slowRateArray[indx])
        fastRateArray[indx] = str('F' + fastRateArray[indx])
        sys.stdout.write("   Tool #: " + str(indx) + '\n')
        sys.stdout.write("Tool ID   [" + str(indx) + "] Value:" + toolArray[indx] + '\n')
        sys.stdout.write("Slow Rate [" + str(indx) + "] Value:" + slowRateArray[indx] + '\n')
        sys.stdout.write("Fast Rate [" + str(indx) + "] Value:" + fastRateArray[indx] + '\n\n')
        indx += 1  # increment the array index
    # Trigger open file window
    # file_path = filedialog.askopenfilename()
    try:
        with fileinput.input(files=file_path, inplace=0) as file:
            k = file_path.rfind(".")
            newFile = file_path[:k] + "_Parsed" + file_path[k:]
            f = open(newFile, 'w')
            for line in file:
                if file.filelineno() == 1:
                    f.write(line)
                    sys.stdout.write("Header: " + line + '\n')
                    # Insert header text from header.txt file
                    headerfile = open('header.txt', 'r')
                    for x in headerfile:
                        x = x.strip('\n')
                        f.write(x + '\n')
                    f.write("W-" + jogVariable + '\nM02\n')
                    headerfile.close()
                    linecheck = file.filelineno()
                    continue
                # Remove comments from the file
                parentCheck = line.find("(")
                if parentCheck != -1:  # Ignore the first line of the program
                    if parentCheck == 0:
                        continue
                    else:
                        line = line[0:parentCheck]
                        line = line + "\n"
                if linecheck <= skipCount:
                    linecheck += 1
                    # Stop skipping lines if tool line is found
                    doubleCheck = line.find('T')
                    if doubleCheck != -1:
                        linecheck = skipCount
                    else:
                        continue
                checkIndex = 0
                while checkIndex < len(checkText):
                    specialCheck = line.find(checkText[checkIndex])
                    if specialCheck != -1:
                        checkIndex += 1
                        skipTrigger = 1
                        sys.stdout.write("Found bad character. Line:[" + str(file.filelineno()) + "] \n")
                        break
                    else:
                        checkIndex += 1
                        continue
                if skipTrigger == 1:
                    skipTrigger = 0
                    continue
                # Remove Feed rates if applicable
                feedCheck = line.find('F')
                if feedCheck >= 1:
                    line = line[0:feedCheck]
                    line += "\n"

                line = line.replace("G23", "G03")  # Change G23 to G03
                line = line.replace("G22", "G02")  # Change G22 to G02
                line = line.replace("M05", "M06E0")  # Change M05 to M06E0

                # Search document for P codes and remove them
                pcodeCheck = line.find('P')
                if pcodeCheck >= 1:
                    line = line[0:pcodeCheck]
                    line += "\n"
                # Search document for S codes and remove them
                pcodeCheck = line.find('S')
                if pcodeCheck >= 1:
                    line = line[0:pcodeCheck]
                    line += "\n"

                # Look for tool changes
                toolCheck = line.find('T')
                if toolCheck >= 1:
                    toolIndex += 1
                    line = (tprefix + "T" + toolArray[toolIndex] + output)
                    if toolIndex >= len(slowRateArray):
                        toolIndex = 0
                # Search document line by line for Z negatives
                if value in line:
                    # Skip adding a feed rate if line has G00 in it
                    if "G00" in line:
                        continue
                    # Add a double check to the next line to see if its a G01
                    linenum = file.filelineno() + 1
                    # Secondary remove feed line if applicable.
                    feedCheck = line.find('F')
                    if feedCheck >= 1:
                        line = line[0:feedCheck]
                    # Remove the end character
                    line = line.rstrip('\n')
                    # Check if fast feed rate is already active
                    if rate >= 2:
                        line += slowRateArray[toolIndex] + "\n"
                        rate = 1
                    # Slow rate is enabled
                    else:
                        # Add slow feed rate to first occurrence
                        if rate == 0:
                            rate = 1
                            line += slowRateArray[toolIndex]
                        line += "\n"
                # Check line number vs linenum, and if G01 in line ( Switch to fast rate )
                if (file.filelineno() == linenum) and ("G01" in line):
                    feedCheck = line.find('F')
                    if feedCheck >= 1:
                        line = line[0:feedCheck]
                    if rate == 1:
                        line = line.rstrip('\n')
                        line += fastRateArray[toolIndex] + "\n"
                        rate = 2
                else:
                    # Skip feed rate change if G01 not in line but check the next line
                    linenum = file.filelineno() + 1
                # Write line to file
                # with fileinput.input(files=newFile, inplace=1) as writeFile:
                # sys.stdout.write(line)
                if lastline == line:
                    sys.stdout.write("\nWARNING: Skipping line due to same value. Line# [" + str(linenum-1) + "]\n\n")
                    continue
                lastline = line
                f.write(line)
        sys.stdout.write('\n')
        f.close()
        fileinput.close()
    # If file cannot be opened
    except IOError:
        exit(4)
    sys.stdout.write("File parsed successfully\n")
    fnameIndex = file_path.rfind('/')
    extIndex = file_path.rfind('.')
    filename = file_path[fnameIndex+1:extIndex]
    sys.stdout.write("New File: " + str(filename) + "_Parsed" + str(file_path[extIndex:]) + "\n\n")
    exit()

# Get data from entry sections
def grabMax():
    indx = 0
    global jogVariable
    jogVariable = str(joglength.get())
    sys.stdout.write("Jog Height: " + str(joglength.get()) + '\n')
    # Ask to save to data file
    saveVariable = tk.messagebox.askyesno("Data File", "Would you like to save the data?")
    if saveVariable is True:
        saveVar = 1
    else:
        saveVar = 0

    config = configparser.ConfigParser()
    config.read('data.ini')
    # Load input from entry window
    while indx < tools:
        try:
            if tools >= len(slowRateArray):
                slowRateArray.extend(["", ""])
            # Grab values from entry array
            slowRateArray[indx] = str(slowRateEntryArray[indx].get())
            if slowRateArray[indx] is "":
                slowdef = config.get('DEFAULT', 'slowDefault')
                sys.stdout.write("! WARNING: Using default setting for Tool_ID: " + str(indx+1) + " Slow Rate\n" +
                                 "   Value: " + slowdef + '\n\n')
                slowRateArray[indx] = slowdef
                indx += 1
                continue
            # Save values to data.ini if allowed and NOT blank!
            if saveVar == 1 and slowRateArray[indx] is not "":
                try:
                    if indx < 10:
                        toolname = ("TOOL_0" + (str(indx+1)))
                    else:
                        toolname = ("TOOL_" + (str(indx+1)))
                    config[toolname]['SlowRate'] = slowRateArray[indx]
                except KeyError:
                    config.add_section(toolname)
                    config.set(toolname, 'SlowRate', slowRateArray[indx])
                except configparser.NoSectionError:
                    config.add_section(toolname)
                    config.set(toolname, 'SlowRate', slowRateArray[indx])
        except ValueError:
            indx += 1
            slowRateArray[indx] = config.get('DEFAULT', 'SlowDefault')
            continue
        indx += 1
    indx = 0
    while indx < tools:
        try:
            if tools >= len(fastRateArray):
                fastRateArray.extend(["", ""])
            # Grab values from entry array
            fastRateArray[indx] = str(fastRateEntryArray[indx].get())
            if fastRateArray[indx] is "":
                fastdef = config.get('DEFAULT', 'fastDefault')
                sys.stdout.write("! WARNING: Using default setting for Tool_ID: " + str(indx + 1) + " Fast Rate\n" +
                                 "   Value: " + fastdef + '\n\n')
                fastRateArray[indx] = fastdef
                indx += 1
                continue
            # Save values to data.ini if allowed and NOT blank!
            if saveVar == 1 and fastRateArray[indx] is not "":
                try:
                    if indx < 10:
                        toolname = ("TOOL_0" + (str(indx + 1)))
                    if indx >= 10:
                        toolname = ("TOOL_" + (str(indx + 1)))
                    config.set(toolname, 'FastRate', fastRateArray[indx])
                except KeyError:
                    config.add_section(toolname)
                    config.set(toolname, 'FastRate', fastRateArray[indx])
                except configparser.NoSectionError:
                    config.add_section(toolname)
                    config.set(toolname, 'FastRate', fastRateArray[indx])
        except ValueError:
            indx += 1
            fastRateArray[indx] = config.get('DEFAULT', 'FastDefault')
            continue
        indx += 1
    indx = 0
    while indx < tools:
        try:
            if tools >= len(toolArray):
                toolArray.extend(["", ""])
            # Grab values from entry array
            toolArray[indx] = str(toolEntryArray[indx].get())
            if toolArray[indx] is "":
                if indx < 10:
                    toolid = '0' + str(indx)
                else:
                    toolid = str(indx)
                sys.stdout.write("! WARNING: Using default setting for Tool_ID: " + str(indx + 1) + " Tool #\n" +
                                 "   Value: " + toolid + '\n\n')
                toolArray[indx] = toolid
                indx += 1
                continue
            # Save values to data.ini if allowed and NOT blank!
            if saveVar == 1 and toolArray[indx] is not "":
                try:
                    if indx < 10:
                        toolname = ("TOOL_0" + (str(indx + 1)))
                    if indx >= 10:
                        toolname = ("TOOL_" + (str(indx + 1)))
                    config.set(toolname, 'ToolID', toolArray[indx])
                except KeyError:
                    config.add_section(toolname)
                    config.set(toolname, 'FastRate', toolArray[indx])
                except configparser.NoSectionError:
                    config.add_section(toolname)
                    config.set(toolname, 'FastRate', toolArray[indx])
        except ValueError:
            indx += 1
            toolArray[indx] = config.get('DEFAULT', '0'+toolid)
            if indx < 10:
                toolArray[indx] = '0' + indx
            else:
                toolArray[indx] = indx
            continue
        indx += 1

    with open('data.ini', 'w') as configfile:
        config.write(configfile)
    execute()


def exeDataFile():
    sys.stdout.write("###   Using data file   ### \n")
    config = configparser.ConfigParser()
    config.read('data.ini')
    arrayindex = 0
    try:
        while arrayindex < tools:
            if arrayindex < 9:
                toolname = ("TOOL_0" + (str(arrayindex + 1)))
            else:
                toolname = ("TOOL_" + (str(arrayindex + 1)))
            try:
                if arrayindex >= len(slowRateArray):
                    slowRateArray.extend(["", ""])
                    fastRateArray.extend(["", ""])
                    toolArray.extend(['', ''])
                slowRateArray[arrayindex] = config.get(toolname, 'SlowRate')
                fastRateArray[arrayindex] = config.get(toolname, 'FastRate')
                toolArray[arrayindex] = config.get(toolname, 'ToolID')
            except configparser.NoSectionError:
                sys.stdout.write("ERROR:" + toolname + " not found in data.ini\n")
                sys.stdout.write("Terminating Program\n\n")
                exit(6)
            arrayindex += 1
    except IOError:
        print("something went wrong")
        exit()
    execute()


# Initialise entry arrays
slowRateEntryArray = ["", ""]
fastRateEntryArray = ["", ""]
toolEntryArray = ["", ""]
# Configure entry arrays
entryIndex = 0
config = configparser.ConfigParser()
config.read('data.ini')
skipCount = int(config['DEFAULT']['forwardx'])
while entryIndex < tools:
    if (entryIndex >= len(slowRateEntryArray)) or (entryIndex >= len(fastRateEntryArray)):
        slowRateEntryArray.extend(["", ""])
        fastRateEntryArray.extend(["", ""])
        toolEntryArray.extend(["", ""])

    toolEntryArray[entryIndex] = tk.Entry(master=root, width=10)
    toolEntryArray[entryIndex].grid(column=2, row=(entryIndex+1))
    try:
        if entryIndex < 10:
            toolname = ("TOOL_0" + (str(entryIndex + 1)))
        else:
            toolname = ("TOOL_" + (str(entryIndex + 1)))
        toolEntryArray[entryIndex].insert(0, config[toolname]['ToolID'])
    except KeyError:
        toolEntryArray[entryIndex].insert(0, "")
    except configparser.NoSectionError:
        toolEntryArray[entryIndex].insert(0, "")

    slowRateEntryArray[entryIndex] = tk.Entry(master=root, width=10)
    slowRateEntryArray[entryIndex].grid(column=4, row=(entryIndex+1))
    try:
        if entryIndex < 10:
            toolname = ("TOOL_0" + (str(entryIndex + 1)))
        else:
            toolname = ("TOOL_" + (str(entryIndex + 1)))
        slowRateEntryArray[entryIndex].insert(0, config[toolname]['slowRate'])
    except KeyError:
        slowRateEntryArray[entryIndex].insert(0, "")
    except configparser.NoSectionError:
        slowRateEntryArray[entryIndex].insert(0, "")

    fastRateEntryArray[entryIndex] = tk.Entry(master=root, width=10)
    fastRateEntryArray[entryIndex].grid(column=6, row=(entryIndex+1))
    try:
        if entryIndex < 10:
            toolname = ("TOOL_0" + (str(entryIndex + 1)))
        else:
            toolname = ("TOOL_" + (str(entryIndex + 1)))
        fastRateEntryArray[entryIndex].insert(0, config[toolname]['fastRate'])
    except KeyError:
        fastRateEntryArray[entryIndex].insert(0, "")
    except configparser.NoSectionError:
        fastRateEntryArray[entryIndex].insert(0, "")
    entryIndex += 1
    root.update()
    root.update_idletasks()
joglength = tk.Entry(master=root, width=10)
joglength.grid(column=5, row=(entryIndex+1))
joglengthLabel.grid(row=(entryIndex+1), column=4)

grabMaxButton = tk.Button(root, text="Run File", width=10, command=grabMax)
grabMaxButton.grid(row=1+entryIndex, column=0)

useDataFile = tk.Button(root, text="Use Data File", width=10, command=exeDataFile)
useDataFile.grid(row=1+entryIndex, column=3)

tk.mainloop()
