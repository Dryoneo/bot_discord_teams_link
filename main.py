### Script Python afin d'envoyer le lien du cours V2.1 ###

### Parametres : ###
### sys.argv[1] : prenom d'un eleve de la classe ###
### sys.argv[2] : nom d'un eleve de la classe ###
### sys.argv[3] : identifiant du channel discord de la classe ###
### sys.argv[4] : classe ###
### sys.argv[5] : TOKEN du bot ###


from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import datetime
import discord
import sys
import os
import re
import csv

### Go to class's planning ###
def GoToPlanning(browser):
    count = 0
    url = 'https://edtmobiliteng.wigorservices.net//WebPsDyn.aspx?action=posEDTBEECOME&serverid=C&Tel=' + sys.argv[1] + '.' + sys.argv[2] + '&date=' + datetime.datetime.now().strftime("%m-%d-%Y")
    browser.get(url)
    while True:
        try:
            WebDriverWait(browser,10).until(EC.presence_of_element_located((By.ID, "DivBody")))
            break
        except:
            print("Waiting for loading page, method : GoToPlanning()\n")
            sleep(3)
            count = count + 1
            if count == 5:
                print("Can't reach planning. method : GoToPlanning()\n")
                CleanUp(browser)
                sys.exit()
                
### Get course link ###
def GetLastLinkTeams(browser):
    try:
        TakeScreenshot(browser)
        links = browser.find_elements(By.CSS_SELECTOR, "a[href^='https://edtmobiliteng.wigorservices.net']")
        if(len(links)>0):
            last_link = links[len(links) - 8]

            # Get parent element to retrieve course name, if is not distancing we dont return anything
            parent_element = last_link.find_element(By.XPATH, "./../..")
            global course_name_element
            course_name_element = GetCourseName(parent_element.get_attribute("innerHTML"))
            if isDistancingCourse(course_name_element) is False: return None
            course_name_element = course_name_element.replace("DISTANCIEL", "").replace("&amp;", "&")
           
            
            browser.get(last_link.get_attribute('href'))
            sleep(2)
            url_teams = browser.current_url
            if(not isAlreadySent(url_teams)):
                # Display the alert box to open Teams directly
                url_teams = url_teams.replace('&suppressPrompt=true', '&suppressPrompt=false')
                SaveLink(url_teams)
                print("Course : " + course_name_element)
                print("We got a new link : " + url_teams)
                return url_teams
            else:
                print("We already have this link : " + url_teams)
    except Exception as e:
        print("An error occured, method : GetLastLinkTeams() -> ", e, "\n")
        return
    return

### Check if teams link has been already sent ###
def isAlreadySent(url_teams):
    try:
        file = open(sys.argv[4] + "/url_teams.txt", "r")
        for url in file:
            if(url[0:333] == url_teams[0:333]):
                return True
    except:
        print("The file doesnt exist, method : isAlreadySent()\n")
    return False
    
### Save the new teams link in the file ###
def SaveLink(url_teams):
    file = open("/home/ubuntu/bot_discord/" + sys.argv[4] + "/url_teams.txt", 'a+')
    file.write(url_teams + "\n")
    
### Take a screenshot of the planning ###
def TakeScreenshot(browser):
    global name_screenshot
    name_screenshot = "/home/ubuntu/bot_discord/" + sys.argv[4] + "/edt_" + datetime.datetime.today().strftime("%m-%d-%Y") + ".png"
    browser.save_screenshot(name_screenshot)
    print("Screenshot " + name_screenshot + " saved.\n")
    
### Get the course name ###
def GetCourseName(string_element):
    return string_element.split('<div class="Presence">')[0] + string_element.split('</div>')[-1]
    
### Get the course name ###
def isDistancingCourse(course_name):
    return True if "DISTANCIEL" in course_name else False
    
### Get link of ressources MyLearningBox with the course name ###
def GetLinkMLB(course_name_element):
    try:
        file = open("./dict_courses.csv")
        reader = csv.reader(file, delimiter = ';')
        for course in reader:
            if(course_name_element[0:10] in course[0]):
                global course_name
                course_name = course[0]
                print("The MLB link : " + course[1] + "\n")
                return course[1]
    except:
        print("The file doesnt exist")
    return None
    
### Cleanup server ###
def CleanUp(browser):
    browser.close()
    os.system('pkill firefox')
    print("Server cleanup done.\n")

    
### Part 0 : Check passed args
if(len(sys.argv) != 6):
    print("Please use this program with these 5 necessary arguments :")
    print("python3 main.py firstname lastname id_discord_chanel class_number token_discord_bot\n")
    exit()

### Part 1 : Go to planning to get the last new teams link ###
count = 0
while link_teams == None:
    print("Browser init.")  
    options = Options()
    options.headless = True
    print("Browser starting...\n")
    browser = webdriver.Firefox(options=options)
    GoToPlanning(browser)
    link_teams = GetLastLinkTeams(browser)
    link_mlb = GetLinkMLB(course_name_element)
    ### Cleanup ###
    CleanUp(browser)
    count = count + 1
    if count == 5:
        print("Can't get new link, abort.\n")
        sys.exit()


if(link_teams != None):
    ### Part 2 : Discord bot will send the teams link in the channel room ###  
    print("Bot discord init.")  
    client = discord.Client()
    @client.event
    async def on_ready():
        print("Bot discord starting..")
        channel = client.get_channel(int(sys.argv[3]))
        print("Bot discord is ready.\n")
        """
        print("Send the planning : " + name_screenshot + " in the class room channel " + sys.argv[4] + "\n")
        await channel.send(file=discord.File(name_screenshot))
        print("Ok.")
        """
        print("Sending the teams link : " + link_teams + " in the class room channel " + sys.argv[4] + "...")
        await channel.send("@everyone\nLe lien du cours " + course_name + ": " + link_teams + "\nLe lien MLB : " + link_mlb)
        print("Ok.")
        await client.close()
        print("Bot disconnected.\n")
        sys.exit()
    client.run(sys.argv[5])
