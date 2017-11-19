from bs4 import BeautifulSoup
import requests


r = requests.get('http://www.nltk.org/book/ch00.html')
html_content = r.text
soup = BeautifulSoup(html_content, 'html.parser')

for script in soup(["script", "style"]):
    script.extract()    # rip it out

# name = soup.extract(["h1"])

#how to change HTML tag
# tag = soup.p
# tag.name = "blockquote"
# tag['class'] = 'verybold'
# tag['id'] = 1

#successfully extracts a cleaned up H1 tag
# for i in soup:
#     if i.find('h1') == -1:
#         pass
#     else:
#         print(i.find('h1').get_text())

# for script in soup(["h1", "p"]):
#     print(script.extract())

h1 = soup.find_all(["h1"]) #list of h1
p = soup.find_all(["p"]) #list of p

h1p = soup.find_all(["h1","p"])

h1_ = []
p_ = []

# for i in h1p:
#     if i.prettify(formatter="html").find('h1') == True:
#         h1_append(i)
#     if i.find('p') == True:
#         p_.append(i)
# print(h1_)
# print(h1p[2]) #bs element

# print(h1p[0].prettify(formatter="html")) #string

t = soup.body
print(type(t))
# print(soup.body)

# t = h1p[0]
# print(t)
# # print(type(t))
#
# print(t.find("h1"))

# print(t.find('h1'))


# t = h1p[0].prettify(formatter="html").get_text()
