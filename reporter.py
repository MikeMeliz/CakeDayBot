import praw
import sqlite3
import datetime
import time
import schedule
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
    handlers=[
        logging.FileHandler("{0}/{1}.log".format('logs', 'reporter')),
        logging.StreamHandler()
    ])
logger = logging.getLogger()

points = 3		# Remove comments with < Points
maxChars = 22 	# Maximum chars for Message Submissions

logger.debug("-- Logging in to Reddit")
r = praw.Reddit('reporter')

# Initialize database
logger.debug("-- Opening SQLite3")
sql = sqlite3.connect("sql.db")
cur = sql.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS sub_blacklist(author TEXT)")
sql.commit()
cur.execute("CREATE TABLE IF NOT EXISTS red_blacklist(author TEXT)")
sql.commit()
cur.execute("CREATE TABLE IF NOT EXISTS contributions(message TEXT)")
sql.commit()

# Reset Messaged Redditor, except current date.
def resetMessageStatuses():
	logger.info("-- Start reseting Users from Database")
	totalReset = 0
	curDay = datetime.date.today().strftime('%d/%m')
	cur.execute("SELECT author FROM cakedays WHERE cakeday != ? AND messaged = ?", (curDay, 1))
	users = cur.fetchall()

	for user in users:
		try:
			cur.execute("UPDATE cakedays SET messaged = ? WHERE author = ?", (0, user[0]))
			sql.commit()
			totalReset += 1
		except sqlite3.Error, e:
			print "Error %s:" % e.args[0]
			pass

	logger.info("-- Total reseted users: " + str(totalReset))

# Remove comments with $Point number and below -to reduce spam 
def removeDownComments():
	logger.info("-- Start deleting comments with points below: " + str(0 - points))
	totalDeleted = 0
	comments = r.user.me().comments.controversial(limit=700)
	for comment in comments:
	    if comment.score < (0 - points):
	        logging.info(" | " + str(comment.score) + " / " + str(0 - points) + " | ")
	        comment.delete()
	        totalDeleted += 1

	logger.info("-- Total deleted comments: " + str(totalDeleted))

# Check comments from Opt-out submission and store them to Database
# TODO: Don't include deleted comments
def storeOptOut():
	logger.info("-- Checking for new Blacklist")
	oocomments = r.submission(id='an080z').comments
	totalOO = 0
	for comment in oocomments:
		combody = comment.body
		# Check if approved
		if comment.approved_by == None:
			break
		# Subreddits
		if combody.startswith("r/"):
			oosubred = combody.replace("r/", "")
			cur.execute("SELECT author FROM sub_blacklist WHERE author = ?", [oosubred])
			if not cur.fetchone():
				logger.debug("-- Added r/"+ oosubred +" to Blacklist.")
				cur.execute("INSERT INTO sub_blacklist(author) VALUES(?)", [oosubred])
				sql.commit()
				totalOO += 1
			continue
		# Redditors
		elif combody.startswith("u/"):
			ooredit = combody.replace("u/", "")
			cur.execute("SELECT author FROM red_blacklist WHERE author = ?", [ooredit])
			if not cur.fetchone():
				logger.debug("-- Added u/"+ ooredit +" to Blacklist.")
				cur.execute("INSERT INTO red_blacklist(author) VALUES(?)", [ooredit])
				sql.commit()
				totalOO += 1
			continue
		# Invalid
		else:
			logger.debug("-- Invalid comment to Opt-out form!")
			continue
	logger.info("-- Total new blacklisted: " + str(totalOO))

# Check new contributions for the start of the message "Hey just noticed.."
def storeContributions():
	logger.info("-- Checking for new Contributions with limit: " + str(maxChars) + " characters.")
	contrSubm = r.submission(id='aorljp').comments.replace_more(limit=0)
	totalCC = 0
	for comment in contrSubm:
		print comment.body # remove
		# Check if approved
		if comment.approved_by == None:
			break
		combody = comment.body
		if len(combody) <= maxChars:
			cur.execute("SELECT message FROM contributions WHERE message = ?", [combody])
			if not cur.fetchone():
				cur.execute("INSERT INTO contributions(message) VALUES(?)", [combody])
				sql.commit()
				logger.debug("-- Added contribution's message: " + combody)
				totalCC += 1
			continue
		# Invalid
		else:
			logger.debug("-- Invalid comment to *Hey just noticed..* form!")
			continue
	logger.info("-- Total new messages: " + str(totalCC))

# Weekly Digist of Analytics and obtained statistics
def weekStatistics():
	logger.info("-- Start posting Week Digest")
	# Count Total Users in Database
	cur.execute("SELECT count(*) FROM cakedays")
	totalUsersDb = cur.fetchone()[0]

	# Count Total Comments of this week
	cur.execute("SELECT COUNT(*) FROM cakedays WHERE messaged = 1")
	totalMessages = cur.fetchone()[0]

	# Find oldest redditor
	cur.execute("SELECT author, year FROM cakedays WHERE year != 2000 ORDER BY year ASC LIMIT 1")
	oldResult = cur.fetchone()
	oldestRedditor = str(''.join(oldResult[0]))
	oldestYear = str(oldResult[1])

	# Redditors by years
	cur.execute("SELECT year, COUNT(author) FROM cakedays WHERE year != 2000 GROUP BY year")
	byYears = cur.fetchall()
	yearList = ""
	for byYear in byYears:
		yearList += "- **" + str(byYear[0]) + "**: " + str(byYear[1]) + " \n"

	# # TODO: Redditors Stored Table
	# cur.execute("SELECT year FROM cakedays WHERE year != 2000 GROUP BY year")
	# byYears = cur.fetchall()
	# yearList = ""
	# for byYear in byYears:
	# 	yearList += str(byYear[0]) + "|"

	cur.execute("SELECT year FROM cakedays WHERE year != 2000 GROUP BY year")
	byMonths = cur.fetchall()
	monthList = ""
	for byMonth in byMonths:
		monthList += str(byMonth[0]) + "|"

	curDay = datetime.date.today().strftime('%d/%m')
	title = curDay + ': Week Digest of Reddit Cakedays'

	selftext = (""
	"### Analytics:	 \n"
	"---  \n"
	"Cakedays Stored: {0}  \n"
	"Wishes this week^(beta): {1}  \n"
	"Oldest redditor found: u/{2}, Year: {3}  \n"
	"  \n"
	"**Redditors by year:**  \n"
    "{4}  \n"
    "  \n"
    # TODO: Table with Years / Months and numbers of stored redditors
	# "**Redditors Stored Table:**  \n"
	# "Months| {}  \n"
	# "{}  \n"
	# "  \n"
	"^(Really, any comment/suggestion/idea is highly appreciated!)  "
	"").format(totalUsersDb, totalMessages, oldestRedditor, oldestYear, yearList)

	r.subreddit('cakedaybot').submit(title,selftext)
	logger.info("-- Posted.")

schedule.every(1).hours.do(storeOptOut)
schedule.every(2).hours.do(storeContributions)
schedule.every(6).hours.do(removeDownComments)
schedule.every().saturday.at("10:00").do(weekStatistics)
schedule.every().saturday.at("11:00").do(resetMessageStatuses)

while True:
    schedule.run_pending()
    time.sleep(1)