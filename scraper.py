import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation requred.
    extractedLinks = []
    parsed = urlparse(url)
    linkDomain = "http://" + parsed.netloc
    
    '''
    # save (write) data to text files while crawling for report data

    # only crawl valid urls with status 200  OK series
    # if valid and OK status, check if in visitedURLs{}
    if is_valid(url) and (resp.status >= 200 ):
        # use beautiful soup here to get webpage text
        html_content = resp.raw_response.content
        soup = BeautifulSoup(html_content, 'html.parser')
    '''
    
    # findall urls listed on this html doc
    for linkPath in soup.findall('a'):
        link = linkPath.get('href')
        # link may be incomplete
        #https://stackoverflow.com/questions/10893374/python-confusions-with-urljoin
        completeLink = urljoin(linkDomain, linkPath)
        extractedLinks.append(completeLink)
    return extractedLinks

def is_valid(url):
    try:
        parsed = urlparse(url)
        
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        checkext = not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
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
            (re.match(r"\/department\/information_computer_sciences\/.*", parsed.path))))
        
        if checkext and checkdomain:
            return True
        else:
            return False

    except TypeError:
        print ("TypeError for ", parsed)
        raise
