from bs4 import BeautifulSoup
import sys
import re

inputfile = sys.argv[1]

# Read HTML content from a file
with open(f'html_input/{inputfile}', 'r', encoding='utf-8') as file:
    html_cont = file.read()

# Parse the HTML content
soup = BeautifulSoup(html_cont, 'html.parser')

# Extract text using CSS selectors
texts = soup.find_all(re.compile('textarea'))  # Select all <p> tags inside <div class='content'>
outputFileName = sys.argv[2]

for text in texts:
    with open(f'./text_output/{outputFileName}.md', "a", encoding="utf-8") as f:
        f.write(text.getText())