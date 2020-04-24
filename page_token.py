from bs4 import BeautifulSoup
import urllib
import scraper
import nltk

nltk.download('stopwords')

from nltk.corpus import stopwords

stop_words = set(stopwords.words('english'))

"""
reference of code online: 
https://stackoverflow.com/questions/328356/extracting-text-from-html-file-using-python
"""

def page_token(url):
    try:
        response = urllib.request.urlopen(url)
        if response.getcode() >= 200 and response.getcode() <= 299:
            html_content = response.read()
            soup = BeautifulSoup(html_content)
            for script in soup(["script", "style"]):
                script.extract()

            text = soup.get_text()
            text = text.strip().lower().split()
            for i in text:
                if i in stop_words:
                    text.remove(i)
                else:
                    if i not in scraper.words:
                        scraper.words[i] = 1
                    else:
                        scraper.words[i] += 1

            if scraper.longest_page:
                if len(text) > scraper.longest_page[1]:
                    scraper.longest_page = (url, len(text))
            else:
                scraper.longest_page = (url, len(text))
    except:
        return

    return
    
