from instagrapi import Client
import psycopg2
import os

cl = Client()
cl.login(os.environ['USERNAME'], os.environ['PASSWORD'])

user_id = cl.user_id_from_username(os.environ['USERNAME'])

followers = cl.user_followers(cl.user_id)
following = cl.user_following(cl.user_id)
followers_list = []
following_list = []
notfollowing = []

conn = psycopg2.connect(host = "localhost", dbname = "postgres", user = "postgres", password = os.environ['POSTGRES_PASSWORD'], port = 5432)
curr = conn.cursor()
def check_table_exists(conn, table_name):
    curr = conn.cursor()
    curr.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = %s
        );
    """, (table_name,))
    exists = curr.fetchone()[0]
    curr.close()
    return exists


if check_table_exists(conn, 'followers'):
    print("The followers table already exists.")
else:
    print("The followers table does not exist. Creating it now...")
    curr = conn.cursor()
    curr.execute('''
    CREATE TABLE followers (
        user_id VARCHAR PRIMARY KEY,
        username VARCHAR,
        full_name VARCHAR,
        profile_pic_url TEXT
    );
    ''')
    conn.commit()
    curr.close()
    print("Followers table created successfully.")


if not check_table_exists(conn, 'followers'):
    for user_id, user_info in followers.items():
        insert_query = '''
        INSERT INTO followers (user_id, username, full_name)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id) DO NOTHING;
        '''
        curr.execute(insert_query, (
            user_info.pk,
            user_info.username,
            user_info.full_name,
        ))

for user_id, user_info in followers.items():
    followers_list.append(user_info.username)
for user_id, user_info in following.items():
    following_list.append(user_info.username)

for i in range(len(following_list)):
    if following_list[i] not in followers_list:
        notfollowing.append(following_list[i])
prev_follower = []
unfollowed = []

#gets the people who unfollowed you since database creation
query = 'SELECT * FROM followers'
curr.execute(query)  
results = curr.fetchall()
for i in range(len(results)):
    prev_follower.append(results[i][1])
for i in range(len(prev_follower)):
    if prev_follower[i] not in followers_list:
        unfollowed.append(prev_follower[i])


print(f'NOT FOLLOWING YOU: {notfollowing}')
print(f'UNFOLLOWED YOU: {unfollowed}')

conn.commit()
curr.close()
conn.close()