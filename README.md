# TwitchScraper
This is a simple implementation of web scraper for Twitch.tv's main directory page (https://www.twitch.tv/directory). The intention behind it is to take a point sample of currently popular content on Twitch with the goal of aiding research projects. I mainly needed it for a project that invloved randomly sampling Twitch content, which required a way of mapping current Twitch content. 

Twitch does provide an official API to this information but that system appears to only provide titles and images, without viewer or tag information that was relevant to our project.

# Instalation
The script uses both Selenium and Beautiful Soup. You can install the main requirements using pip::

    pip install -r requirements.txt

However, you will need to install the appropriate Chrome Webdriver (https://selenium-python.readthedocs.io/installation.html#drivers) to get it working. It would also be trivial to switch to a different Webdrivier if you don't want to use Chrome.
