import discord
import os
import urllib
import urllib.request
import datetime
from datetime import date
from bs4 import BeautifulSoup
from discord.ext import commands
from keep_alive import keep_alive
from firebase import firebase

TOKEN = os.environ.get("TOKEN")
client = commands.Bot(command_prefix='$')
hockeyReferencePlayers = "https://www.hockey-reference.com/players/"
hockeyReferenceLeaders = "https://www.hockey-reference.com/leagues/NHL_"
hockeyReferencePlayoffLeaders = "https://www.hockey-reference.com/playoffs/NHL_"
botWebsite = "https://discordbots.org/bot/483804027583332363"
dailyFaceoffLines = "https://www.dailyfaceoff.com/teams/"
sportsnetLogos = "https://images.rogersdigitalmedia.com/www.sportsnet.ca/team_logos/200x200/hockey/nhl/"
hockeyDbDraft = "https://www.eliteprospects.com/draft/nhl-entry-draft/"
scoreURL = "https://www.hockey-reference.com/boxscores/"
scheduleURL = "https://www.cbssports.com/nhl/schedule/"
capFriendlyURL = "https://www.capfriendly.com/players/"
fullTeamName = ["toronto-maple-leafs", "montreal-canadiens", "edmonton-oilers", "vancouver-canucks", "boston-bruins", "chicago-blackhawks", "pittsburgh-penguins", "washington-capitals", "new-york-rangers", "philadelphia-flyers", "detroit-red-wings", "calgary-flames", "buffalo-sabres", "san-jose-sharks", "ottawa-senators", "new-york-islanders", "winnipeg-jets", "new-jersey-devils", "vegas-golden-knights", "anaheim-ducks", "los-angeles-kings", "st-louis-blues", "tampa-bay-lightning", "carolina-hurricanes", "colorado-avalanche", "minesota-wild", "dallas-stars", "columbus-blue-jackets", "arizona-coyotes", "nashville-predators", "florida-panthers"]
shortTeamName = ["TOR", "MTL", "EDM", "VAN", "BOS", "CHI", "PIT", "WSH", "NYR", "PHI", "DET", "CGY", "BUF", "SJS", "OTT", "NYI", "WPG", "NJD", "VEG", "ANA", "LAK", "STL", "TBL", "CAR", "COL", "MIN", "DAL", "CBJ", "ARI", "NSH", "FLA"]
firebaseLink = os.environ.get("FIREBASE")
firebase = firebase.FirebaseApplication(firebaseLink, None)

def scheduleRetrive(date):
	cbsURL = scheduleURL + date
	pageToOpen = urllib.request.urlopen(cbsURL)
	soup = BeautifulSoup(pageToOpen, "html.parser")
	teamCount = 0
	output = ""

	#Loop through all links on page source
	for link in soup.findAll('a'):
		if "/nhl/teams/" in link.get("href") and link.text != "Teams" and link.text != "":
			teamCount+=1
			
			output += link.text
			if teamCount % 2 != 0:
				output += " @ "
				
		elif "/nhl/gametracker/" in link.get("href"):
			output += " " + link.text
			output+="\n"
	if output == "":
		output = "No Games :grinning:"
	return output

@client.event
async def on_ready():
    print("Bot Online.")

@client.command(pass_context=True)
async def draft(ctx, year, roundNumber):
		author = str(ctx.message.author)
		draftLink = hockeyDbDraft + year
		pageToOpen = urllib.request.urlopen(draftLink)
		soup = BeautifulSoup(pageToOpen, "html.parser")
		outputPart1 = ""
		outputPart2 = ""
		seperatorInt = 0;
		tableStart = False
		count = 0
		roundNumber = int(roundNumber)
		roundLength = 0
		if int(year) >= 2017:
			roundLength = 31
		else:
			roundLength = 30

		#Loop through all players in draft round
		for link in soup.findAll('td'):
			if "['overall', 'sorted']" in str(link.get("class")):
				overallNumberStr = str((link.text).strip())
				overallNumberStr = overallNumberStr[1:]
				overallNumberInt = int(overallNumberStr)
				if count < (roundLength * roundNumber) and count >= ((roundLength * roundNumber) - roundLength):
					if seperatorInt < 16:
						outputPart1+= overallNumberStr + " "
					else:
						#Break output to 2 parts, to much info for 1 section of embed
						outputPart2+= overallNumberStr + " "
				tableStart = True
			if "['player']" in str(link.get("class")) and tableStart == True:
				if count < (roundLength * roundNumber) and count >= ((roundLength * roundNumber) - roundLength):
					if seperatorInt < 16:
						outputPart1 += "**" + str((link.text).strip()) + "**" + "\n"
					else:
						outputPart2 += "**" + str((link.text).strip()) + "**" + "\n"
					seperatorInt+=1
				count += 1
			if "['team']" in str(link.get("class")):
				if count < (roundLength * roundNumber) and count >= ((roundLength * roundNumber) - roundLength):
					if seperatorInt < 16:
						outputPart1 += str((link.text).strip()) + " "
					else:
						outputPart2 += str((link.text).strip()) + " "

		#Embed
		draftEmbed = discord.Embed(
			title = "NHL Draft " + str(year) + " Round " + str(roundNumber),
			colour = discord.Colour.teal())
		
		draftEmbed.set_footer(text = "Powered by Eliteprospects.com, no affiliation")
		thumbnailURL = "https://upload.wikimedia.org/wikipedia/en/thumb/3/3a/05_NHL_Shield.svg/1200px-05_NHL_Shield.svg.png"
		draftEmbed.set_thumbnail(url=thumbnailURL)
		draftEmbed.add_field(name="The Picks: ", value=outputPart1, inline=True)
		draftEmbed.add_field(name="-", value=outputPart2, inline=True)
		await client.say(embed=draftEmbed)
		print("draft command used by " + author)
		#await client.say(output)

@client.command(pass_context=True)
async def caphit(ctx, playerFirstName, playerLastName):
	author = str(ctx.message.author)
	playerLink = capFriendlyURL + playerFirstName + "-" + playerLastName
	pageToOpen = urllib.request.urlopen(playerLink)
	soup = BeautifulSoup(pageToOpen, "html.parser")
	output = ""
	startPoint = 0
	endPoint = 0
	caphit = ""
	totalSalary = ""
	baseSalary = ""
	years = ""
	for link in soup.findAll('script'):
		if "data={" in link.text:
			for i in range (0,4):
				startPoint = (link.text).index("[", startPoint+1)
				endPoint = (link.text).index("]", endPoint+1)
				if i == 0:
					caphit+=((link.text)[startPoint+1:endPoint]) + "\n"
				elif i == 1:
					totalSalary+=((link.text)[startPoint+1:endPoint]) + "\n"
				elif i == 2:
					baseSalary+=((link.text)[startPoint+1:endPoint]) + "\n"
				elif i == 3:
					years += ((link.text)[startPoint+1:endPoint]) + "\n"
			#print (caphit + totalSalary + baseSalary + years)
			caphit = "$" + caphit.replace(",", "\n$")
			totalSalary = "$" + totalSalary.replace(",", "\n$")
			baseSalary = "$" + baseSalary.replace(",", "\n$")
			years = years.replace(",", "\n")
		
			#order of arrays from data: caphit, total salary, base salary, years



	#Embed for cap hit
	caphitEmbed = discord.Embed(
		title = "Cap Hit For " + playerFirstName + " " + playerLastName,
		colour = discord.Color.orange())
	caphitEmbed.set_footer(text = "Powered by CapFriendly, no affiliation")
	partOne = (playerLastName[0:5]).lower()
	partTwo = (playerFirstName[0:2]).lower()
	thumbnailURL = "https://d9kjk42l7bfqz.cloudfront.net/req/201810042/images/headshots/" + partOne + partTwo + "01-2017.jpg"
	caphitEmbed.set_thumbnail(url=thumbnailURL)
	caphitEmbed.add_field(name="Years", value=str(years), inline=True)
	caphitEmbed.add_field(name="Cap Hit", value=str(caphit), inline=True)
	caphitEmbed.add_field(name="Total Salary", value=str(totalSalary), inline=True)
	caphitEmbed.add_field(name="Base Salary", value=str(baseSalary), inline=True)
	await client.say(embed=caphitEmbed)

# command that checks statitics of players. *args treats the name of player with spaces
# as multiple parameters to search
@client.command(pass_context=True)
async def stats(ctx, firstName, lastName):
    author = str(ctx.message.author)
    print("Stats command used by " + author)

    partOne = (lastName[0:1]).lower()
    partTwo = (lastName[0:5]).lower()
    partThree = (firstName[0:2]).lower() + "01.html"

    statsLink = hockeyReferencePlayers + partOne + "/" + partTwo + partThree
    await client.say(statsLink)

@client.command(pass_context=True)
async def statsAlternate(ctx, firstName, lastName):
    author = str(ctx.message.author)
    print("Stats Alternate command used by " + author)

    partOne = (lastName[0:1]).lower()
    partTwo = (lastName[0:5]).lower()
    partThree = (firstName[0:2]).lower() + "02.html"

    statsLink = hockeyReferencePlayers + partOne + "/" + partTwo + partThree
    await client.say(statsLink)

@client.command(pass_context=True)
async def leaders(ctx, year):
    author = str(ctx.message.author)
    print("Leaders command used by " + author)
    leadersLink = hockeyReferenceLeaders + year + "_leaders.html"
    await client.say(leadersLink)


@client.command(pass_context=True)
async def playoffLeaders(ctx, year):
    author = str(ctx.message.author)
    print("playoffLeaders command used by " + author)
    playoffLeadersLink = hockeyReferencePlayoffLeaders + year + "_leaders.html"
    await client.say(playoffLeadersLink)


@client.command(pass_context=True)
async def onlineLink(ctx):
    author = str(ctx.message.author)
    print("onlineLink command used by " + author)
    await client.say(
        "I am avaliable online on the discord bots website! I'd appreciate a vote! :) "
        + botWebsite)

# @client.command(pass_context=True)
# async def schedule(ctx):
#     author = str(ctx.message.author)
#     print("Schedule command used by " + author)
#     schedule = "https://www.nhl.com/schedule"
#     await client.say(schedule)


@client.command(pass_context=True)
async def lines(ctx, teamNameWithDashes):
    author = str(ctx.message.author)
    print("Lines command used by " + author)
    teamNameWithDashes = teamNameWithDashes.lower()
    linesLink = dailyFaceoffLines + teamNameWithDashes + "/line-combinations/"
    linesEmbed = discord.Embed(
        title="Line Combos For " + teamNameWithDashes,
        description=linesLink,
        colour=discord.Colour.blue())

    linesEmbed.set_footer(
        text=
        "Thanks to daily Faceoff for the line info link and sportsnet for team logos. I don't own these images or lines, and am not associated with daily faceoff or sportsnet!"
    )
    teamLogo = sportsnetLogos + teamNameWithDashes + ".png"
    linesEmbed.set_thumbnail(url=teamLogo)
    linesEmbed.set_author(name="Hockey Fantasy Fanatic")

    await client.say(embed=linesEmbed)

@client.command()
async def credits():
    await client.say(
        "Icon made by Freepik from www.flaticon.com. This bot is in no way associated with the NHL, any teams, or the websites whose links are provided for info. Bot developed by @Zaid#5456"
    )

@client.command(pass_context=True)
async def schedule(ctx, date):
	#Declaration
	author = str(ctx.message.author)
	output = scheduleRetrive(date)

	#Embed
	scheduleEmbed = discord.Embed(
		title = "NHL Schedule for " + date,
		colour=discord.Colour.green())
	scheduleEmbed.set_footer(text="Powered by CBS Sports, no Affiliation")
	scheduleEmbed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/en/thumb/3/3a/05_NHL_Shield.svg/1200px-05_NHL_Shield.svg.png")
	scheduleEmbed.add_field(name="The Games: ", value=output, inline=True)
	await client.say(embed=scheduleEmbed)

	#Console Output
	print ("schedule command used by " + author)

@client.command(pass_context=True)
async def score(ctx, awayTeam, homeTeam, date):

		# Declaration
		author = str(ctx.message.author)
		uniqueScoreURL = scoreURL + date + "0" + homeTeam + ".html"
		pageToOpen = urllib.request.urlopen(uniqueScoreURL)
		soup = BeautifulSoup(pageToOpen, "html.parser")
		awayScoreInfo = (soup.find('div', {"class":"score"}).text)
		homeScoreInfo = (soup.findAll('div', {"class":"score"})[1].text)
		awayTeamIndex = shortTeamName.index(awayTeam)
		awayTeamLongName = fullTeamName[awayTeamIndex]
		homeTeamIndex = shortTeamName.index(homeTeam)
		homeTeamLongName = fullTeamName[homeTeamIndex]

		# Console Output
		print("Score command used by " + author)
		print (uniqueScoreURL)

		#embeds

		#title Embed
		scoreEmbedTitle = discord.Embed(
				title = soup.title.text,
				colour=discord.Colour.blue())
		
		scoreEmbedTitle.set_footer(text= uniqueScoreURL)
		await client.say(embed=scoreEmbedTitle)

		# Away Score Embed
		awayScoreEmbed = discord.Embed(
		    title = awayScoreInfo,
				colour=discord.Colour.blue())
		
		teamLogo = sportsnetLogos + awayTeamLongName + ".png"
		awayScoreEmbed.set_thumbnail(url=teamLogo)
		await client.say(embed=awayScoreEmbed)	

		#Home Score Embed
		homeScoreEmbed = discord.Embed(
				title = homeScoreInfo,
				colour=discord.Colour.blue())
		
		teamLogo = sportsnetLogos + homeTeamLongName + ".png"
		homeScoreEmbed.set_thumbnail(url=teamLogo)
		await client.say(embed=homeScoreEmbed)

keep_alive()
client.run(TOKEN)