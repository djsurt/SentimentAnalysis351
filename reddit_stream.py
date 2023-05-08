import datetime
import os
import sys
import time
import praw
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import psycopg2
import configparser
import threading
from transformers import pipeline
NEGATIVE_THRESHOLD=-0.6
sys.path.insert(0, os.path.realpath(os.path.dirname(__file__)))
os.chdir(os.path.realpath(os.path.dirname(__file__)))

analyzer = SentimentIntensityAnalyzer()
sentiment_analysis = pipeline("sentiment-analysis",model="siebert/sentiment-roberta-large-english")

reddit = praw.Reddit(client_id='5hdtNTA2qGBAceBPFhDm6g',
                     client_secret='MiwmqmQzlHOm9KXMP8t_Aa1WBtBg-A',
                     user_agent='testscript by /u/Born-Finger-2677', username='Born-Finger-2677')

def get_sentiment(text):
    if len(text.split()) > 512:
        text = " ".join(text.split(' ')[:512])
    sentiment = sentiment_analysis(text)
    sign = -1 if sentiment[0]['label'] == 'NEGATIVE' else 1
    return sentiment[0]['score'] * sign
class listener():

    def topic(self, text=""):
        return text

    def subred(self, text):
        subreddit = reddit.subreddit(text)
        return subreddit

    #Need to modify this method so that it flags malicious posts and puts them into a separate database.
    def save_in_db(self, text):
        subreddit = self.subred(text=text)
        # subreddit = reddit.subreddit('AskReddit')

        for submis in subreddit.stream.submissions():
            try:
                submission = submis.selftext
                if submission == None or len(submission) == 0:
                    continue
                submission = submission.lower()
                vs = (analyzer.polarity_scores(submission)["compound"] + get_sentiment(submission)) / 2
                time = datetime.datetime.now()
                values = (text, submission, vs, time)

                print(values)

                config = configparser.ConfigParser()
                config.read('postgres.ini')
                conn = psycopg2.connect(host=config['DEFAULT']['POSTGRES_HOST'], database="reddit",
                                                        user="postgres", password=config['DEFAULT']['POSTGRES_PASSWORD'])
                cur = conn.cursor()
                #sentiment = sentiment_analysis(submission)
                #print(sentiment)
                #print(sentiment[0]['label'])
                if vs < NEGATIVE_THRESHOLD:
                    cur.execute(
                        'INSERT INTO malicious_posts (subreddit, thread,sentiment,time) VALUES (%s, %s,%s,%s)', values)
                    conn.commit()
                else:
                    cur.execute(
                        'INSERT INTO threads (subreddit, thread,sentiment,time) VALUES (%s, %s,%s,%s)', values)
                    conn.commit()

                for comment in subreddit.stream.comments(skip_existing=True):

                    parent_id = str(comment.parent())
                    submission = reddit.comment(parent_id)
                    if submission == None or len(submission.body) == 0:
                        continue
                    thread = submission.body
                    thread = thread.lower()
                    vs = (analyzer.polarity_scores(submission.body)["compound"] + get_sentiment(submission.body)) / 2
                    time = datetime.datetime.now()
                    values = (text, thread, vs, time)
                    if vs < NEGATIVE_THRESHOLD:
                        cur.execute(
                            'INSERT INTO malicious_posts (subreddit, thread,sentiment,time) VALUES (%s, %s,%s,%s)', values)
                        conn.commit()
                    else:
                        cur.execute(
                            'INSERT INTO threads (subreddit, thread,sentiment,time) VALUES (%s, %s,%s,%s)', values)
                        conn.commit()

                    for reply in submission.replies:
                        reply = reply.lower()
                        if reply  == None or len(reply) == 0:
                            continue
                        vs = (analyzer.polarity_scores(reply)["compound"] + get_sentiment(reply)) / 2
                        time = datetime.datetime.now()
                        rep_values = (text, reply, vs, time)
                        if vs < NEGATIVE_THRESHOLD:
                            cur.execute(
                                'INSERT INTO malicious_posts (subreddit, thread,sentiment,time) VALUES (%s, %s,%s,%s)', rep_values)
                            conn.commit()
                        else:
                            cur.execute(
                                'INSERT INTO threads (subreddit, thread,sentiment,time) VALUES (%s, %s,%s,%s)', rep_values)
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
             (id SERIAL PRIMARY KEY,subreddit text, thread text, sentiment real, time timestamp)''')
conn.commit()

cur.execute('''CREATE TABLE IF NOT EXISTS twitter_threads
             (id SERIAL PRIMARY KEY, thread text, sentiment real)''')
conn.commit()

cur.execute('''CREATE TABLE IF NOT EXISTS malicious_twitter_threads
             (id SERIAL PRIMARY KEY, thread text, sentiment real)''')
conn.commit()

cur.execute('''CREATE TABLE IF NOT EXISTS malicious_posts
             (id SERIAL PRIMARY KEY, subreddit TEXT, thread TEXT, sentiment REAL, time TIMESTAMP)''')
conn.commit()



while True:
    try:
        redditlistern = listener()
        # Create threads for each subreddit
        t_askreddit = threading.Thread(target=redditlistern.save_in_db, args=('AskReddit',))
        t_worldnews = threading.Thread(target=redditlistern.save_in_db, args=('worldnews',))
        t_movies = threading.Thread(target=redditlistern.save_in_db, args=('movies',))
        # Start the threads
        t_askreddit.start()
        t_worldnews.start()
        t_movies.start()

        # Wait for all threads to finish (optional, but recommended)
        t_askreddit.join()
        t_worldnews.join()
        t_movies.join()
        redditlistern.del_from_db()
    except Exception as e:
        print(str(e))

conn.close()
