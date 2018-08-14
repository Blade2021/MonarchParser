import fileinput
import sys
import configparser

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

# Initialise arrays for parsing
slowRateArray = ['2', '2', '2', '2', '2', '2', '2', '2', '2', '2']
fastRateArray = ['10', '10', '10', '10', '10', '10', '10', '10', '10', '10']
# Main Window
root = tk.Tk()
root.title("GCode File Parser - By Matt W.")
root.resizable(width=False, height=False)  # Disable resizing
indx = 0
slowRateLabel = ["", "", "", "", "", "", "", "", "", ""]
fastRateLabel = ["", "", "", "", "", "", "", "", "", ""]
file_path = filedialog.askopenfilename()

def toolAmount():
    tools = -1
    try:
        with fileinput.input(files=file_path, inplace=0) as file:
            for line in file:
                parentCheck = line.find("(")
                if parentCheck == 0:
                    toolCheck = line.find('T.')
                    if toolCheck >= 1:
                        tools += 1
        if tools < 0:
            exit("ERROR: No tools found")
    except IOError:
        print("File not found")
        exit(4)
    return tools-1


tools = toolAmount()

# Initialise rate labels
while indx < tools:
    slowRateLabel[indx] = tk.Label(root, text=("Slow Rate " + str(indx)), font='Times 12', borderwidth=3, width=12)
    slowRateLabel[indx].grid(row=indx+1, column=0)

    fastRateLabel[indx] = tk.Label(root, text=("Fast Rate " + str(indx)), font='Times 12', borderwidth=3, width=12)
    fastRateLabel[indx].grid(row=indx + 1, column=3)
    indx += 1
    root.focus_force()

# Execute Function: Runs values entered or from datafile to parse the file.
def execute():
    root.withdraw()
    y = 0
    rate = 0
    value = "Z-"
    toolIndex = -1
    indx = 0

    # Add F key before the feed rate
    while indx < tools:
        slowRateArray[indx] = str('F' + slowRateArray[indx])
        fastRateArray[indx] = str('F' + fastRateArray[indx])
        sys.stdout.write("   Tool #: " + str(indx) + '\n')
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
                if(file.filelineno() == 1):
                    f.write(line)
                    sys.stdout.write("Header: " + line)
                    continue
                # Remove comments from the file
                parentCheck = line.find("(")
                if parentCheck != -1:  # Ignore the first line of the program
                    if parentCheck == 0:
                        continue
                    else:
                        line = line[0:parentCheck]
                        line = line + "\n"

                # Remove Feed rates if applicable
                feedCheck = line.find('F')
                if feedCheck >= 1:
                    line = line[0:feedCheck]
                    line += "\n"

                line = line.replace("G23", "G03")  # Change G23 to G03
                line = line.replace("G22", "G02")  # Change G22 to G02

                # Search document for P codes and remove them
                pcodeCheck = line.find('P')
                if pcodeCheck >= 1:
                    line = line[0:pcodeCheck]
                    line += "\n"
                # Look for tool changes
                toolCheck = line.find('T')
                if toolCheck >= 1:
                    toolIndex += 1
                    if toolIndex >= len(slowRateArray):
                        toolIndex = 0

                # Search document line by line for Z negatives
                if value in line:
                    # Skip adding a feed rate if line has G00 in it
                    if "G00" in line:
                        continue
                    # Add a double check to the next line to see if its a G01
                    y = file.filelineno() + 1
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
                # Check line number vs y, and if G01 in line ( Switch to fast rate )
                if (file.filelineno() == y) and ("G01" in line):
                    feedCheck = line.find('F')
                    if feedCheck >= 1:
                        line = line[0:feedCheck]
                    if rate == 1:
                        line = line.rstrip('\n')
                        line += fastRateArray[toolIndex] + "\n"
                        rate = 2
                # Write line to file
                # with fileinput.input(files=newFile, inplace=1) as writeFile:
                # sys.stdout.write(line)
                f.write(line)
        sys.stdout.write('\n')
        f.close()
        fileinput.close()
    # If file cannot be opened
    except IOError:
        exit(4)
    sys.stdout.write("File parsed successfully\n\n")
    exit()

def grabMax():
    indx = 0
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
            # Grab values from entry array
            slowRateArray[indx] = str(slowRateEntryArray[indx].get())
            # Save values to data.ini if allowed and NOT blank!
            if saveVar == 1 and slowRateArray[indx] is not "":
                try:
                    toolname = ("TOOL_" + (str(indx+1)))
                    config[toolname]['SlowRate'] = slowRateArray[indx]
                except KeyError:
                    config.add_section(toolname)
                    config.set(toolname, 'SlowRate', slowRateArray[indx])
        except ValueError:
            indx += 1
            slowRateArray[indx] = '2'
            continue
        indx += 1
    indx = 0
    while indx < tools:
        try:
            # Grab values from entry array
            fastRateArray[indx] = str(fastRateEntryArray[indx].get())
            # Save values to data.ini if allowed and NOT blank!
            if saveVar == 1 and fastRateArray[indx] is not "":
                try:
                    toolname = ("TOOL_" + (str(indx + 1)))
                    config.set(toolname, 'FastRate', fastRateArray[indx])
                except KeyError:
                    config.add_section(toolname)
                    config.set(toolname, 'FastRate', slowRateArray[indx])
        except ValueError:
            indx += 1
            fastRateArray[indx] = '8'
            continue
        indx += 1

    with open('data.ini', 'w') as configfile:
        config.write(configfile)
    execute()


def exeDataFile():
    config = configparser.ConfigParser()
    config.read('data.ini')
    arrayindex = 0
    try:
        while arrayindex < tools:
            toolname = ("TOOL_" + (str(arrayindex + 1)))
            try:
                slowRateArray[arrayindex] = config.get(toolname, 'SlowRate')
                fastRateArray[arrayindex] = config.get(toolname, 'FastRate')
                # fastRateArray[arrayindex] = config[toolname]['FastRate']
            except configparser.NoSectionError:
                sys.stdout.write("ERROR:" + toolname + " not found in data.ini\n\n")
                exit(6)
            arrayindex += 1
    except IOError:
        print("something went wrong")
        exit()
    execute()


# Initialise entry arrays
slowRateEntryArray = ["", "", "", "", "", "", "", "", "", ""]
fastRateEntryArray = ["", "", "", "", "", "", "", "", "", ""]
# Configure entry arrays
entryIndex = 0
while entryIndex < toolAmount():
    slowRateEntryArray[entryIndex] = tk.Entry(master=root, width=10)
    slowRateEntryArray[entryIndex].grid(column=2, row=(entryIndex+1))

    fastRateEntryArray[entryIndex] = tk.Entry(master=root, width=10)
    fastRateEntryArray[entryIndex].grid(column=4, row=(entryIndex+1))
    entryIndex += 1
    root.update()
    root.update_idletasks()
    loop = 1

grabMaxButton = tk.Button(root, text="Enter", width=10, command=grabMax)
grabMaxButton.grid(row=12, column=0)

useDataFile = tk.Button(root, text="Use Data File", width=10, command=exeDataFile)
useDataFile.grid(row=12, column=3)

tk.mainloop()
