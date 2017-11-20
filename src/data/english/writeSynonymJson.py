import sys
import os

import random
import asyncio
from aiohttp import ClientSession

"""
Created by David Goldstein on 11/19/17
Python script to write all english synonyms to large json file
"""

def printProgress (iteration, total, msg, suffix = '', decimals = 0):
  """
  Call in a loop to create terminal progress bar
  @params:
      iteration   - Required  : current iteration (Int)
      total       - Required  : total iterations (Int)
      msg       - Optional  : msg string (Str)
      suffix      - Optional  : suffix string (Str)
      decimals    - Optional  : positive number of decimals in percent complete (Int)
  """
  barLength = 50
  formatStr       = "{0:." + str(decimals) + "f}"
  percents        = formatStr.format(100 * (iteration / float(total)))
  filledLength    = int(round(barLength * iteration / float(total)))
  bar             = '=' * filledLength + '-' * (barLength - filledLength)


  # sys.stdout.write('[ %s %s%s %s \r%s' % ( msg, bar, percents, '%', suffix))
  sys.stdout.write('{:<30}[ {:<50} ]{}%  \r'.format(msg,bar,percents))
  if iteration == total:
      sys.stdout.write('\n')
  sys.stdout.flush()


def readInWordList():
  """
  reads In file with all words in language. Creates node for each word and
  creates verticies to corresponding synonyms
  @return array or False on failure
  """  
  try:
    path = os.path.abspath(os.path.join(os.getcwd())) + '/english/wordList.txt'
    rawWordList = open(path,'r').readlines()

  except IOError:
    print("No such file {}".format(path))
    return False  

  # remove '\r' and '\n'
  cleanedWordList = []
  for word in rawWordList:
    cleanedWordList.append((word.rstrip('\n')).rstrip('\r').lower())
  return cleanedWordList


def scrapeSynonym(word,key='b08CVJHscZ6rRGfc7MzS',language='en_US', max=5):
  """
  scrapes synonyms of word from thesaurus.com
  @params:
      word      - Required  : word to scrape
      key       - Required  : registed key with http://thesaurus.altervista.org/ (string)
    language    - Optional  : language synonym is in
    max       - Optional  : max n of synonsm (int)

  @return dictionary (word : syn list), or None if no synonyms found or invalid word
  """
  endpoint = "http://thesaurus.altervista.org/thesaurus/v1"
  url = endpoint + "?word={}&language={}&key={}&output=json".format(word,language,key)
  r = requests.request('GET', url, timeout=5.0)
  if r.status_code == 200:
    try:
      syns = r.json()['response'][0]['list']['synonyms'].split('|')
    except KeyError or TypeError:
      return None

    del syns[max:]
    for i in range(len(syns)):
      syns[i] = syns[i].split(' ')[0]       

    return {'word' : word,'syns' : syns}



"""
Async code
"""

async def fetch(url, session, i , total, word):
    async with session.get(url) as response:
        delay = response.headers.get("DELAY")
        date = response.headers.get("DATE")
        printProgress(i, total + 1, "{:<25}".format("    " + word))
        return await response.read()


async def bound_fetch(sem, url, session, i, total, word):
    # Getter function with semaphore.
    async with sem:
        await fetch(url, session, i, total, word)


async def run(words):
    url = "http://localhost:8080/{}"
    tasks = []
    # create instance of Semaphore
    sem = asyncio.Semaphore(1000)

    # Create client session that will ensure we dont open new connection
    # per each request.
    async with ClientSession() as session:
        endpoint = "http://thesaurus.altervista.org/thesaurus/v1"
        i = 0
        for word in words:
            i += 1; 
            # pass Semaphore and session to every GET request
            url = endpoint + "?word={}&language={}&key={}&output=json".format(word,'en_US','b08CVJHscZ6rRGfc7MzS')
            task = asyncio.ensure_future(bound_fetch(sem, url, session, i, len(words), word))
            tasks.append(task)


        responses = asyncio.gather(*tasks)
        await responses

# Entrypoint
if __name__ == "__main__":
  printProgress(0,1,'reading word list')
  words = readInWordList()
  printProgress(1,1,'reading word list')

  printProgress(0, len(words),"{:<25}","   fetching words")
  loop = asyncio.get_event_loop()
  future = asyncio.ensure_future(run(words))
  loop.run_until_complete(future)
  printProgress(len(words), len(words),"{:<25}","   fetching words")






