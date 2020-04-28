
from bs4 import BeautifulSoup
import urllib
from nltk.corpus import stopwords

"""
reference of code online: 
https://stackoverflow.com/questions/328356/extracting-text-from-html-file-using-python
"""

def page_token(url):
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html)

    # kill all script and style  elements
    for script in soup(["script", "style"]):
        script.extract()

    # get text
    text = soup.get_text()
    text_str = ""
    for line in text.splitlines():
        for ch in line.lower()
            if not ch.isascii() or not char.isalnum:
                text_str += " "
            else:
                text_str += ch

    # compute word frequencies
    num = {}
    word_count = 0
    for i in text:
        if i in stopwords:
            text.remove(i)
        if i not in num:
            num[i] = text.count(i)
        word_count += 1
    
    num = sorted(num.items(), key = lambda x: x[1], reverse = True)
    top_fifty = list(num.keys())[0-50]
    return top_fifty, word_count

    


    
