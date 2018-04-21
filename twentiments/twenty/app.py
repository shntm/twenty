# import shit later
import requests
import time
from nltk.corpus import stopwords
from nltk.corpus import twitter_samples
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk.classify import NaiveBayesClassifier
import nltk.classify.util
from requests_oauthlib import OAuth1
import tweepy
import json
import re

globalClassifier = "empty"

def callTwitterApi(inputData):
	auth = tweepy.OAuthHandler("", "")
	auth.set_access_token("", "")

	api = tweepy.API(auth)

	searchResults = api.search(inputData, rpp=100, count=100, lang='en')
	# print(rate_limit_left)
	return searchResults
	# for result in searchResults:
	#     print(result.text)
	#timestamp = str(int(time.time()))
	#headers = {
	#	"authorization" : "OAuth",
	#	"oauth_consumer_key" : "cECZHayAqLiN4tMdzSXzlXqgy",
	#	"oauth_nonce" : "9SfBX5mNDDyHSWbPbKx5mnw6SiYgQQXqoqUi3NuEdGZLZk3VsQ",
	#	"oauth_signature_method" : "HMAC-SHA1",
	#	"oauth_timestamp" : timestamp,
	#	"oauth_token" :"178231005-X2HJUt9WrFCRlGlHM53YQG5q9Nx7c2lQbu5QSImg",
	#	"oauth_version" :"1.0",
	#}
	#auth = OAuth1('cECZHayAqLiN4tMdzSXzlXqgy', '9SfBX5mNDDyHSWbPbKx5mnw6SiYgQQXqoqUi3NuEdGZLZk3VsQ', ' 178231005-X2HJUt9WrFCRlGlHM53YQG5q9Nx7c2lQbu5QSImg', ' 9N8lxSqYmqcSHVeN2rvtq3e7hPgei27qriVNfraKmoSpx')
	#result = requests.get('https://stream.twitter.com/1.1/statuses/sample.json', auth=auth, headers=headers)
	#return result

def giveLengthOfTest(x):
	return int(x*0.05)

def loadTwitterDataset():
	positiveTweets = twitter_samples.strings('positive_tweets.json')
	negativeTweets = twitter_samples.strings('negative_tweets.json')
	testSizePos, testSizeNeg = giveLengthOfTest(len(positiveTweets)), giveLengthOfTest(len(positiveTweets))
	sampleSizePos, sampleSizeNeg = len(positiveTweets) - testSizePos, len(positiveTweets) - testSizeNeg
	samplePos = positiveTweets[:sampleSizePos]
	sampleNeg = negativeTweets[:sampleSizeNeg]
	testPos = positiveTweets[sampleSizePos+1:]
	testNeg = negativeTweets[sampleSizeNeg+1:]
	dataset = {
		"samplePos" : cleanUpData(samplePos),
		"sampleNeg" : cleanUpData(sampleNeg),
		"testPos" : cleanUpData(testPos),
		"testNeg" : cleanUpData(testNeg),
		"actualSamplePos" : samplePos,
		"actualSampleNeg" : sampleNeg,
		"actualTestPos" : testPos,
		"actualTestNeg" : testNeg,
	}
	return dataset

def removeStopWords(words):
 	return [word for word in words if word not in stopwords.words('english')]

def removeSymbols(words):
	invalidSymbols = [":", "-", ")", "(", "@", "#", ";", "http", "https", ",", "a", "the", "an", "i", "he", "she", "it", "is", "was", "you", "they", "we", "I", "us", "our", "has", "had"]
	return [word for word in words if word not in invalidSymbols]

def removeUrls(words):
	reg = re.compile('\A\//[a-z0-9.\/]+')
	for word in words:
		matchObj = reg.match(word)
		if matchObj:
			words.remove(word)
	return words

def removeNonWords(words):
	returnList = []
	for word in words:
		if wordnet.synsets(word):
			returnList.append(word)
	return returnList

def changeToWill(words):
	i=0
	for word in words:
		if word == "'ll":
			words[i] = "will"
		i+=1
	return words

def removeContractions(sentence):
	words = sentence.split(' ')
	substituteDict = {
	"aren\'t" : "are not",
	"can\'t" : "can not",
	"couldn\'t" : "could not",
	"didn\'t" : "did not",
	"doesn\'t" : "does not",
	"don\'t" : "do not",
	"hadn\'t" : "had not",
	"hasn\'t" : "has not",
	"haven\'t" : "have not",
	"he\'d" : "he had",
	"he\'ll" : "he will",
	"he\'s" : "he is",
	"i\'d" : "I had",
	"i\'ll" : "I will",
	"i\'m" : "I am",
	"i\'ve" : "I have",
	"isn\'t" : "is not",
	"it\'s" : "it is",
	"let\'s" : "let us",
	"mustn\'t" : "must not",
	"shan\'t" : "shall not",
	"she\'d" : "she had",
	"she\'ll" : "she will",
	"she\'s" : "she is",
	"shouldn\'t" : "should not",
	"that\'s" : "that is",
	"there\'s" : "there is",
	"they\'d" : "they had",
	"they\'ll" : "they will",
	"they\'re" : "they are",
	"they\'ve" : "they have",
	"we\'d" : "we had",
	"we\'re" : "we are",
	"we\'ve" : "we have",
	"weren\'t" : "were not",
	"what\'ll" : "what will",
	"what\'re" : "what are",
	"what\'s" : "what is",
	"what\'ve" : "what have",
	"where\'s" : "where is",
	"who\'d" : "who had",
	"who\'ll" : "who will",
	"who\'re" : "who are",
	"who\'s" : "who is",
	"who\'ve" : "who have",
	"won\'t" : "will not",
	"wouldn\'t" : "would not",
	"you\'d" : "you had",
	"you\'ll" : "you will",
	"you\'re" : "you are",
	"you\'ve" : "you have",
	"y'all" : "you all",
	"yall" : "you all",
	"u" : "you",
	"wanna": "want to",
	"gonna" : "going to",
	}
	i=0
	for word in words:
		if substituteDict.get(word) is not None:
			newWord = substituteDict.get(word)
			wordList = newWord.split(' ')
			words[i] = wordList[0]
			if len(wordList) > 1:
				words.insert(i+1, wordList[1])
		i+=1
	sentence = " ".join(words)
	return sentence

def cleanUpData(listOfTweets):
	i = 0;
	for tweet in listOfTweets:
		listOfTweets[i] = removeUrls(removeSymbols(changeToWill(word_tokenize(removeContractions(tweet.lower())))))
		print(listOfTweets[i])
		i+=1
	return listOfTweets

def trainDataSet():
	print("Loading dataset...")
	dataset = loadTwitterDataset()
	# print(dataset)
	print("Structuring dataset...")
	dataset['testPos'] = appendClasses(structureDataForNaiveBayes(dataset['testPos']), 'positive')
	dataset['testNeg'] = appendClasses(structureDataForNaiveBayes(dataset['testNeg']),'negative')
	dataset['sampleNeg'] = appendClasses(structureDataForNaiveBayes(dataset['sampleNeg']), 'negative')
	dataset['samplePos'] = appendClasses(structureDataForNaiveBayes(dataset['samplePos']), 'positive')
	trainingSet = dataset['samplePos'] + dataset['sampleNeg']
	testSet = dataset['testPos'] + dataset['testNeg']
	print(len(trainingSet), len(testSet))
	global globalClassifier
	globalClassifier = trainAndPrintAccuracy(trainingSet, testSet)

	# getInputFromUser(classifier);
	

def getInputFromUser(input):
	# inputData = input("Enter Search Query: ")
	global globalClassifier
	actualData = predictingQuery(input)
	i=0;
	res = []
	for tweet in actualData['processedText']:
		print(actualData['actualText'][i].text)
		res.append({
			'tweet' : actualData['actualText'][i].text,
			'output' : globalClassifier.classify(tweet)
		})
		i+=1
	print(res)
	return calculatePercentage(res)
	# getInputFromUser(classifier)

def calculatePercentage(predictions):
	numberOfPredictions = len(predictions)
	numberOfPositive = 0
	for prediction in predictions:
		if prediction['output'] == 'positive':
			numberOfPositive+=1
	return numberOfPositive/numberOfPredictions

def echo(input):
	return "Hey dude %s" % input

def appendClasses(sentences, stringToAppend):
	i=0
	for sentence in sentences:
		sentences[i] = [sentence, stringToAppend]
		i+=1
	return sentences

def structureDataForNaiveBayes(sentences):
	i=0
	for words in sentences:
		sentences[i] = dict([(word, True) for word in words])
		i+=1
	return sentences

def trainAndPrintAccuracy(trainingSet, testSet):
	print("Training data...")
	classifier = NaiveBayesClassifier.train(trainingSet)
	accuracy = nltk.classify.util.accuracy(classifier, testSet);
	print(accuracy);
	return classifier

def predictingQuery(inputData):
	fetchedTweets = callTwitterApi(inputData)
	finalTweetsText = []
	for tweet in fetchedTweets:
		finalTweetsText.append(tweet.text)
	# print(finalTweetsText)
	return {
		"processedText" : structureDataForNaiveBayes(cleanUpData(finalTweetsText)),
		"actualText" : fetchedTweets
	}

trainDataSet()