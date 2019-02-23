import praw
import sqlite3
import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
    handlers=[
        logging.FileHandler("{0}/{1}.log".format('logs', 'collector')),
        logging.StreamHandler()
    ])
logger = logging.getLogger()

SUBREDDIT = "all"	# Subreddit to fetch redditors
MAXCOMMS = 100		# Comments fetched when looking to get author information

# Logs into reddit as read-only 
logger.debug("-- Logging in to Reddit")
r = praw.Reddit('collector')

# Initialize database
logger.debug("-- Opening SQLite3")
sql = sqlite3.connect("sql.db")
cur = sql.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS cakedays(author TEXT, cakeday TEXT, year INTEGER, messaged INTEGER)")
sql.commit()

# Fetchs newest comments in $SUBREDDIT and pulls author from each comment
def fetchRedditors():
	logger.debug("-- Start fetching Redditors from " + str(MAXCOMMS) + " comments of r/" + str(SUBREDDIT))
	subreddit = r.subreddit(SUBREDDIT)
	comments = subreddit.comments(limit=MAXCOMMS)
	for comment in comments:
		try:
			rName = comment.author.name
			
			# Check Redditor in DB
			cur.execute("SELECT author FROM cakedays WHERE author=?", [rName])
			if not cur.fetchone():
				getCakeDay(rName)

		except AttributeError:
			pass

# Retrieve CakeDay of Subredditor 
def getCakeDay(author):	
	try:
		authdate = r.redditor(author).created_utc
		logger.debug("CakeDay of: " + author + " : " + str(authdate))
		storeRedditors(author, authdate)
	except Exception as e:
		print str(e)
		authdate = '978307199' # TODO: From 31/12/2000 to catch unreachable dates & users, to pass
		pass

# Store them to Database
def storeRedditors(author, date):
	year = datetime.datetime.utcfromtimestamp(int(float(date))).strftime('%Y')
	cakeday = datetime.datetime.utcfromtimestamp(int(float(date))).strftime('%d/%m')

	logger.info(" | " + cakeday + "/" + year + " | u/" + author)
	try:
		cur.execute("INSERT INTO cakedays(author, cakeday, year, messaged) VALUES(?, ?, ?, ?)", (author, cakeday, year, 0))
		sql.commit()
	except sqlite3.Error, e:
		print "Error %s:" % e.args[0]

while True:
	fetchRedditors()