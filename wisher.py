import praw
import prawcore
import sqlite3
import datetime
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
    handlers=[
        logging.FileHandler("{0}/{1}.log".format('logs', 'wisher')),
        logging.StreamHandler()
    ])
logger = logging.getLogger()

WAIT = 40 	# Time (in seconds) pausing between messages

logger.debug("-- Logging in to Reddit")
r = praw.Reddit('wisher')

# Connects with Database
logger.debug("-- Opening SQLite3")
sql = sqlite3.connect("sql.db")
cur = sql.cursor()

def main():
	curDay = datetime.date.today().strftime('%d/%m')
	
	# Gets users with cakeday on given day
	logger.debug("-- Retrieve from DB Users")
	cur.execute("SELECT * FROM cakedays WHERE cakeday = ? AND messaged != ? LIMIT 50", (curDay, 1))
	users = cur.fetchall()

	for user in users:
		if(user[3] == 0):
			logger.debug("-- Checking BL Redditor: " + user[0])
			redBlacklist = checkRedditorBlacklist(user[0])
			if redBlacklist:
				continue
			message(user[0], user[2])

def checkSubredditBlacklist(input):
	cur.execute("SELECT author FROM sub_blacklist WHERE author = ?", [input])
	if cur.fetchone():
		return True
	return False

def checkRedditorBlacklist(input):
	cur.execute("SELECT author FROM red_blacklist WHERE author = ?", [input])
	if cur.fetchone():
		return True
	return False

# Customised Message from members of r/CakeDayBot
# def customMessage():
# 	cur.execute("SELECT message FROM contributions ORDER BY RANDOM() LIMIT 1")
# 	if cur.fetchone():
# 		return cur.fetchone()[0]
# 	else: 
# 		return "Hey just noticed.."

# Message Redditor for their cakeday, update the database
def message(user, createdYear):
	curYear = datetime.date.today().strftime('%Y')
	years = int(curYear) - createdYear
	ordinal = lambda n: "{}{}".format(n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])

	cur.execute("SELECT message FROM contributions ORDER BY RANDOM() LIMIT 1")
	preMessage = cur.fetchone()[0]

	message = "*" + str(preMessage) + "* It's your **" + ordinal(years) + " Cakeday** " + user + "! ^(hug)"

	if years > 0:
		messagestep = 0 # Keep the number of tries
		
		cur.execute("UPDATE cakedays SET messaged = ? WHERE author = ?", (1, user))
		sql.commit()
		
		try:
			redditor = r.redditor(user)
			comments = redditor.comments.new(limit=3)
			for comment in comments:
				
				logger.debug("-- " + "Checking BL Subreddit: " + comment.subreddit.display_name)
				subBlacklist = checkSubredditBlacklist(comment.subreddit.display_name)
				if subBlacklist:
					continue

				messagestep += 1
				try:
					logger.info("-- Commenting ("+ str(messagestep) + "/3): " + user + " | " + str(preMessage) + " | " + comment.permalink)
					# comment.reply(message)
					time.sleep(WAIT)
					break
				# TODO: Fix the below mess
				except praw.exceptions.APIException as e:
					logger.debug("-- [APIException]["+ e.error_type +"]: " + e.message)
					if e.error_type == 'RATELIMIT':
						logger.info("-- [APIException][RATELIMIT]: " + str(r.auth.limits))
						time.sleep(30)
						pass
					if e.error_type in ('DELETED_COMMENT', 'TOO_OLD', 'THREAD_LOCKED'):
						logger.debug("-- [APIException][DELETED_COMMENT][TOO_OLD][THREAD_LOCKED]")
						time.sleep(2)
						continue
				except prawcore.exceptions.Forbidden as e:
					logger.debug("-- [Forbidden]: " + str(e))
					time.sleep(2)
					continue
				except prawcore.exceptions.NotFound as e:
					logger.debug("-- [Reply.NotFound]: " + str(e))
					time.sleep(2)
					continue 
				except AssertionError as e:
					logger.debug("-- [AsertionError]: " + str(e))
					time.sleep(2)
					continue
				except Exception as e:
					logger.debug("-- [Exception]: " + str(e))
					time.sleep(2)
					continue
		except prawcore.exceptions.NotFound as e:
			logger.debug("-- [Comment.NotFound]: " + str(e))
			time.sleep(2)
			pass
		except prawcore.exceptions.Forbidden as e:
			logger.debug("-- [Comment.Forbidden]: " + str(e))
			time.sleep(2)
			pass
	else:
		logger.debug("-- Abort: New User [" + user + "]")

while True:
	main()	