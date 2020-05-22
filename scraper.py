import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from tokenizer import page_token

uniqueURLs = set()  # set
subDomains = {}  # dict {url hostname, num of unique urls}
words = {}  # dict of words and num occurrences
longest_page = ()   # tuple (url, length)

def scraper(url, resp):
    parsed = urlparse(url)
    sub = "http://" + parsed.hostname  # key for subDomains dict
    if resp.status < 400:
        links = [link for link in extract_next_links(url, resp) if is_valid(link)]
        update_info(url, links)
        if sub not in links:
            links.append(sub)
        return links
    else:
        if re.match(r"(www.)?[-a-z0-9.]+\.ics\.uci\.edu", parsed.hostname):  # if url is a .ics.uci.edu subdomain, update dict
            if sub in subDomains and url in uniqueURLs:
                subDomains[sub] -= 1
        if url in uniqueURLs:
            uniqueURLs.remove(url)
        return []


def extract_next_links(url, resp):
    # Implementation required.
    extractedLinks = []
    parsed = urlparse(url)

    # only crawl valid urls with status 200-299 OK series
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status

    if resp.status >= 200 and resp.status <= 299:
        # use beautiful soup here to get html content
        html_content = resp.raw_response.content
        soup = BeautifulSoup(html_content, 'html.parser')

        # findall urls listed on this html doc
        for link in soup.find_all('a', href=True):
            tempLink = link.get('href')
            # link may be incomplete - but!! it may be a complete link
            # to a different domain, so let's check if it's a path first
            # by checking if its an "absolute" url or a "relative" url
            #       https://html.com/anchors-links/#Absolute_vs_Relative_URLs
            if tempLink.startswith("http"):  # absolute url will always have scheme
                tempParsed = urlparse(tempLink)
                if tempParsed.netloc == "" or tempParsed.hostname == "":
                    completeLink = urljoin(url, tempLink)
                else:
                    completeLink = tempLink
            else:  # relative url - always relative to the base url so
                completeLink = urljoin(url, tempLink)  # we can simply urljoin  with original url

            completeLink = completeLink.split("#", 1)[0]
            if "replytocom" in completeLink or "datasets.php?format" in completeLink or "?rev=" in completeLink:
                completeLink = completeLink.split("?", 1)[0]

            if "do=diff" in completeLink:
                completeLink = completeLink.split("&", 1)[0]

            extractedLinks.append(completeLink)

    return extractedLinks


def is_valid(url):
    try:
        if type(url) != str:
            return False

        parsed = urlparse(url)

        if parsed.netloc == "" or parsed.hostname == "":
            return False

        pathnames = (parsed.path).split("/")

        for path in pathnames:
            if pathnames.count(path) > 1:
                return False

        if parsed.scheme not in set(["http", "https"]):
            return False

        if ".jpg" in url:   # not catching jpg for some reason
            return False

        if "do=revisions" in url:
            return False

        checkext = not re.match(
            r".*\.(css|js|bmp|gif|jpeg|ico|jpg"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf|mpg"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|ppsx"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

        # check if domain/path matches requirements
        checkdomain = (re.match(r"(www.)?[-a-z0-9.]*\.ics\.uci\.edu", parsed.hostname) or \
                       re.match(r"(www.)?[-a-z0-9.]*\.cs\.uci\.edu", parsed.hostname) or \
                       re.match(r"(www.)?[-a-z0-9.]*\.informatics\.uci\.edu", parsed.hostname) or \
                       re.match(r"(www.)?[-a-z0-9]*\.stat\.uci\.edu", parsed.hostname) or \
                       (re.match(r"(www.)?today\.uci\.edu", parsed.hostname) and \
                        (re.match(r"\/department\/information_computer_sciences\/.*", parsed.path.lower()))))

        if checkext and checkdomain:
            return True
        else:
            return False

    except TypeError:
        print("TypeError for ", parsed)
        raise


def update_info(url, links):
    temp = page_token(url)

    uniqueTemp = [link for link in links if link not in uniqueURLs]  # temporary list of unique extracted links
    parsed = urlparse(url)
    if re.match(r"(www.)?[-a-z0-9.]+\.ics\.uci\.edu",
                parsed.hostname):  # if url is a .ics.uci.edu subdomain, update dict
        sub = "http://" + parsed.hostname  # key for subDomains dict
        if sub not in subDomains.keys():
            subDomains[sub] = len(
                uniqueTemp)  # if not already in dict, add to dict w value = # of unique links extracted
        else:
            subDomains[sub] += len(uniqueTemp)  # else, add # of unique links extracted to value of corresponding key
    for link in uniqueTemp:
        uniqueURLs.add(link)  # add unique urls to set
    return
