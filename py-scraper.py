from bs4 import BeautifulSoup
import requests

#can take multiple url's in a list

url = "https://en.wikipedia.org/wiki/Chuck_Norris"
r = requests.get(url)
html_content = r.text
soup = BeautifulSoup(html_content, 'html.parser')

for script in soup(["script", "style"]):
    script.extract()    # rip it out
soup = soup.get_text().strip().split()

uniquewords = {}

for i in soup:
    if i not in uniquewords:
        uniquewords[i] = 0
for i in soup:
    uniquewords[i] += 1

order = sorted(uniquewords, key = uniquewords.get, reverse=True)
values = [uniquewords[key] for key in order]

# for i in range(50):
#     print(order[i], ":",values[i])

for i in range(100):
    print(order[i])

#appends result to a csv file
# with open('index.csv','a') as csv_file:
#     writer = csv.writer(csv_file)
#     writer.writerow([h1, datetime.now()])
