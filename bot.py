import time

import praw
from fuzzywuzzy import fuzz
from tinydb import TinyDB, Query

# Setup

with open("password.txt", "r") as f:
    password = f.read()

reddit = praw.Reddit(client_id="TfdQxE-AgUs_WQ",
                     client_secret="Z9fXGYi8DNWNquBtL9xlgR7mkxpCWw",
                     password=password,
                     user_agent="TopCommentBot by u/LAZDev13",
                     username="LAZDev13")

db = TinyDB('db.json')

subquery = Query()


def findtopcommentforq(question):
    for localsubmi in reddit.subreddit("askreddit").search(question, sort="top"):
        if not db.contains(subquery.id == localsubmi.id):

            prob = fuzz.token_set_ratio(question,localsubmi.title)
            print(f"Probability: {prob}")
            if prob>85:
                print("Title of copy:")
                print(localsubmi.title)

                localsubmi.comment_sort = "top" 
                comm = localsubmi.comments.list()
                try:
                    p = 0
                    if comm[0].stickied:
                        p=1
                    print("Top Comment of Copy:")
                    print(comm[p].body)
                    return comm[p].body
                except IndexError:
                    print("No comment found")
    return "NO GOOD COMMENT FOUND"
        

def main():
    for subm in reddit.subreddit("askreddit").new():
        if not db.contains(subquery.id == subm.id):
            db.insert({"id" :subm.id})
            newsubinask(subm)
           



def newsubinask(sub):
    quest = sub.title

    print("Original Question:")
    print(quest)

    retcomment = findtopcommentforq(quest)
    if retcomment!="NO GOOD COMMENT FOUND":
        time.sleep(10)
        sub.reply(retcomment)
    else:
        print("NO GOOD COMMENT FOUND")

main()

