import json
import re
import nltk
from nltk.corpus import stopwords
from collections import Counter
from operator import itemgetter
from progress.bar import IncrementalBar
import itertools  

accounts = []   # [User1, User2, ...]
tweets_per_account = [] # [User1Tweets, User2Tweets, ....]
                        # {USER: TEXT:},
                        # {USER: TEXT:}

words_per_account = []  # [User1[], User2, ....]
                        # {word1,
                        #  word2,
                        #  ...}, 

all_words = []      # {"WORD":word, "COUNT":count_of_accounts_feat}
final_words = []    
# Need to save to file
common_words_per_account = []   # [User1[], User2[], ....]
                                # [(word1,count),
                                #  (word2,count),
                                #  ...], 

accounts_with_common = [] # {USER: user, "WORD":word, "OCCUR":count_of_accounts_feat}}

common_all_words = {}  # Top 1000, used for Matrix
apcount={}
final_common = {}
matrix_words = []
matrix = []

def process():
    global apcount, common_all_words, final_common
    data = readJSONFile()
    matchTweets(data)
    print("Getting words per account...")
    for user in tweets_per_account:
        clean_words=[]
        for tweet in user:
            clean_words.append(cleanText(tweet["TEXT"]))
        words_per_account.append(clean_words)

    print("Getting apcount...")
    apcount = getApCount(words_per_account)
    print("Getting all words...")
    populateAllWords()
    
    print("Removing stopwords per account...")

    fakeStopwordsTFIDF(apcount)
    countFinalWords()
    
    sorted_common = dict(sorted(common_all_words.items(), key=itemgetter(1),reverse=True))

    final_common = dict(itertools.islice(sorted_common.items(),1000))

    createMatrix()

def createMatrix():
    fwords = list(final_common.keys())
    temp = []
    for user in words_per_account:
        row = {x:0 for x in fwords}
        #row = {account: {x:0 for x in fwords} for account in accounts}
        for key,value in row.items():
            for words in user:
                for word in words:
                    if word == key:
                        row[word]+=1
        matrix.append(row)
    
    #for user in temp:
        #row = {account: {word:key for word,key in user.items()} for account in accounts}
        #matrix.append(row)

def countFinalWords():
    global common_all_words
    #top_words = {}
    bar = IncrementalBar('Counting', max=len(final_words))
    for word in final_words:
        for user in words_per_account:
            for w in user:
                for x in w:
                    if word == x:
                        common_all_words[word]=common_all_words.get(word,0)+1
        bar.next()
    bar.finish()
    
def populateAllWords():
    for user in words_per_account:
        for words in user:
            for word in words:
                all_words.append(word)

def getApCount(words_list):
    global common_words_per_account
    ap = {}
    for user in words_list:
        common_words = []
        words_no_dupes = []
        for words in user:
            [words_no_dupes.append(x) for x in words if x not in words_no_dupes]

            temp = sorted(getMostCommonTerms(words),key=itemgetter(1),reverse=True)

            common_words.append(temp)                  
                
        for word in words_no_dupes:
            ap[word]=ap.get(word,0)+1

        #sorted_common = common_words.sort(key=itemgetter(0))
        common_words_per_account.append(common_words)

    return dict(sorted(ap.items(), key=itemgetter(1),reverse=True))

def getMostCommonTerms(list):
    common_words = Counter(list)

    most_common = common_words.most_common(1000)
    
    return most_common

def matchTweets(data):
    global tweets_per_account
    for account in accounts:
        tweets_from_account = []
        for item in data:
            if account == item["USER"]:
                for tweet in item["TWEETS"]:
                    tweet_dict = {'USER':account,'TEXT':tweet["TEXT"]}
                    tweets_from_account.append(tweet_dict)
        tweets_per_account.append(tweets_from_account)

def matchCommonTerms():
    for index, user in enumerate(accounts):
        for words in common_words_per_account[index]:
            for word in words:
                word_dict = {"USER":user,"WORD":word[0],"FREQ":word[1]}
                accounts_with_common.append(word_dict)

def readJSONFile():
    with open("h9_tweets.json",'r') as f:
        data = json.load(f)
    return data

def readAccounts():
    with open("100Accounts.txt",'r') as f:
        for line in f:
            line = line.rstrip('\n')
            accounts.append(line)

def cleanText(text):
    clean_text = text.lower()

    clean_no_mention = re.sub(r"@[\w]+","",clean_text) # remove @mentions

    # remove links, punctuation, emojis, and hashtags
    clean_no_chars = " ".join(re.sub(r"([^0-9A-Za-z \t])|(\w+:\/\/\S+)", "", clean_no_mention).split()) 
    
    text_word_list = clean_no_chars.split()

    clean_words_list = []

    for word in text_word_list:
        if len(word) >= 3 and len(word) <= 15:
            clean_words_list.append(word)
    
    return clean_words_list

def fakeStopwordsTFIDF(apcount):
    global final_words
    #num_accounts = 100

    bar = IncrementalBar('Processing', max=len(apcount))
    for word,ac in apcount.items():
        frac = float(ac) / 100
        if frac>0.1 and frac<0.5:
            final_words.append(word)
        bar.next()
    bar.finish()

def writeFinalWordsToFile():
    with open("FinalWords.json","w") as f:
        json.dump(final_common,f,indent=2)
        #for word in final_common:
            #f.write(word+"\n")

def readInFinalWords():
    with open("FinalWords.json",'r') as f:
        data = json.load(f)
    
    for key,value in data.items():
        temp_dict = {"WORD":key,"COUNT":value}
        matrix_words.append(temp_dict)

def writeCommonTermsPerAccount():
    with open("Common_Terms_Per_File.txt","w") as f:
        for item in accounts_with_common:
            f.write("User: "+item["USER"]+"\n")
            f.write("Word: "+item["WORD"]+"\n")
            f.write("Occurences across account: "+str(item["FREQ"])+"\n\n")

def writeMatrixData():
    with open("MatrixData.json","w") as f:
        json.dump(matrix,f,indent=2)
        #for row in matrix:
            #json.dump(row,f)
            #f.write("\n")

def testOutput():
    #for tweet in tweets_per_account[0]:
        #print(tweet)
        #print("\n")

    #for words in words_per_account[1]:
        #print(words)
        #print("\n")
    #print(all_words)
    
    for tweet in common_words_per_account[0]:
        for word in tweet:
            print(word)
        print("\n"+("-"*25))        

if __name__ == '__main__':
    readAccounts()
    #readInFinalWords()
    #processFinalWords()
    process()
    writeMatrixData()
    #writeCommonTermsPerAccount()
    #writeFinalWordsToFile()