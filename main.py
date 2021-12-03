### Script Python afin d'envoyer le lien du cours V3.0.1 ###

### EVOLUTIONS ###
### 30min avant : donner la salle & bat + lien MLB ###
### 15min avant : donner le lien teams ###
### Dimanche soir vers 18h : donner planning de la semaine + jours en distanciel ###
### Vendredi soir vers 20h : dire si semaine pro entreprise ou ecole ###

### Parametres : ###
### sys.argv[1] : prenom d'un eleve de la classe ###
### sys.argv[2] : nom d'un eleve de la classe ###
### sys.argv[3] : identifiant du channel discord de la classe ###
### sys.argv[4] : classe ###
### sys.argv[5] : TOKEN du bot ###


from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from time import sleep
import discord
import datetime
import sys
from Scrapper import Scrapper
from SysUtils import SysUtils
    

def sendMessage(message):
    print("Bot discord init.")  
    client = discord.Client()
    @client.event
    async def on_ready():
        print("Bot discord starting..")
        channel = client.get_channel(int(sys.argv[3]))
        print("Bot discord is ready.\n")
            
        await channel.send(message)
        
        print("Ok.")
        await client.close()
        print("Bot disconnected.\n")
    client.run(sys.argv[5])  

def sendPlanning(screenshotNextWeekPath):
    print("Bot discord init.")  
    client = discord.Client()
    @client.event
    async def on_ready():
        print("Bot discord starting..")
        channel = client.get_channel(int(sys.argv[3]))
        print("Bot discord is ready.\n")
            
        await channel.send(file=discord.File(screenshotNextWeekPath))
        
        print("Ok.")
        await client.close()
        print("Bot disconnected.\n")
    client.run(sys.argv[5])  

### Part 0 : Check passed args
if(len(sys.argv) != 6):
    print("Please use this program with these 5 necessary arguments :")
    print("python3 main.py firstname lastname id_discord_chanel class_number token_discord_bot\n")
    exit()

count = 0
urlTeams = None
urlMLB = None
iAmTheScrapper = Scrapper()
iAmUrWaiter = SysUtils()

### Part 1 : Go to planning to get the last new teams link ###
# While cuz sometimes selenium get first WebElement insted of the last, then it doesnt work well
# Then we gonna retry 5 times until we give up
while (urlTeams == None) and (urlMLB == None):
    print("Browser init.")  
    options = Options()
    options.headless = True
    print("Browser starting...")
    browser = webdriver.Firefox(options=options)
    print("Browser is started.\n")

    date_now = datetime.datetime.now()
    if(date_now.isoweekday() == 5 and date_now.hour == 18):
        isSchool, screenshotNextWeekPath = iAmTheScrapper.isSchoolPeriodNextWeek(browser)
        if(isSchool):
            sendMessage("@everyone\nSemaine prochaine : **Ecole**")
            sendPlanning(screenshotNextWeekPath)
        else:
            sendMessage("@everyone\nSemaine prochaine : **Entreprise**")  


    iAmTheScrapper.goToPlanning(browser, date_now.strftime("%m-%d-%Y") )
    iAmTheScrapper.takeScreenshot(browser, date_now.strftime("%m-%d-%Y"))
    urlTeams, urlMLB, courseName, alreadyGetted = iAmTheScrapper.getLastLinkTeams(browser)
    ### Cleanup ###
    iAmUrWaiter.cleanUp(browser)
    count = count + 1
    if count == 5:
        print("Can't get new link, abort.\n")
        sys.exit()
    sleep(5)

if(urlTeams != None) or ((courseName != None) and (alreadyGetted != True)):
    ### Part 2 : Discord bot will send datas in the channel room ### 

    message = "@everyone Cours : " + courseName
    
    # If we have a new cours at this hours
    if(courseName != None) and (alreadyGetted != True):
        print("Sending the MLB link : " + urlMLB + " in the class room channel " + sys.argv[4] + "...")
        message = message + "\nLe lien MLB : " + urlMLB

    # If we get an url teams (then we are in distancing)
    if(urlTeams != None):
        print("Sending the teams link : " + urlTeams + " in the class room channel " + sys.argv[4] + "...")
        message = message + "\nLe lien Teams : " + urlTeams

    sendMessage(message)
