import datetime
import os
import sys
import time
import praw
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import psycopg2
import configparser

sys.path.insert(0, os.path.realpath(os.path.dirname(__file__)))
os.chdir(os.path.realpath(os.path.dirname(__file__)))

analyzer = SentimentIntensityAnalyzer()


reddit = praw.Reddit(client_id='5hdtNTA2qGBAceBPFhDm6g',
                     client_secret='MiwmqmQzlHOm9KXMP8t_Aa1WBtBg-A',
                     user_agent='testscript by /u/Born-Finger-2677', username='Born-Finger-2677')


class listener():

    def topic(self, text=""):
        return text

    def subred(self, text='AskReddit'):
        subreddit = reddit.subreddit(text)
        return subreddit

    def save_in_db(self):

        #subreddit = self.subred()
        #track = self.topic()
        subreddit = reddit.subreddit('AskReddit')

        for submis in subreddit.stream.submissions():
            try:
                submission = submis.selftext
                submission = submission.lower()
                vs = analyzer.polarity_scores(submission)["compound"]
                time = datetime.datetime.now()
                values = (submission, vs, time)

                config = configparser.ConfigParser()
                config.read('postgres.ini')
                conn = psycopg2.connect(host=config['DEFAULT']['POSTGRES_HOST'], database="reddit",
                                                        user="postgres", password=config['DEFAULT']['POSTGRES_PASSWORD'])
                cur = conn.cursor()
                cur.execute(
                    'INSERT INTO threads (thread,sentiment,time) VALUES (%s,%s,%s)', values)
                conn.commit()

                for comment in subreddit.stream.comments(skip_existing=True):

                    parent_id = str(comment.parent())
                    submission = reddit.comment(parent_id)
                    thread = submission.body
                    thread = thread.lower()
                    vs = analyzer.polarity_scores(submission.body)["compound"]
                    time = datetime.datetime.now()
                    values = (thread, vs, time)

                    cur.execute(
                        'INSERT INTO threads (thread,sentiment,time) VALUES (%s,%s,%s)', values)
                    conn.commit()

                    for reply in submission.replies:
                        reply = reply.lower()
                        vs = analyzer.polarity_scores(reply)["compound"]
                        time = datetime.datetime.now()
                        rep_values = (reply, vs, time)

                        cur.execute(
                            'INSERT INTO threads (thread,sentiment,time) VALUES (%s,%s,%s)', rep_values)
                        conn.commit()

            except praw.exceptions.PRAWException as e:
                #print(e)
                pass

    def del_from_db(self):

        HM_DAYS_KEEP = 30
        current_ms_time = time.time()*1000
        one_day = 86400 * 1000
        del_to = int(current_ms_time - (HM_DAYS_KEEP*one_day))

        config = configparser.ConfigParser()
        config.read('postgres.ini')
        conn = psycopg2.connect(host=config['DEFAULT']['POSTGRES_HOST'], database="reddit",
                                                user="postgres", password=config['DEFAULT']['POSTGRES_PASSWORD'])
        cur = conn.cursor()

        cur.execute("DELETE FROM threads WHERE time < {}".format(del_to))
        conn.commit()
        cur.execute(
            "DELETE FROM threads WHERE thread IS NULL OR trim(thread) = ''")
        conn.commit()
        conn.isolation_level = None
        cur.execute('VACUUM')
        conn.isolation_level = ''

        conn.commit()


config = configparser.ConfigParser()
config.read('postgres.ini')
conn = psycopg2.connect(host=config['DEFAULT']['POSTGRES_HOST'], database="reddit",
                                        user="postgres", password=config['DEFAULT']['POSTGRES_PASSWORD'])
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS threads
             (id SERIAL PRIMARY KEY,thread text, sentiment real, time timestamp)''')
conn.commit()


while True:
    try:
        redditlistern = listener()
        redditlistern.save_in_db()
        redditlistern.del_from_db()
    except Exception as e:
        print(str(e))

conn.close()
