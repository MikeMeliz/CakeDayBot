<!--
  Title: Cakeday bot for Reddit (u/CakeDay--Bot)
  Description: Source code of u/CakeDay--Bot that finds, stores, and reply at Redditors that have their anniversary at Reddit. 
  Author: MikeMeliz
  -->

# Cakeday bot for Reddit
- **Profile: [u/CakeDay--Bot](https://www.reddit.com/user/CakeDay--Bot/)**
- **Subreddit: [r/CakeDayBot](https://www.reddit.com/r/CakeDayBot)**

[![Version](https://img.shields.io/badge/version-0.8-green.svg?style=plastic)]() [![license](https://img.shields.io/github/license/MikeMeliz/CakeDayBot.svg?style=plastic)]()

### What's a Cakeday?
Your anniversary day of registering at Reddit.com!

## How is it working:  
It's based on three scripts, one to find, one to message, and the last one to maintain the process.It's based on 
Python 2.7 and SQLite3 to store Redditors.

### Collector.py:
That crazy-bot crawl the specified subreddit (r/all by default), with `readonly` mode, to find and collect redditors at database. 

### Wisher.py:
Chooses the users and *if they're not blacklisted*, replies at his/her last -out of specified range- comments. Checking 
from the database for Blacklisted subreddits or redditors.

### Reporter.py:
The schedule for now is:
- [Every  1 hour] Check for new contributions [here](https://www.reddit.com/r/CakeDayBot/comments/aorljp/submit_your_wish/).
- [Every  2 hours] Check for Opt-out users/subreddits [here](https://www.reddit.com/r/CakeDayBot/comments/an080z/optout_form/).
- [Every 6 hours] Remove comments with negative karma.
- [Saturday: 10:00AM UTC] Posts, at r/CakeDayBot analytics and statuses.
- [Saturday: 11:00AM UTC] Reset users that've been messaged.

## Installation and testing:
*Not available yet,* there'll be a specific branch for testing (with a testing subreddit too). Stay tuned!

## Contributors:
Feel free to contribute on this project! Just fork it, make any change on your fork and add a pull request on current branch! 
Any advice, help or questions will be great for me :)

## License:
“GPL” stands for “General Public License”. Using the GNU GPL will require that all the released improved versions be free 
software. [source & more](https://www.gnu.org/licenses/gpl-faq.html)
