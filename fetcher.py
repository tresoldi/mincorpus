# encoding: utf-8

import json
import random
import langid
import twitter

# some Esperanto words with at least three letters, mostly from
# https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/Esperanto
# (I didn't include words very common in other languages)
SEARCH_WORDS = ['kaj', 'estas', 'estis', 'kun', 'kiu', 'pri',
	'kiel', 'pli', u'ankaŭ', 'tiu', 'plej', 'dum', 'jaro',
	'jaroj', 'urbo', 'urboj', 'havas', 'havis', 'kiuj',
	u'ĝis', 'aliaj', 'povas', 'povis', 'unua', 'lingvo',
	'lingvoj', 'jam', 'kie', 'tiuj', 'kiam', 'granda',
	'grandaj', 'multaj', u'antaŭ', 'kelkaj', 'kies', 'ties',]
	
# how many words to extract from the list above with random search
SEARCH_LENGTH = 2

# the language to filter the tweets
CORPUS_LANG = 'eo'

# Logs into twitter, returning the 'api' object
def open_twitter(filename='twitter_tokens.json'):
	# load secrets from file
	handler = file(filename)
	source = handler.read()
	handler.close()

	# parse JSON
	secret = json.loads(source)

	# log into twitter
	api = twitter.Api(consumer_key=secret['consumer_key'],
                      consumer_secret=secret['consumer_secret'],
                      access_token_key=secret['access_token_key'],
                      access_token_secret=secret['access_token_secret'])
	
	# return handler
	return api

def query(api, term, count=100):
	result = {}
	
	for entry in api.GetSearch(term=term, count=count):
		result[entry.id] = [entry.created_at,
					        entry.user.screen_name,
							entry.user.lang,
							entry.user.location,
					        entry.text]

	return result
	
# load already fetched data (simple csv-like file)
# TODO: use a proper sqlite
def load_database(filename='corpus.txt'):
	# I know, that's not how it is supposed to be done...
	ret = []
	try:
		with file(filename) as handler:
			for line in handler:
				tokens = line[:-1].split("|")
				ret.append(tokens)
	except:
		# first run, file does not exist
		pass
		
	return ret
	
def tweet2csv(tweet):
	# very basic escaping
	tweet[-1] = tweet[-1].replace('\\', '\\\\')
	tweet[-1] = tweet[-1].replace('|',  '\\|')
	tweet[-1] = tweet[-1].replace('\n', '<br>')
	
	return '|'.join(tweet)
	
# main loop
def run():
	# load current database and expand the word list if possible
	database = load_database()
	
	# open connection
	api = open_twitter()
	#print api.VerifyCredentials()

	handler = file('corpus.txt', 'a')
	for i in range(10):
		# new random search term
		term = ' '.join(random.sample(SEARCH_WORDS, SEARCH_LENGTH))
		print "Searching for '%s'..." % str([term])
		tweets = query(api, term, 10)
		
		for id in tweets:
			# is it in the language we want?
			if langid.classify(tweets[id][-1])[0] != CORPUS_LANG:
				continue
			
			et = tweet2csv(tweets[id])
			buf = '%s|%s\n' % (id, et.encode('utf-8'))
			handler.write(buf)

	handler.close()
	
# program starts here
if __name__ == '__main__':
	run()



