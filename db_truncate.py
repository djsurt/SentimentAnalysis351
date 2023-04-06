'''
Run as a cronjob to keep database size under control
'''
import time
import psycopg2

conn = psycopg2.connect(host="csds351.crl8z4r48ftj.us-east-1.rds.amazonaws.com", database="reddit", user="postgres", password="csds351group6")
c = conn.cursor()

HM_DAYS_KEEP = 30
current_ms_time = time.time()*1000
one_day = 86400 * 1000
del_to = int(current_ms_time - (HM_DAYS_KEEP*one_day))

c.execute("DELETE FROM threads WHERE time < {}".format(del_to))
conn.commit()
c.execute("DELETE FROM threads WHERE thread IS NULL OR trim(thread) = ''")
conn.commit()

conn.isolation_level = None
conn.execute('VACUUM')
conn.isolation_level = ''

conn.commit()
conn.close()
