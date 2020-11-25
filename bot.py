#!/usr/bin/python3
import time

import praw
import yaml
from fuzzywuzzy import fuzz
from tinydb import TinyDB, Query


# Setup
with open("conf.yaml",mode="r") as f:
    conf = yaml.load(f, Loader=yaml.FullLoader)

reddit = praw.Reddit(client_id=conf.get("client_id"),
                     client_secret=conf.get("client_secret"),
                     password=conf.get("password"),
                     user_agent=conf.get("user_agent"),
                     username=conf.get("username"))

db = TinyDB('db.json')

subquery = Query()


def findtopcommentforq(question):
    for localsubmi in reddit.subreddit(conf.get("subreddit")).search(question, sort="top"):
        if not db.contains(subquery.id == localsubmi.id):
            if localsubmi.score < conf.get("min-karma-post"):
                print("Post Karma to low.")
                continue

            prob = fuzz.token_set_ratio(question,localsubmi.title)
            print(f"Probability: {prob}")
            if prob>conf.get("confidence"):
                print("Title of copy:")
                print(localsubmi.title)

                localsubmi.comment_sort = "top" 
                comm = localsubmi.comments.list()
                for comment in comm:
                    try:
                        if comment.distinguished !=None:
                            print("Mod comment")
                            continue
                        if comment.stickied:
                            print("Sticked comment")
                            continue
                        if comment.score < conf.get("min-karma-comment"):
                            print("Comment Karma to low.")
                        cbody = comment.body
                        
                    except:
                        continue
                    
                    
                    if "edit" in cbody.lower():
                        continue
                    if "gold" in cbody.lower():
                        
                        continue
                    print(cbody + "\n ----------\n")
                    return cbody

                    
    return "NO GOOD COMMENT FOUND"
        

def main():
   
    subreddit = reddit.subreddit("AskReddit")
    for subm in subreddit.stream.submissions():
        if not db.contains(subquery.id == subm.id):
            db.insert({"id" :subm.id})
            newsubinask(subm)
           



def newsubinask(sub):
    quest = sub.title

    print("Original Question:")
    print(quest)

    retcomment = findtopcommentforq(quest)
    if retcomment!="NO GOOD COMMENT FOUND":
        time.sleep(conf.get("delay"))

        
        sub.reply(retcomment)
    else:
        print("NO GOOD COMMENT FOUND")

main()

