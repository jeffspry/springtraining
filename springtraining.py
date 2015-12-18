import datetime
import praw
import string
import time
import os
import time

__author__ = '/u/spookyyz'
__version__ = '0.2'
user_agent = 'Baseball Spring Training Responder by /u/spookyyz'
bot_sig = "\r\n\r\n---\r\n\r\n^^I'm just a little bot trying to let you know when spring training is. Sorry if I did it poorly, let /u/spookyyz know if it goes haywire."
bot_sig = bot_sig.replace(' ', ' ^^')

###########Vars
SUBREDDIT = 'baseball'
SPRING_KEYWORDS = 'how long many days when does pitchers catchers report and spring training'
WAIT_TIME = 30
SLEEP_TIME = 10
DEVELOPER = False #True to print output instead of post
START_TIME = time.time() # var to monitor time of startup so posts prior to that time can be ignored. (in Unix)
###########

cache = []

class spring_bot(object):
    """
    This little guy is going to try to fuzzy match some phrases in /r/baseball asking when spring training is... lets see if he can do it!
    """
    def __init__(self, SUBREDDIT):
        self.r = praw.Reddit(user_agent=user_agent)
        self.sub = SUBREDDIT
        if (DEVELOPER):
            print "DEVELOPER MODE ON"
        else:
            self.login()

    def login(self):
        if (DEVELOPER):
            print "Skipping login (DEVELOPER MODE ON)"
        else:
            try:
                self.r.login(os.environ['SPRING_REDDIT_USER'], os.environ['SPRING_REDDIT_PASS'])
            except Exception, e:
                print "ERROR(@login): " + str(e)

    def days_until_spring(self):
        spring = datetime.date(2016, 2, 18)
        today = datetime.date.today()
        return abs((spring - today)).days

    def generate_phrase(self):
        if (self.days_until_spring() > 50):
            phrase = "You still got a ways to go buddy...\r\n\r\nOk, ok, it's exactly %s days until spring training starts.\r\n\r\n *Spring training starts on February 18th*" % self.days_until_spring()
        elif (self.days_until_spring() > 30):
            phrase = "We're gettin' pretty close!\r\n\r\nOh, you want exactly? Fine, %s days until spring training starts.\r\n\r\n *Spring training starts on February 18th*" % self.days_until_spring()
        elif (self.days_until_spring() > 15):
            phrase = "I can smell the leather conditioner from here!  We're close!\r\n\r\nCan you smell it?  It's only %s days until spring training starts!\r\n\r\n *Spring training starts on February 18th*" % self.days_until_spring()
        elif (self.days_until_spring() > 0):
            phrase = "I CAN'T HARDLY STAND IT, ITS RIGHT AROUND THE FRIGGIN CORNER!\r\n\r\nAlright, I'll calm down, but it's ONLY %s DAYS UNTIL SPRING TRAINING STARTS! [EXCITEMENT INSTENSIFIES]\r\n\r\n *Spring training starts on February 18th*" % self.days_until_spring()
        elif (self.days_until_spring() == 0):
            phrase = "SPRING TRAINING STARTS TODAY!"
        elif (self.days_until_spring() < 0):
            phrase = "You done missed it buddy, they already reported...\r\n\r\nIt was literally %s days ago when spring training started... way to go." % self.days_until_spring()
        return phrase + bot_sig

    def post(self, comment):
        if (DEVELOPER):
            print "(DEVELOPER) Posting this to comment: " + str(comment.id) + " by " + str(comment.author)
            print self.generate_phrase()
        else:
            try:
                comment.reply(self.generate_phrase())
                time.sleep(WAIT_TIME)
            except Exception, e:
                cache.pop()
                print "ERROR(@post): " + str(e)
                time.sleep(WAIT_TIME)

    def scan_comments(self):
        try:
            sub_obj = self.r.get_subreddit(self.sub)
        except Exception, e:
            print "ERROR(@sublisting): " + str(e)

        try:
            for comment in sub_obj.get_comments(limit=25): #iterate through 25 most recent comments for symbols
                to_post = False
                exclude = set(string.punctuation)
                comment_stripped = ''.join(ch for ch in comment.body if ch not in exclude)
                comment_stripped = comment_stripped.lower()
                if ('when' in comment_stripped and 'spring training' in comment_stripped):
                    to_post = True
                if ('report' in comment_stripped and 'spring training' in comment_stripped):
                    to_post = True
                if ('pitcher' in comment_stripped and 'catcher' in comment_stripped and 'spring training' in comment_stripped):
                    to_post = True
                if ('pitcher' in comment_stripped and 'catcher' in comment_stripped and 'report' in comment_stripped):
                    to_post = True
                if ('start' in comment_stripped and 'spring training' in comment_stripped):
                    to_post = True
                comment_utcunix = datetime.datetime.utcfromtimestamp(comment.created) - datetime.timedelta(hours=8) #offset from comment time as seen by the server to UTC
                start_utcunix = datetime.datetime.utcfromtimestamp(START_TIME)
                if (to_post and comment.id not in cache and not str(comment.author) == 'is_it_spring_yet' and not len(comment_stripped) > 200 and not len(comment_stripped) < 7 and comment_utcunix > start_utcunix):
                    self.post(comment)
                    cache.append(comment.id)
                    print "SUCCESS[@post]: " + comment.id
        except Exception, e:
            print "ERROR(@subloop): " + str(e)


b = spring_bot(SUBREDDIT)
while True:
    b.scan_comments()
    print cache
    time.sleep(SLEEP_TIME)
