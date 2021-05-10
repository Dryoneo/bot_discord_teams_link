### Script Python afin d'envoyer le lien du cours V1.1 ###

### Améliorations possibles : ###
### Au lieu de chercher le lien se trouvant à la position X et Y selon le jour/heure ###
### prendre le dernier lien teams du code source ###

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

### Dirige le navigateur vers le planning de la classe ###
### Param browser : Le navigateur headless ###  
def go_to_planning(browser):
    browser.get('https://edtmobiliteng.wigorservices.net//WebPsDyn.aspx?action=posEDTBEECOME&serverid=C&Tel=' + sys.argv[1] + '.' + sys.argv[2] + 'date=' + strftime("%m-%d-%Y"))
    while True:
        try:
            WebDriverWait(browser,10).until(EC.presence_of_element_located((By.ID, "DivBody")))
            break
        except:
            sleep(3)
            
### Récupération du lien du cours ###
### Param browser : Le navigateur headless ###  
### Avant tout on récupère le cours actuel à l'aide de sa position dans la page ###
### -> Chaque heure/jour possede une position spécifique sur beecome.io ###
def get_link_teams(browser):
    css_top_heure = {8 : "115.15%",
                 9 : "125.15%",
                 10 : "135.15%",
                 11 : "145.15%",
                 13 : "165.15%",
                 14 : "175.15%",
                 15 : "185.15%",
                 16 : "195.15%",
                 17 : "205.15%"}
    css_left_jour = {1 : "103.12%",
                     2 : "122.52%",
                     3 : "141.92%",
                     4 : "161.32%",
                     5 : "180.72%",}
    heure = datetime.datetime.today().hour
    jour = datetime.datetime.today().isoweekday()
    top_heure = css_top_heure.get(heure)
    left_jour = css_left_jour.get(jour)
    try:
        div = browser.find_element_by_css_selector("div[class='Case'][style*='top: " + top_heure + "; left: "  + left_jour + ";']")
        take_screenshot(browser)
        link = div.find_element(By.CSS_SELECTOR, "a[href^='https://edtmobiliteng.wigorservices.net']")  
        browser.get(link.get_attribute('href'))
        sleep(2)
        return browser.current_url
    except:
        print("Aucun cours pour la classe : " + sys.argv[4] + " à la date : " + datetime.datetime.today())
        return
    
### Prends un screenshot du planning ###
def take_screenshot(browser):
    global name_screenshot
    name_screenshot = sys.argv[4] + "/edt_" + datetime.datetime.today().strftime("%m-%d-%Y") + ".png"
    browser.save_screenshot(name_screenshot)
    

### Partie 1 : Navigation vers le cours actuel afin de prendre l'URL ###    
options = Options()
options.headless = True
browser = webdriver.Firefox(options=options)
go_to_planning(browser)
link_teams = get_link_teams(browser)
# Affiche l'alert box pour ouvrir Teams directement
link_teams.replace('&suppressPrompt=true', '&suppressPrompt=false')

### Nettoyage ###
browser.close()
os.system('pkill firefox')

if(link_teams != None):
    ### Partie 2 : Bot Discord qui va envoye l'URL dans le salon de la classe ###    
    client = discord.Client()
    @client.event
    async def on_ready():
        channel = client.get_channel(int(sys.argv[3]))
        print("Le bot discord est prêt\n")
        print("Envoi du planning : " + name_screenshot + " dans le channel de la classe " + sys.argv[4] + "\n")
        print("Envoi du lien du cours : " + link_teams + " dans le channel de la classe " + sys.argv[4] + "\n")
        await channel.send(file=discord.File(name_screenshot))
        await channel.send("Le lien du cours : " + link_teams)
        await client.logout()
        exit()
    client.run(sys.argv[5])