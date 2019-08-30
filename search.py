#!/usr/bin/python

import requests
import json
import time
import sys
from collections import Counter
import csv, codecs, cStringIO

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.

    Source: https://docs.python.org/2/library/csv.html
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

def prettyPrint(counter):
    c = counter.most_common()
    for entry in c:
        print str(entry[1]) + " - " + entry[0]

def getMembers(guildId, session, limit = 1000):
  return session.get('https://discordapp.com/api/v6/guilds/{}/members?limit={}'.format(guildId, limit)).json()

def searchContent(query, guildId, session, maxToSearch = 200):
  return search("content={}".format(query), guildId, session, maxToSearch)

def searchByAuthor(authorId, guildId, session, maxToSearch = 1):
  return search("author_id={}".format(authorId), guildId, session, maxToSearch)

def search(query, guildId, session, maxToSearch = 200):
    offset = 0
    results = 0
    messageCounter = Counter()
    print "offset = ",
    while offset <= results and offset < maxToSearch:
        print offset,
        sys.stdout.flush()

        time.sleep(0.8)
        url = 'https://discordapp.com/api/v6/guilds/{}/messages/search?{}&offset={}'.format(guildId, query, offset)
        response = session.get(url)
        responseJson = json.loads(response.text)

        results = responseJson['total_results']
        for messageGroup in responseJson['messages']:
            for message in messageGroup:
                if 'hit' in message and message['hit']:
                    author = message['author']
                    user = u"{}#{}".format(author['username'], author['discriminator'])
                    messageCounter.update({user: 1})

        offset += 25

    print "\nTotal hits for {} in guild {}: {}".format(query, guildId, results)
    print "Counts for latest {} search results: ".format(min(maxToSearch, results))
    prettyPrint(messageCounter)

    return [results, messageCounter]

def main():
    usage = '''Usage: ./search.py {guildId} {authorization token} {output file} {search1} [search2] [search3]...'''

    if len(sys.argv) < 5:
        print usage
        sys.exit(1)

    s = requests.Session()
    s.headers.update({'Authorization': sys.argv[2]})

    queries = sys.argv[4:]
    results = []
    for q in queries:
        results.append([q] + searchByContent(q, int(sys.argv[1]), s))

    outfile = sys.argv[3]

    keys = reduce(lambda a,b: a|b, [set(res[2]) for res in results], set())
    headers = ['String', 'Length', 'Total'] + sorted(list(keys), key=lambda u: -results[0][2][u])

    with open(outfile, 'w') as fout:
        writer = UnicodeWriter(fout)
        writer.writerow(headers)

        for entry in results:
            query, total, stats = entry
            row = [query, len(query), total] + [stats[user] for user in headers[3:]]
            writer.writerow([str(i) for i in row])

if __name__ == '__main__':
    main()
