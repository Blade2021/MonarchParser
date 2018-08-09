import fileinput
import sys
import configparser

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

# Initialise arrays for parsing
slowRateArray = ['2', '2', '2', '2', '2', '2', '2', '2', '2', '2']
fastRateArray = ['10', '10', '10', '10', '10', '10', '10', '10', '10', '10']
global saveVar
saveVar = 0
# Main Window
root = tk.Tk()
root.title("GCode File Parser - By Matt W.")
root.resizable(width=False, height=False)  # Disable resizing

# Initialise rate labels
slowRate1 = tk.Label(root, text="Slow Rate 1", font='Times 12', borderwidth=3, width=12)
slowRate1.grid(row=1, column=0)
slowRate2 = tk.Label(root, text="Slow Rate 2", font='Times 12', borderwidth=3, width=12)
slowRate2.grid(row=2, column=0)
slowRate3 = tk.Label(root, text="Slow Rate 3", font='Times 12', borderwidth=3, width=12)
slowRate3.grid(row=3, column=0)
slowRate4 = tk.Label(root, text="Slow Rate 4", font='Times 12', width=12)
slowRate4.grid(row=4, column=0)
slowRate5 = tk.Label(root, text="Slow Rate 5", font='Times 12', borderwidth=3, width=12)
slowRate5.grid(row=5, column=0)
slowRate6 = tk.Label(root, text="Slow Rate 6", font='Times 12', borderwidth=3, width=12)
slowRate6.grid(row=6, column=0)
slowRate7 = tk.Label(root, text="Slow Rate 7", font='Times 12', borderwidth=3, width=12)
slowRate7.grid(row=7, column=0)
slowRate8 = tk.Label(root, text="Slow Rate 8", font='Times 12', width=12)
slowRate8.grid(row=8, column=0)
slowRate9 = tk.Label(root, text="Slow Rate 9", font='Times 12', width=12)
slowRate9.grid(row=9, column=0)
slowRate10 = tk.Label(root, text="Slow Rate 10", font='Times 12', width=12)
slowRate10.grid(row=10, column=0)
fastRate1 = tk.Label(root, text="Fast Rate 1", font='Times 12', width=12)
fastRate1.grid(row=1, column=3)
fastRate2 = tk.Label(root, text="Fast Rate 2", font='Times 12', width=12)
fastRate2.grid(row=2, column=3)
fastRate3 = tk.Label(root, text="Fast Rate 3", font='Times 12', width=12)
fastRate3.grid(row=3, column=3)
fastRate4 = tk.Label(root, text="Fast Rate 4", font='Times 12', width=12)
fastRate4.grid(row=4, column=3)
fastRate5 = tk.Label(root, text="Fast Rate 5", font='Times 12', width=12)
fastRate5.grid(row=5, column=3)
fastRate6 = tk.Label(root, text="Fast Rate 6", font='Times 12', width=12)
fastRate6.grid(row=6, column=3)
fastRate7 = tk.Label(root, text="Fast Rate 7", font='Times 12', width=12)
fastRate7.grid(row=7, column=3)
fastRate8 = tk.Label(root, text="Fast Rate 8", font='Times 12', width=12)
fastRate8.grid(row=8, column=3)
fastRate9 = tk.Label(root, text="Fast Rate 9", font='Times 12', width=12)
fastRate9.grid(row=9, column=3)
fastRate10 = tk.Label(root, text="Fast Rate 10", font='Times 12', width=12)
fastRate10.grid(row=10, column=3)


# Excute Function: Runs values entered or from datafile to parse the file.
def execute():
    root.withdraw()
    y = 0
    rate = 0
    value = "Z-"
    toolIndex = -1
    indx = 0
    # Add F key before the feed rate
    while indx < 10:
        slowRateArray[indx] = str('F' + slowRateArray[indx])
        fastRateArray[indx] = str('F' + fastRateArray[indx])
        indx += 1  # increment the array index
    # Trigger open file window
    file_path = filedialog.askopenfilename()
    try:
        with fileinput.input(files=file_path, backup=".bak", inplace=1) as file:
            for line in file:
                if(file.filelineno() == 1):
                    sys.stdout.write(line)
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
                        # Add slow feed rate to first occurance
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
                sys.stdout.write(line)

        fileinput.close()
    # If file cannot be opened
    except IOError:
        print("File not found")
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
    while indx < 10:
        try:
            slowRateArray[indx] = str(slowRateEntryArray[indx].get())
            if saveVar == 1 and slowRateArray[indx] is not "":
                try:
                    toolname = ("TOOL_" + (str(indx+1)))
                    config[toolname]['SlowRate'] = slowRateArray[indx]
                except ValueError:
                    print("Something went wrong")
        except ValueError:
            indx += 1
            slowRateArray[indx] = '2'
            continue
        indx += 1
    indx = 0
    while indx < 10:
        try:
            fastRateArray[indx] = str(fastRateEntryArray[indx].get())
            if saveVar == 1 and fastRateArray[indx] is not "":
                try:
                    toolname = ("TOOL_" + (str(indx + 1)))
                    config.set(toolname, 'FastRate', fastRateArray[indx])
                except ValueError:
                    print("Something went wrong")
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
        while arrayindex < 10:
            toolname = ("TOOL_" + (str(arrayindex + 1)))
            slowRateArray[arrayindex] = config[toolname]['SlowRate']
            fastRateArray[arrayindex] = config[toolname]['FastRate']
            arrayindex += 1
    except ValueError:
        print("something went wrong")
        exit()
    execute()

# Initialise entry arrays
slowRateEntryArray = ["", "", "", "", "", "", "", "", "", ""]
fastRateEntryArray = ["", "", "", "", "", "", "", "", "", ""]
# Configure entry arrays
slowRateEntryArray[0] = tk.Entry(master=root, width=10)
slowRateEntryArray[0].grid(column=2, row=1)

slowRateEntryArray[1] = tk.Entry(master=root, width=10)
slowRateEntryArray[1].grid(column=2, row=2)

slowRateEntryArray[2] = tk.Entry(master=root, width=10)
slowRateEntryArray[2].grid(column=2, row=3)

slowRateEntryArray[3] = tk.Entry(master=root, width=10)
slowRateEntryArray[3].grid(column=2, row=4)

slowRateEntryArray[4] = tk.Entry(master=root, width=10)
slowRateEntryArray[4].grid(column=2, row=5)

slowRateEntryArray[5] = tk.Entry(master=root, width=10)
slowRateEntryArray[5].grid(column=2, row=6)

slowRateEntryArray[6] = tk.Entry(master=root, width=10)
slowRateEntryArray[6].grid(column=2, row=7)

slowRateEntryArray[7] = tk.Entry(master=root, width=10)
slowRateEntryArray[7].grid(column=2, row=8)

slowRateEntryArray[8] = tk.Entry(master=root, width=10)
slowRateEntryArray[8].grid(column=2, row=9)

slowRateEntryArray[9] = tk.Entry(master=root, width=10)
slowRateEntryArray[9].grid(column=2, row=10)

fastRateEntryArray[0] = tk.Entry(master=root, width=10)
fastRateEntryArray[0].grid(column=4, row=1)

fastRateEntryArray[1] = tk.Entry(master=root, width=10)
fastRateEntryArray[1].grid(column=4, row=2)

fastRateEntryArray[2] = tk.Entry(master=root, width=10)
fastRateEntryArray[2].grid(column=4, row=3)

fastRateEntryArray[3] = tk.Entry(master=root, width=10)
fastRateEntryArray[3].grid(column=4, row=4)

fastRateEntryArray[4] = tk.Entry(master=root, width=10)
fastRateEntryArray[4].grid(column=4, row=5)

fastRateEntryArray[5] = tk.Entry(master=root, width=10)
fastRateEntryArray[5].grid(column=4, row=6)

fastRateEntryArray[6] = tk.Entry(master=root, width=10)
fastRateEntryArray[6].grid(column=4, row=7)

fastRateEntryArray[7] = tk.Entry(master=root, width=10)
fastRateEntryArray[7].grid(column=4, row=8)

fastRateEntryArray[8] = tk.Entry(master=root, width=10)
fastRateEntryArray[8].grid(column=4, row=9)

fastRateEntryArray[9] = tk.Entry(master=root, width=10)
fastRateEntryArray[9].grid(column=4, row=10)


grabMaxButton = tk.Button(root, text="Enter", width=10, command=grabMax)
grabMaxButton.grid(row=12, column=0)

grabMaxButton = tk.Button(root, text="Use Data File", width=10, command=exeDataFile)
grabMaxButton.grid(row=12, column=3)

# Main loop
tk.mainloop()
