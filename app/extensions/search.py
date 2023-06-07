import re
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup


def search(search_word):
    try:
        url = 'https://baike.baidu.com/item/' + urllib.parse.quote(search_word)
        html = urllib.request.urlopen(url)
        content = html.read().decode('utf-8')
        html.close()
        soup = BeautifulSoup(content, 'lxml')
        text = soup.find('div', class_="lemma-summary").children

        message_return = ""
        for message_searched in text:
            word = re.sub(re.compile(r"<(.+?)>"), '', str(message_searched))
            word = word.replace(' ', '').replace('\n', '')
            words = re.sub(re.compile(r"\[(.+?)\]"), '', word)
            message_return = message_return+'  '+words+'\n'
        return True, message_return
    except Exception as e:
        print(str(e))
        return False, "Failed! Please enter more in details!"
