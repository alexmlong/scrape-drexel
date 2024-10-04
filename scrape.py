import os
from requests_html import HTMLSession
import csv
# ImportError: lxml.html.clean module is now a separate project lxml_html_clean.
# Install lxml[html_clean] or lxml_html_clean directly.
# from lxml.html.clean import clean_html
session = HTMLSession()
r = session.get('https://drexel.edu/Search?type=student&q=a&page=1&app=directory')
r.html.render()

# this is what we're trying to scrape:
# 
# <div class="directory-list-item__body"><div class="directory-list-item__title is-visible"><span>Aho, Layton, Electrical Engineering, College of Engineering</span></div><div class="directory-list-item__info"><div class="directory-list-item__contact"><div class="directory-list-item__contact-item"><a class="icon-link" href="mailto:layton.aho@drexel.edu"><span class="icon-link__icon"><svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="24" height="24" viewBox="0 0 24 24" role="img" focusable="false">
#   <g fill-rule="evenodd">
#     <path d="M20,4 L4,4 C2.9,4 2.01,4.9 2.01,6 L2,18 C2,19.1 2.9,20 4,20 L20,20 C21.1,20 22,19.1 22,18 L22,6 C22,4.9 21.1,4 20,4 L20,4 Z M20,8 L12,13 L4,8 L4,6 L12,11 L20,6 L20,8 L20,8 Z"></path>
#   </g>
# </svg>
# </span><span class="icon-link__text">layton.aho@drexel.edu</span></a></div></div><div class="directory-list-item__location"></div></div></div>

# we want to extract the name, department, college, and email address from this div

student = r.html.find('.directory-list-item__body')

def extractStudent(studentEl):
    title = studentEl.find('.directory-list-item__title', first=True).text
    title = title.split(',')
    name = f"{title[0]}, {title[1]}"
    department = title[2]
    college = title[3]
    email = studentEl.find('.icon-link__text', first=True).text
    return {
        'name': name,
        'department': department,
        'college': college,
        'email': email
    }

studentIndex = 0
headersNeeded = True
for letter in 'abcdefghijklmnopqrstuvwxyz':
    print(f'Getting students with search term {letter}')
    page = 1
    noSearchResults = False
    while not noSearchResults:   
        students = [] 
        print(f'Getting page {page}')
        r = session.get(f'https://drexel.edu/Search?type=student&q={letter}&page={page}&app=directory')
        r.html.render()
        studentsEls = r.html.find('.directory-list-item__body')
        for studentEl in studentsEls:
            try:
                student = extractStudent(studentEl)
            except Exception as e:
                print('Error extracting student, skipping')
                print('Error:', e)
                print("HTML:")
                print(studentEl.html)
                continue

            student['index'] = studentIndex
            students.append(student)
            studentIndex += 1

        if len(studentsEls) == 0:
            noSearchResults = True
        else:
            page += 1
        
        with open('students.csv', 'a', newline='') as csvfile:
            fieldnames = ['index', 'name', 'department', 'college', 'email']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if headersNeeded:
                writer.writeheader()
                headersNeeded = False

            for student in students:
                writer.writerow(student)