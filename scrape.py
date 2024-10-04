import os
from requests_html import HTMLSession
import csv

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
