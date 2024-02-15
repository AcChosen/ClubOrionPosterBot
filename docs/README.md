# Club-Orion Poster Bot

A discord bot written in python that dynamically curates and updates community submitted virtual event posters for the virtual club known as Club Orion inside of VRChat. Written in python, the bot looks for images posted inside of a specific discord channel and reacts to those images. The owner of the discord server can click those reactions. to interface with the bot, either to tell the bot what position they want the poster in or to reject the poster outright. The bot then downloads the poster and then uses the Image library from PIL to create a dynamic texture atlas containing all community submitted posters that is then pushed to a github pages repository to be deployed.

![https://i.imgur.com/A96Z212.png](https://i.imgur.com/A96Z212.png)

# [Video](https://streamable.com/0yp151)
