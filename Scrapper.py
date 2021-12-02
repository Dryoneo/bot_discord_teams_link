from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import sys
import datetime
import pendulum
from SysUtils import SysUtils

class Scrapper:
    iAmUrWaiter = SysUtils()
    ### Load Page ###
    def loadPage(self, browser, url, idToFind):
        browser.get(url)
        try:
            wait = WebDriverWait(browser, 15)
            condition = EC.presence_of_element_located((By.ID, idToFind))
            wait.until(condition)
        except TimeoutException as e:
            print(e)
            print("Can't load page with url : " + url + "\n")
            self.iAmUrWaiter.cleanUp(browser)
            sys.exit()

    ### Go to class's planning ###
    def goToPlanning(self, browser, date):
        url = 'https://edtmobiliteng.wigorservices.net//WebPsDyn.aspx?action=posEDTBEECOME&serverid=C&Tel=' + sys.argv[1] + '.' + sys.argv[2] + '&date=' + date
        idToFind = 'DivBody'
        self.loadPage(browser, url, idToFind)
                
    ### Get course link ###
    def getLastLinkTeams(self, browser):
        try:
            links = browser.find_elements(By.CSS_SELECTOR, "a[href^='https://edtmobiliteng.wigorservices.net']")
            if(len(links)>0):
                # To get the Principal Link Teams
                crossLink = links[len(links) - 8]

                # Get parent element to retrieve course name
                parentElement = crossLink.find_element(By.XPATH, "./../..")
                courseNameElement = self.getCourseName(parentElement.get_attribute("innerHTML"))
                
                # Go on the link in planning, to acces to the real link  of Teams
                url = crossLink.get_attribute('href')
                idToFind = 'container'
                self.loadPage(browser, url, idToFind)
                urlTeams = browser.current_url

                # If course not already sent/saved, we gonna save the link
                if(not self.iAmUrWaiter.isAlreadySent(urlTeams)):
                    # Display the alert box to open Teams directly
                    urlTeams = urlTeams.replace('&suppressPrompt=true', '&suppressPrompt=false')
                    self.iAmUrWaiter.saveLink(urlTeams)
                    # If is not distancing we dont return anything
                    isDistancing = True if self.isDistancingCourse(courseNameElement) else False
                    courseNameElement = courseNameElement.replace("DISTANCIEL", "").replace("&amp;", "&")
                    urlMLB, courseName = self.iAmUrWaiter.getLinkMLB(courseNameElement)
                    if isDistancing is False: return None, urlMLB, courseName, None
                    print("Course : " + courseNameElement)
                    print("We got a new link : " + urlTeams)
                    return urlTeams, urlMLB, courseName, None
                else:
                    print("We already have this link : " + urlTeams)
        except Exception as e:
            print("An error occured, method : getLastLinkTeams() -> ", e, "\n")
            return None, None, None, None
        return None, None, None, True

    ### Take a screenshot of the planning ###
    def takeScreenshot(self, browser, date):
        nameScreenshot = "/home/ubuntu/bot_discord/" + sys.argv[4] + "/edt_" + date + ".png"
        browser.save_screenshot(nameScreenshot)
        print("Screenshot " + nameScreenshot + " saved.\n")

    ### Get the course name ###
    def getCourseName(self, stringElement):
        return stringElement.split('<div class="Presence">')[0] + stringElement.split('</div>')[-1]

    ### Get the course name ###
    def isDistancingCourse(self, courseName):
        return True if "DISTANCIEL" in courseName else False

    ### Are we in a school or entreprise period next week ? ###
    def isSchoolPeriodNextWeek(self, browser):
        next_week = pendulum.now().next(pendulum.MONDAY).strftime('%Y-%m-%d')
        self.goToPlanning(browser, next_week)
        isNotSchool = browser.find_elements(By.XPATH, "//*[contains(text(), 'Pas de cours cette semaine')]")
        if(isNotSchool):

            self.takeScreenshot(browser, next_week)
            return False, next_week
        return True, None