
# bot.py
import threading
import ctypes
import os
import requests # request img from web
import shutil # save img locally
import logging
from logging.handlers import RotatingFileHandler
from PIL import Image
# import pystray
# import subprocess
import discord
from dotenv import load_dotenv
# from github import Github
#from ClubOrionPosterBotDropBoxIntegration import upload_to_dropbox

#Set up Logging
logger=logging.getLogger("posterbot_logger")
logger.setLevel(logging.INFO)

consoleHandler = logging.StreamHandler()
consoleFormatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
consoleHandler.setFormatter(consoleFormatter)
logger.addHandler(consoleHandler)

fileHandler = RotatingFileHandler("ClubOrionPosterBot_Log.log", maxBytes=1024, backupCount=2)
fileHandler.setFormatter(consoleFormatter)
logger.addHandler(fileHandler)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
LEADERID = int(os.getenv('DISCORD_GUILD_LEADER'))
DBOXTOKEN = os.getenv('DROPBOX_TOKEN')

intents = discord.Intents.default()
client = discord.Client(command_prefix='!', intents=intents)

# ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
# console_toggle = False

# def trayIcon():
#     #Set up System Tray Icon
#     iconImage = Image.open("OrionPosterBot-Icon.png")

#     def raise_console(toggle):
#         """Brings up the Console Window."""
#         if toggle:
#             # Show console
#             ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 4)
#         else:
#             # Hide console
#             ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)


#     def showHideConsole(icon, item):
#         global console_toggle
#         console_toggle = not item.checked
#         raise_console(console_toggle)

#     def quitAppliction(icon, item):
#         icon.stop()
#         os._exit(1)

#     icon = pystray.Icon("Club Orion Poster Bot", iconImage, menu=pystray.Menu(
#         pystray.MenuItem("Show/Hide Console", showHideConsole, checked=lambda item: console_toggle),
#         pystray.MenuItem("Quit", quitAppliction)
#     ))
#     icon.run()

# threading.Thread(target=trayIcon).start()






@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            logger.info('Connected Sucessfully to the Club Orion/VRSL Server!')
            break

    logger.info(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

@client.event
async def on_message(message):
    print('Message recieved!')
    if message.author == client.user:
        return
    print('Message is not mine! Checking to see if it is a poster!')
    msg = message.content
    print('Content: ' + str(msg))
    formats=['.png', '.jpg', '.jpeg', '.jpg' , '.jpeg' ,'.jfif', '.bmp']
    valid_reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "❌"]
    channel = message.channel
    if channel.name == 'in-game-ads':
        logger.info('Message is from poster channel! Checking to see if valid')
        print(str(message.attachments))
        if len(message.attachments) > 0  or (any(ele in msg for ele in formats) and "https://" in msg):
            logger.info('Message atleast has an attachment')
            if len(message.attachments) > 0:
                logger.info('Second Check Passed!')
                split_v1 = str(message.attachments).split("filename='")[1]
                filename = str(split_v1).split("' ")[0]
                isValid = False
                for format in formats:
                    if filename.endswith(format):
                        isValid = True
                        logger.info('This attachment is valid!')
                if isValid == False:
                    logger.info("This attachment does not have a valid format")
                    return            
            await message.add_reaction("1️⃣")
            await message.add_reaction("2️⃣")
            await message.add_reaction("3️⃣")
            await message.add_reaction("4️⃣")
            await message.add_reaction("5️⃣")
            await message.add_reaction("6️⃣")
            await message.add_reaction("❌")



@client.event
async def on_raw_reaction_add(payload):
    logger.info("Someone posted a reaction!")
    
    #Are they reacting in the VRSL/Club Orion Guild?
    guild_id = payload.guild_id
    guild = discord.utils.find(lambda g : g.id == guild_id, client.guilds)
    if guild.name != GUILD:
        return
    #Are they AcChosen or a valid Moderator?
    modRole = discord.utils.get(guild.roles,name="Moderator")
    logger.info("ModRole Status: " + str(modRole))
    if payload.user_id != LEADERID and modRole not in payload.member.roles:
        logger.info("This user is not valid!")
        return
    errorP = "Image link not valid! Did not download!"
    errorPReply = "Sorry, your poster was not posted in a valid format! Please try again by simply uploading a .png file instead!"
    success = "Image uploaded sucessfully!"
    successReply = "Congrats! Your poster has been updated to Orion in position: "
    
    #Is the reaction inside the in-game-ads channel?
    chanID = payload.channel_id
    channel = client.get_channel(chanID)
    if channel.name != 'in-game-ads':
        return
    
    #Does the message have an attachment or image link?
    formats=['.png', '.jpg', '.jpeg', '.jpg' , '.jpeg' ,'.jfif', '.bmp']
    msgID = payload.message_id
    message = await channel.fetch_message(msgID)
    msg = message.content
    if (len(message.attachments) > 0 or (any(ele in msg for ele in formats) and "https://" in msg)) == False:
        logger.info("This message has no image to react to.")
        return
    if len(message.attachments) > 0:
                split_v1 = str(message.attachments).split("filename='")[1]
                filename = str(split_v1).split("' ")[0]
                isValid = False
                for format in formats:
                    if filename.endswith(format):
                        isValid = True
                if isValid == False:
                    logger.info("This attachment does not have a valid format")
                    return 

    #Is the reaction a valid reaction emoji?
    valid_reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "❌"]
    reactionEmoji = payload.emoji.name
    if any(ele in reactionEmoji for ele in valid_reactions) == False:
        return
    logger.info("Valid Reaction!")

    #Did AccChosen deny the request with ❌ ?
    if reactionEmoji == valid_reactions[6]:
        logger.info("This poster request has been denied!")
        await message.reply("Sorry, your poster request has been denied. Please try again later!")
        return
    

    #ATTEMPT TO DOWNLOAD:
    else:
        if (any(ele in msg for ele in formats) and "https://" in msg): #if has image link
            try:
                sep = "https://"
                url = sep + msg.partition(sep)[2]
                isValid = False
                f = "format"
                for format in formats:
                    if format in url:
                        url = url.partition(format)[0] + url.partition(format)[1]
                        isValid = True
                        f = format
                        break
                if isValid == False:
                    logger.info(errorP)
                    await message.reply(errorPReply)
                    return
                
                #by this point the link should be valid, attempt to download
                file_name = "oriontempposter" + f
                res = requests.get(url, stream = True)
                if res.status_code == 200:
                    with open(file_name,'wb') as f:
                        shutil.copyfileobj(res.raw, f)
                    logger.info('Image sucessfully Downloaded: ',file_name)
                else:
                    logger.info('Image Couldn\'t be retrieved')
                    logger.info(errorP)
                    await message.reply(errorPReply)
                    return                               
            except:
                logger.info(errorP)
                await message.reply(errorPReply)

        ######################################################################

        else: #if has attachment
            try:
                if str(message.attachments) == "[]": # Checks if there is an attachment on the message
                    logger.info(errorP)
                    await message.reply(errorPReply)
                    return
                else: # If there is it gets the filename from message.attachments
                    split_v1 = str(message.attachments).split("filename='")[1]
                    filename = str(split_v1).split("' ")[0]
                    isValid = False

                    for format in formats:
                        if filename.endswith(format):
                            isValid = True
                            f = format
                            file_name = "oriontempposter" + f
                            await message.attachments[0].save(fp=file_name) # saves the file
                            logger.info('Image sucessfully Downloaded: ',file_name)
                            break
                    if isValid == False:
                        logger.info(errorP)
                        await message.reply(errorPReply)                      
            except:
                logger.info(errorP)
                await message.reply(errorPReply)
                return
        
        # we now should have a file called file_name = "oriontempposter" + f        
        newPosterImage = Image.open(file_name)
        posterAtlasImage = Image.open("LobbyPosters-Orion-1-Export.png")

        targetWidth = 672
        targetHeight = 887
        posOne = (6,7)
        posTwo = (689, 7)
        posThree = (1370, 7)
        posFour = (6,904)
        posFive = (689, 904)
        posSix = (1370, 904)
        newPosterImage = newPosterImage.resize((targetWidth, targetHeight))

        position = 0

        if reactionEmoji == valid_reactions[0]:
            posterAtlasImage.paste(newPosterImage, posOne)
            position = 1
        elif reactionEmoji == valid_reactions[1]:
            posterAtlasImage.paste(newPosterImage, posTwo)
            position = 2
        elif reactionEmoji == valid_reactions[2]:
            posterAtlasImage.paste(newPosterImage, posThree)
            position = 3
        elif reactionEmoji == valid_reactions[3]:
            posterAtlasImage.paste(newPosterImage, posFour)
            position = 4
        elif reactionEmoji == valid_reactions[4]:
            posterAtlasImage.paste(newPosterImage, posFive)
            position = 5
        elif reactionEmoji == valid_reactions[5]:
            posterAtlasImage.paste(newPosterImage, posSix) 
            position = 6
        else:
            newPosterImage.show() 
        #posterAtlasImage.show()



        posterAtlasImage.save("LobbyPosters-Orion-1-Export.png", format = 'PNG')
        # subprocess.call([r'ClubOrionToGithub.bat'])
        os.system('git commit -m "Update" -a')
        os.system('git push')

        
        if os.path.isfile(file_name):
            os.remove(file_name)
        else:
            # If it fails, inform the user.
            logger.info("Error: %s file not found" % file_name)        

        logger.info(success)
        await message.reply(successReply + str(position))
        return
    

client.run(TOKEN)
