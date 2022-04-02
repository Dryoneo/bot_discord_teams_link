### Parametres : ###
### sys.argv[1] : prenom d'un eleve de la classe ###
### sys.argv[2] : nom d'un eleve de la classe ###
### sys.argv[3] : identifiant du channel discord de la classe ###
### sys.argv[4] : classe ###
### sys.argv[5] : TOKEN du bot ###


from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from time import sleep
from datetime import datetime
import sys
from Scrapper import Scrapper
from SysUtils import SysUtils
import requests as rq
import json
    
def sendMessage(courseName, message, screenshotNextWeekPath=None):
    data = {
        "embeds": [{
            "title": courseName,
            'thumbnail': {'url': 'attachment://' + screenshotNextWeekPath},
            "description": message,
            "color": int(1127128),
            "footer": {'text': 'Made by Lucas'},
            "timestamp": str(datetime.utcnow())
        }]
    }

    result = rq.post('https://discord.com/api/webhooks/959745986815754280/IEf_713VEibpDtCSCDOpMdjAsMp4mz3EXh9dbTYHSjTYk9l_4VVMeVnshk3oQz9cFz8B', data=json.dumps(data), headers={"Content-Type": "application/json"})

    try:
        result.raise_for_status()
    except rq.exceptions.HTTPError as err:
        print(err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))

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

    date_now = datetime.now()
    if(date_now.isoweekday() == 5 and date_now.hour == 18):
        isSchool, screenshotNextWeekPath = iAmTheScrapper.isSchoolPeriodNextWeek(browser)
        if(isSchool):
            sendMessage("@everyone\nSemaine prochaine : **Ecole**", screenshotNextWeekPath)
        else:
            sendMessage("@everyone\nSemaine prochaine : **Entreprise**")  
        sys.exit()


    iAmTheScrapper.goToPlanning(browser, date_now.strftime("%m-%d-%Y") )
    nameScreenshot = iAmTheScrapper.takeScreenshot(browser, date_now.strftime("%m-%d-%Y"))
    urlTeams, urlMLB, courseName, alreadyGetted = iAmTheScrapper.getLastLinkTeams(browser)
    ### Cleanup ###
    iAmUrWaiter.cleanUp(browser)
    count = count + 1
    if count == 5:
        print("Can't get new link, abort.\n")
        browser.close();
        sys.exit()
    sleep(5)


if(urlTeams != None) or ((courseName != None) and (alreadyGetted != True)):
    
    # If we have a new cours at this hours
    if(courseName != None) and (alreadyGetted != True):
        print("Sending the MLB link : " + urlMLB + " in the class room channel " + sys.argv[4] + "...")
        message = "Le lien MLB : " + urlMLB

    # If we get an url teams (then we are in distancing)
    if(urlTeams != None):
        print("Sending the teams link : " + urlTeams + " in the class room channel " + sys.argv[4] + "...")
        message = "Le lien Teams : " + urlTeams

    sendMessage(courseName, message, nameScreenshot)
