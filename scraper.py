import re
from urllib.parse import urlparse, urljoin

from bs4 import BeautifulSoup
# Downloads the data.
import nltk
nltk.download('stopwords')


# Using the stopwords.
from nltk.corpus import stopwords

# Initialize the stopwords
stoplist = stopwords.words('english')

uniqueURLs = set()  # set
subDomains = {}  # dict {url hostname, num of unique urls}
visitedURLs = set()  #set of already crawled urls

fifty_words = list()
longestPage = ""
longestWords = 0
cur_wordCount = 0

def scraper(url, resp):
    links = [link for link in extract_next_links(url, resp) if is_valid(link)]
    build_report(url, links)
    output()
    return links


def extract_next_links(url, resp):
    global longestWords,longestPage, fifty_words
    # Implementation requred.
    extractedLinks = []

    # different formats
    # http://www.ics.uci.edu/~kay/scheme/restaurants2.scm

    if resp.status >= 200 and resp.status <= 299:
        # avoid similar pages and traps
       # if url not in visitedURLs:
           # visitedURLs.add(url)

        # use beautiful soup here to get html content
        html_content = resp.raw_response.content
        soup = BeautifulSoup(html_content, 'html.parser')

        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text()
        TopCommon_words = page_token(text)

        if len(fifty_words) == 0:
            fifty_words.extend(TopCommon_words)
        else:
            fifty_words.clear()
            fifty_words.extend(getCommonWords(TopCommon_words))

        # Q3) longest page
        if longestWords < cur_wordCount:
            longestPage = url
            longestWords = cur_wordCount

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
            #AVOID similar links
            if "ics.uci.edu" in completeLink:
                if "evoke" in completeLink and "replytocom" in completeLink:
                    completeLink = completeLink.split("?",1)[0]
                else:
                    completeLink = is_similar(completeLink)

            # http://www.ics.uci.edu/~kay/wordlist.txt --> long list of all words

            extractedLinks.append(completeLink)

    return extractedLinks

def is_similar(completeLink):
    # Avoid these traps urls
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
        if ".edu/doku.php/people?rev=1418330812&do=diff" in completeLink:
            completeLink = completeLink.split("=diff", 1)[0]
            return completeLink
    if "wics.ics.uci.edu/events" in completeLink:
        completeLink = completeLink.split("/events", 1)[0]
        return completeLink
    if "ics.uci.edu/accessibility" in completeLink:
        completeLink = completeLink.split("/accessibility", 1)[0]
        return completeLink
    if "www.ics.uci.edu/~kay/wordlist.txt" in completeLink:
        completeLink = completeLink.split("/~kay", 1)[0]
        return completeLink

    return completeLink

def is_valid(url):
    try:
        parsed = urlparse(url)

        if parsed.scheme not in set(["http", "https"]):
            return False

        checkext = not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
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


def page_token(text):
    global cur_wordCount


    text = text.strip().lower().split()
    num = dict()
    word_count = 0
    for i in text:
        if i in stoplist:
            text.remove(i)
        else:
            if i not in num:
                num[i] = text.count(i)
        word_count += 1

    num = sorted(num.items(), key=lambda x: x[1], reverse=True)

    if len(num) <= 50:
        top_fifty = num
    else:
        top_fifty = num[0 - 49]
    cur_wordCount = word_count
    return top_fifty

def getCommonWords(TopCommon_words):
    """
    :param tokens_1: list, tokens_2: list
    :return: none
    Finds intersection of the two sets and prints its length.
    """
    t1 = set(fifty_words)
    t2 = set(TopCommon_words)
    commonWords = []
    for word in t1:
        if word in t2:
            commonWords.append(word)
    return commonWords

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
    with open("unique_q1.txt", "w") as file:
            file.write("Q1)\n" + str(len(uniqueURLs)) + " unique URLs found.\n")

    with open("q_2and3.txt", "w") as file2:
        file2.write("Q2)\n")
        file2.write("Longest page: " + longestPage + "\n\n")

    '''
    # Q2
        with open("q_2and3.txt", "w") as file2:
            file2.write("Q2)\n")
            file2.write("Longest page: " + longestPage + "\n\n")
            file2.write("Q3)\n")
            file2.write("50 most common words:\n")
            for word in fifty_words:
                file2.write(str(word[0]))
                file2.write("\n")
    
    '''


    # write subdomain to txt file
    with open("subdomains_q4.txt", "w") as file1:
        file1.write("Q4)\n")
        for url, num in sorted(subDomains.items()):
            file1.write(url + ", " + str(num) + "\n")
