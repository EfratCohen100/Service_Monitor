import platform
import datetime
import os
import sys
import time
import subprocess
from ast import literal_eval
from datetime import datetime
import psutil


fileServiceListName= "serviceList.log"
fileStatusLogName = "status_Log.log"


# this function write of file serviceList.txt the name of services and their status - on Windows
#the function get input name of file and return output list of information that we want to get
def Windows_WriteFileLog(logServiceFile):
    listOfFileWindows = {}
    log_file = open(logServiceFile, "a")
    dateNow = datetime.now()
    log_file.write("{}\n".format(dateNow))
    for service in psutil.win_service_iter():
        serviceName = service.name()
        serviceStatus = service.status()
        line_to_write = serviceName +" " +serviceStatus + "\n"
        log_file.write(line_to_write)
        listOfFileWindows[serviceName] = serviceStatus
    log_file.write("\n")
    log_file.close()
    return listOfFileWindows

# this function write of file serviceList.txt the name of services and their status - on Linux
#the function get input name of file and return output list of information that we want to get
def Linux_WriteFileLog(logServiceFile):
  listOfFileLinux = {}
  output = subprocess.check_output(["service", "--status-all"])
  date = datetime.now()
  serviceFile = open(logServiceFile, "a")
  serviceFile.write("{}\n".format(date))
  for line in output.decode().split('\n'):
    serviceName = line[8:]
    serviceStatus = line[3:4]
    line2write = "{} {}\n".format(serviceName,serviceStatus)
    serviceFile.write(line2write)
    listOfFileLinux[serviceName] = serviceStatus
  serviceFile.write("\n")
  serviceFile.close()
  return listOfFileLinux

# this function get input file Status_Log and history list of all the services and new list that contains
#information about the services and platform.
#The function checks whether there is a change in information between the two arrays and each
# change it prints to the screen and writes the same change within the file Status_Log.
def Create_FileStatusLog_Diff(log_file, listHistory, listChange, checkPlatform):
    for serviceNameKey, valueChanged in listHistory.items():
        dateChange = datetime.now()
        if serviceNameKey not in listChange:
            lineChange = "Service {} is found at listHistory but not listChange." .format(serviceNameKey)
            print(lineChange)
            log_file.write(lineChange + "\n")
            log_file.flush()
        elif valueChanged != listChange[serviceNameKey]:
            if checkPlatform == "Windows":
                lineChange = "in time: {}: Service '{}' changed status from '{}' to '{}'".format(dateChange, serviceNameKey, valueChanged, listChange[serviceNameKey])
            else:
                firstStatus = valueChanged
                secondStatus = listChange[serviceNameKey]
                if firstStatus == "+":
                    firstStatus = "running"
                else:
                    firstStatus = "stopped"

                if secondStatus == "+":
                    secondStatus = "running"
                else:
                    secondStatus = "stopped"
                lineChange = "in time: {}: Service '{}' changed status from '{}' to '{}'".format(dateChange, serviceNameKey, firstStatus,secondStatus)
            print(lineChange)
            log_file.write(lineChange + "\n")
            log_file.flush()

#This function check if the files exist in path.
#If files exist, the function deletes these files to create new files.
def Check_exist_file():
    if os.path.exists(fileServiceListName):
        os.remove(fileServiceListName)
    if os.path.exists(fileStatusLogName):
        os.remove(fileStatusLogName)

#This function receives two dates from the keyboard,
# creating a list of all the services that have changed between these two times.
#The function returns output an array of all changed servers.
def filter_status_log_by_dates(firstDate, secondDate):
    listOfServices = []
    with open(fileStatusLogName, "r") as log_status:
        for line in log_status:
            lineDateStr = line[9:28]
            dateLine = datetime.strptime(lineDateStr,"%Y-%m-%d %H:%M:%S")
            if lineDateStr == False:
                print("Error! Something went wrong with the time conversion process of status log")
                exit()
            if firstDate <= dateLine <= secondDate:
                listOfServices.append(line)

    return listOfServices

#This function return number of changes between the dates
def ManualMode(start_date, end_date):
    lines = filter_status_log_by_dates(start_date, end_date)
    print("The number of changes made between the times: " + str(len(lines)))
    for line in lines:
        print(line)

if __name__ == '__main__':
    checkPlatform = platform.system()
    mode = int(input("Welcome, please choose from your options your mode" " \n monitor 2 \n manual 1 \n exit 0 \n" "Your choice:"))
    if mode == 0:
        print("Exit now")
        exit()
    if mode == 2:
        print("selected monitor")
        Check_exist_file()
        try:
            timerSecond = input("Please select the number of seconds in each run:")
            strTime = "The program samples every {} seconds of all the services running on the computer".format(timerSecond)
            print(strTime)
        except:
            print("Error input!, please enter time  X again in seconds:")

 # -------------------------Windows Platform-------------------------
        if(checkPlatform == "Windows"):
          print("your platform is Windows")
          while 1:
            listLogHistory = Windows_WriteFileLog(fileServiceListName)
            time.sleep(float(timerSecond))
            listLogChange = Windows_WriteFileLog(fileServiceListName)
            file_Log = open(fileStatusLogName, "a")
            Create_FileStatusLog_Diff(file_Log, listLogHistory, listLogChange, checkPlatform)
        else:
#-------------------------Linux Platform-------------------------
            print("your platform is Linux")
            while 1:
              listLogHistory_Linux = Linux_WriteFileLog(fileServiceListName)
              time.sleep(float(timerSecond))
              listLogChange_Linux = Linux_WriteFileLog(fileServiceListName)
              file_Log = open(fileStatusLogName, "a")
              Create_FileStatusLog_Diff(file_Log, listLogHistory_Linux, listLogChange_Linux, checkPlatform)

    elif(mode == 1):
        print("You chose manual mode \n ")
        failed = True
        while failed:
            try:
                first_input = input("Please enter the first date (YYYY-mm-dd hh:mm:ss)")
                first_date = datetime.strptime(first_input, "%Y-%m-%d %H:%M:%S")
                failed = False
            except:
                print("Error! Invalid input, please enter correct date")

        failed = True
        while failed:
            try:
                second_input = input("Please enter the second date (YYYY-mm-dd hh:mm:ss) ")
                second_date = datetime.strptime(second_input, "%Y-%m-%d %H:%M:%S")
                failed = False
            except:
                print("Error! Invalid input, please enter correct date")
        ManualMode(first_date, second_date)

    else:
        print("Error! This option not exist.Please try again")