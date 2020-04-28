import re
import urllib
from urllib.parse import urlparse, urljoin


from bs4 import BeautifulSoup
# Downloads the data.
import nltk
nltk.download('stopwords')


# Using the stopwords.
from nltk.corpus import stopwords

# Initialize the stopwords
stoplist = set(stopwords.words('english'))
lowInfo = False
visitedURLs = set()
uniqueURLs = set()  # set
subDomains = {}  # dict {url hostname, num of unique urls}

fifty_words = dict()
longestPage = ""
longestWords = 0



def scraper(url, resp):
    if resp.status < 400:
        links = [link for link in extract_next_links(url, resp) if is_valid(link)]
        build_report(url, links)
        output()
        return links
    else:
        parsed = urlparse(url)
        if re.match(r"(www.)?[-a-z0-9.]+\.ics\.uci\.edu",parsed.hostname):  # if url is a .ics.uci.edu subdomain, update dict
            # use http for all to avoid double keys of same subdomain
            sub = "http://" + parsed.hostname  # key for subDomains dict
            if sub in subDomains and url in uniqueURLs:
                    subDomains[sub] -= 1
        if url in uniqueURLs:
            uniqueURLs.remove(url)
        return []



def extract_next_links(url, resp):
    global longestWords,longestPage
    # Implementation requred.
    extractedLinks = []

    # different formats
    # http://www.ics.uci.edu/~kay/scheme/restaurants2.scm

    if resp.status >= 200 and resp.status <= 299:
        # avoid crawling the same page twice
        if url not in visitedURLs:
            visitedURLs.add(url)

            # use beautiful soup here to get html content
            html_content = resp.raw_response.content
            soup = BeautifulSoup(html_content, 'html.parser')
            # parse text and avoid low info pages
            pageLength = page_token(url)
            if pageLength == 0:
                return []

            # longest page
            if pageLength > longestWords:
                longestPage = url
                longestWords = pageLength

            #print("LENGTH OF 50 --> " + str(len(fifty_words)))

            # findall urls listed on this html doc
            for link in soup.find_all('a', href=True):
                tempLink = link.get('href')
                # link may be incomplete - but!! it may be a complete link
                # to a different domain, so let's check if it's a path first
                # by checking if its an "absolute" url or a "relative" url
                #       https://html.com/anchors-links/#Absolute_vs_Relative_URLs
                if tempLink.startswith("http"):  # absolute url will always have scheme
                    completeLink = tempLink
                else:  # relative url - always relative to the base url so
                    completeLink = urljoin(url,
                                           tempLink)  # we can simply urljoin  with original url

                completeLink = completeLink.split("#", 1)[0]
                # avoid calendar traps
                # https://today.uci.edu/department/information_computer_sciences/calendar
                if "/calendar" in completeLink:
                    completeLink = completeLink.split("/calendar", 1)[0]
                    return completeLink
                #AVOID similar links
                if "ics.uci.edu" in completeLink:
                    if "evoke" in completeLink and "replytocom" in completeLink:
                        completeLink = completeLink.split("?",1)[0]
                    else:
                        completeLink = is_similar(completeLink)

                #if "www.informatics.uci.edu/files/pdf/InformaticsBrochure-March2018" in completeLink:
                   # completeLink = completeLink.split("/pdf", 1)[0]

                # http://www.ics.uci.edu/~kay/wordlist.txt --> long list of all words

                extractedLinks.append(completeLink)

    return extractedLinks

def is_similar(completeLink):
    # Avoid these traps urls

    if "wics.ics.uci.edu/events" in completeLink:
        completeLink = completeLink.split("/events", 1)[0]
        return completeLink
    if "stayconnected" in completeLink:
        completeLink = completeLink.split("/stayconnected", 1)[0]
        return completeLink
    if "hall_of_fame" in completeLink:
        completeLink = completeLink.split("/hall_of_fame", 1)[0]
        return completeLink
    if "www.ics.uci.edu/index.php" in completeLink:
        completeLink = completeLink.split("/vod", 1)[0]
        return completeLink
    if "cbcl.ics.uci.edu" in completeLink:
        if "/public_data/wgEncodeBroadHistone" in completeLink:
            completeLink = completeLink.split("/wgEncodeBroadHistone", 1)[0]
            return completeLink
        if ".edu/doku.php/people?rev=" in completeLink:
            completeLink = completeLink.split("?rev", 1)[0]
            return completeLink
    if "ics.uci.edu/accessibility" in completeLink:
        completeLink = completeLink.split("/accessibility", 1)[0]
        return completeLink
    if "grape.ics.uci.edu/wiki/asterix/wiki/stats170ab-2018?" in completeLink: # ""www.ics.uci.edu/~kay/wordlist.txt" in completeLink:
        completeLink = completeLink.split("?", 1)[0]
        return completeLink
    if "archive.ics.uci.edu/ml/machine-learning-databases/" in completeLink:
        completeLink = "http://archive.ics.uci.edu/ml/machine-learning-databases"
        return completeLink
    if "archive.ics.uci.edu/ml/datasets.php?" in completeLink:
        completeLink = completeLink.split("?", 1)[0]
        return completeLink
    #if "www.ics.uci.edu/~kay/wordlist.txt" in completeLink:
     #   completeLink = completeLink.split("/~kay", 1)[0]
    #    return completeLink
    return completeLink

def is_valid(url):
    try:
        parsed = urlparse(url)

        pathnames = (parsed.path).split("/")

        for path in pathnames:
            if pathnames.count(path) > 1:
                return False
        
        if parsed.scheme not in set(["http", "https"]):
            return False

        if ".jpg" in url:  # not catching jpg for some reason
            return False

        if "do=revisions" in url:
            return False

        checkext = not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|jpg|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|mpg|ram|m4v|mat|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|ppsx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|scm|wma|zip|rar|gz)$", parsed.path.lower())

        # check if domain/path matches requirements
        if parsed.hostname == "" or parsed.hostname == None:
            checkdomain = False
        else:
            checkdomain = (re.match(r"(www.)?[-a-z0-9.]*\.ics\.uci\.edu", parsed.hostname) or \
                           re.match(r"(www.)?[-a-z0-9.]*\.cs\.uci\.edu", parsed.hostname) or \
                           re.match(r"(www.)?[-a-z0-9.]*\.informatics\.uci\.edu", parsed.hostname) or \
                           re.match(r"(www.)?[-a-z0-9]*\.stat\.uci\.edu", parsed.hostname) or \
                           (re.match(r"(www.)?today\.uci\.edu", parsed.hostname) and \
                        (re.match(r"\/department\/information_computer_sciences\/.*",parsed.path))))

        if checkext and checkdomain:
            return True
        else:
            return False

    except TypeError:
        print("TypeError for ", parsed)
        raise

def page_token(url):

    try:
        global fifty_words, longestWords, longestPage, lowInfo
        pageLength = 0
        response = urllib.request.urlopen(url)
        if response.getcode() >= 200 and response.getcode() <= 299:
            html_content = response.read()
            soup = BeautifulSoup(html_content, 'html.parser')
            for script in soup(["script", "style"]):
                script.extract()

            text = soup.get_text()
            text = text.strip().lower().split()

            # avoid low info pages
            if len(text) < 200:
                lowInfo = True
                return 0

            for i in text:
                if i in stoplist or len(i) < 3:
                    text.remove(i)
                else:
                    pageLength += 1
                    if i not in fifty_words:
                        fifty_words[i] = 1
                    else:
                        fifty_words[i] += 1

            if len(text) > longestWords:
                longestPage = url
                longestWords = len(text)

    except:
        return 0
    return pageLength

def build_report(url, links):
    uniqueTemp = [link for link in links if
                  link not in uniqueURLs]  # temporary list of unique extracted links
    parsed = urlparse(url)

    proceed = True
    # check if hostname is ""
    if parsed.hostname == "":
        proceed = False

    if proceed:
        if re.match(r"(www.)?[-a-z0-9.]+\.ics\.uci\.edu",
                    parsed.hostname):  # if url is a .ics.uci.edu subdomain, update dict
            # use http for all to avoid double keys of same subdomain
            sub = "http://" + parsed.hostname  # key for subDomains dict
            if sub not in subDomains.keys():
                subDomains[sub] = len(
                    uniqueTemp)  # if not already in dict, add to dict w value = # of unique links extracted
            else:
                subDomains[sub] += len(
                    uniqueTemp)  # else, add # of unique links extracted to value of corresponding key

    for link in uniqueTemp:
        uniqueURLs.add(link)  # add unique urls to set

    return

def output():
    # write uniqueURLs to txt file
    with open("report.txt", "w") as file:
        file.write("Q1)\n" + str(len(uniqueURLs)) + " unique URLs found.\n\n")

        file.write("Q2)\n")
        file.write("Longest page: " + longestPage + "  " + str(
            longestWords) + " words\n\n")
        file.write("Q3)\n")
        file.write("50 most common words:\n")
        c = 0
        for token, count in sorted(fifty_words.items(), key=lambda x: x[1],
                                   reverse=True):
            if c >= 50:
                break
            file.write(token + " : " + str(count) + "\n")
            c += 1
        file.write("Number of unique words: " + str(len(fifty_words)) + "\n\n")

        file.write("Q4)\n")
        file.write("Subdomain , number of unique pages\n\n")
        for url, num in sorted(subDomains.items()):
            file.write(url + ", " + str(num) + "\n")
