from bs4 import BeautifulSoup
import requests
from urlparse import urlparse, urljoin
from robotparser import RobotFileParser

def getRobots(url):
    parsed = urlparse(url)
    robots_url = parsed.scheme + '://' + parsed.netloc + '/robots.txt'
    if robots_url not in robots:
        rp = RobotFileParser()
        try:
            r = requests.get(robots_url, verify=False, timeout=1)
            r.raise_for_status()
        except Exception:
            rp.parse('')
        else:
            rp.parse(r.text)
        #print "  new robot at " + robots_url
        robots[robots_url] = rp
    return robots[robots_url]

def isValid(url, check_robots):
    parsed = urlparse(url)
    is_http = parsed.scheme.startswith("http")
    is_umich = parsed.netloc.endswith("umich.edu")
    if (not is_http) or (not is_umich):
        return False
    if check_robots:
        is_allowed = getRobots(url).can_fetch("*", url.encode("ascii"))
    else:
        is_allowed = True
    unseen = url not in seen
    return unseen and is_allowed

start = "http://www.eecs.umich.edu"
seen = {}
robots = {}
queue = [start]
queue_index = 0

while len(seen) < 1500 and len(queue) != 0:

    url = queue[queue_index]
    queue_index += 1

    if isValid(url, True):
        try:
            r = requests.get(url, verify=False, timeout=.5)
            r.raise_for_status()
        except Exception:
            pass
        else:
            if "html" in r.headers["content-type"]:
                data = r.text
                seen[url] = True
                print url
                #print url + ' (#' + str(len(seen)) + ', queue @ ' + str(queue_index) + '/' + str(len(queue)) + ')'

                soup = BeautifulSoup(data)

                for link in soup.find_all('a'):
                    href = urljoin(url, link.get('href'))
                    if isValid(href, False):
                        queue.append(href)
