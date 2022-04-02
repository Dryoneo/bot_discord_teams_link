import sys
import csv
import os

class SysUtils:  
    ### Check if teams link has been already sent ###
    def isAlreadySent(self, urlTeams):
        try:
            file = open("./" + sys.argv[4] + "/urlTeams.txt", "r")
            for url in file:
                if(url[0:333] == urlTeams[0:333]):
                    return True
        except:
            print("The file doesnt exist, method : isAlreadySent()\n")
        return False
    
    ### Save the new teams link in the file ###
    def saveLink(self, urlTeams):
        file = open("./" + sys.argv[4] + "/urlTeams.txt", 'a+')
        file.write(urlTeams + "\n")
    
    ### Get link of ressources MyLearningBox with the course name ###
    def getLinkMLB(self, courseNameElement):
        try:
            file = open("./dict_courses.csv", encoding='utf-8')
            reader = csv.reader(file, delimiter = ';')
            for course in reader:
                if(courseNameElement[0:10].lower().lstrip() in course[0].lower()):
                    courseName = course[0]
                    print("The MLB link : " + course[1] + "\n")
                    return course[1], courseName
                if(courseNameElement[0:10].lstrip() in course[0]):
                    courseName = course[0]
                    print("The MLB link : " + course[1] + "\n")
                    return course[1], courseName
        except Exception as e:
            print("An error occured : ", e)
        return None, None
        
    ### Cleanup server ###
    def cleanUp(self, browser):
        browser.close()
        os.system('pkill firefox')
        print("Server cleanup done.\n")
