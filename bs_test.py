from bs4 import BeautifulSoup

html="<!DOCTYPE html><html><head><title>Page Title</title></head><body><h3><b id='boldest'>Lebron James</b></h3><p> Salary: $ 92,000,000 </p><h3> Stephen Curry</h3><p> Salary: $85,000, 000 </p><h3> Kevin Durant </h3><p> Salary: $73,200, 000</p></body></html>"
soup = BeautifulSoup(html, 'html.parser')
tag_title = soup.title
tag_head = soup.head
tag_body = soup.body


body_parent = tag_body.parent
body_children = tag_body.children

for child in body_children:
    print("\t|child content:", child.string)

# print(type(body_parent))
# print(soup.prettify())

