import tweepy
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json

# Keys ommitted 
consumer_key="***"
consumer_secret="***"
access_token="***"
access_secret="***"

# Handles authorization with Twitter
auth = OAuthHandler(consumer_key,consumer_secret)
auth.set_access_token(access_token,access_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
#api = tweepy.API(auth)

accounts=[]
tweets_per_account = []


def retrieveTweets():
    count=1
    for user in accounts:
        print("Processing Account #"+str(count)+": "+user)
        tweets = []
        statuses = api.user_timeline(screen_name=user,count=200, tweet_mode="extended")
        for status in statuses:
            #tweet_dict = {"USER":user,"ID":status.id,"TEXT":status.full_text}
            tweet_dict = {"ID":status.id,"TEXT":status.full_text}
            tweets.append(tweet_dict)

        writeTweetsToFile(user,tweets)
        #writeTweetsToJSON(user, tweets)
        #account_dict = {"USER":user, "TWEETS":tweets}
        account_dict = {user: {tweets}}
        tweets_per_account.append(account_dict)
        print("Done"+'\n')
        count+=1


def writeTweetsToFile(account,tweets):
    path = r"C:\Users\Brenden\Desktop\ODU\Fall 2020\CS432\HW_8\hw8-cluster-blewis1014\account_tweets\tweets_{}.txt".format(account)
    fileToWrite = open(path,"a", encoding="utf-8")
    for tweet in tweets:
        fileToWrite.write(str(tweet["ID"])+"\n")
        fileToWrite.write(tweet["TEXT"]+"\n\n")
    fileToWrite.close()

def writeTweetsToJSON():
    with open("H9_tweets.json","w") as f:
        json.dump(tweets_per_account, f, indent=2)

def readAccounts():
    with open("100Accounts.txt",'r') as f:
        for line in f:
            line = line.rstrip('\n')
            accounts.append(line)

def collectAccounts():
    user_ID = ""
    #user_IDs = ["","","",
    #           "","","",
    #           "","","",
    #           "", "", "",
    #           "", "", ""]

    user = api.get_user(user_ID)
    #users = api.lookup_users(screen_names=user_IDs)

    #for user in users:
    #    tweet_count = user.statuses_count
    #    print(user.screen_name+"\n"+"Tweets: "+str(tweet_count))
    #    print("Followers: "+str(user.followers_count)+"\n")

    tweet_count = user.statuses_count
    print(user.screen_name+"\n"+"Tweets: "+str(tweet_count))
    print("Followers: "+str(user.followers_count)+"\n")

if __name__ == '__main__':
    #collectAccounts()
    readAccounts()
    retrieveTweets()
    writeTweetsToJSON()