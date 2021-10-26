from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import asksaveasfile
from PIL import ImageTk, Image
import requests, bs4, lxml, re
import  xlsxwriter
import datetime
from datetime import timedelta


# Define date, as on jobs.bg ads have date "today" and "yesterday" --> will use .replace() in date

today = datetime.datetime.now()
yesterday = today - timedelta(days = 1)

def save(file):
    files = [('xlsx', '*.xlsx')]
    file = asksaveasfile(filetypes = files, defaultextension = files)

#Create Tkinter window

window = Tk()
window.title("Job finder by Stefan Tonchev")
window.configure(background = "black")
window.option_add('*Font', 'Broadway 14')
window.geometry("1000x750")
window.resizable(False, False)
window.wm_iconbitmap('img/ico.ico')
photo_main = ImageTk.PhotoImage(file = "img/BGR.jpg")
Label(window, image = photo_main, bg= "black").grid(row = 0, columnspan = 2)

#Choose website - jobs.bg or zaplata.bg (Label --> 2x Radioubtton)

Label(window, text = "Please choose website:" , fg = "white", bg= "black").grid(row = 1, column = 0 , sticky = "w", padx = 30, pady = 10)
i = IntVar()
R1 = Radiobutton(window, text="jobs.bg       ", value=1, variable = i).grid(row = 2 , column = 0 , sticky = "w", padx = 30, pady = 10)
R2 = Radiobutton(window, text="zaplata.bg", value=2, variable = i).grid(row = 3, column = 0 , sticky = "w" , padx = 30)
r1 = StringVar()
r2 = StringVar()

#Choose job category - IT or Administration (Label --> OptionMenu)

Label(window, text = "Please choose category:" , fg = "white", bg= "black").grid(row = 4, column = 0 , sticky = "w", padx = 30, pady = 10)
options = ["it", "administration"]
selected_category = StringVar()
mb = OptionMenu(window, selected_category,*options)
mb.grid(row = 5, column = 0, sticky = "w", padx = 30)

#Choose number of pages to look through (Label --> Spinbox)

Label(window, text = "Please choose number of pages to look for:" , fg = "white", bg= "black").grid(row = 7, column = 0 , sticky = "w", padx = 30, pady = 10)
pages = StringVar()
pages_number = Spinbox(window, width = 3, from_ = 0, to = 1000, textvariable=pages).grid(row = 7, column = 0, padx = 460, pady = 10)

#Enter keywords for the search(Label --> Entry)

Label(window, text = "Please enter keywords to search for, spereated by comma:" , fg = "white", bg= "black").grid(row = 8, column = 0 , sticky = "w", padx = 30, pady = 10)
words = StringVar()
keywords_entry = Entry(window, width = 25, textvariable=words).grid(row = 9, column = 0, sticky = "w", padx = 30, pady = 10)






#----------------------------------------------------------

#Submit button

def submit_btn():

    #Create workbook
    files = [('Excel Document', '.xlsx'), ('All Files', '*.*')]
    workbook = xlsxwriter.Workbook("Result/result.xlsx")
    worksheet = workbook.add_worksheet()
    worksheet.write('A1', "Job Title")
    worksheet.write('B1', 'Date')
    worksheet.write('C1', 'Description')
    worksheet.write('D1', 'Link')

    #Get choice from RadioButton
    choose_website = ""
    if i.get() == 1:
        choose_website = "jobs"
    elif i.get() == 2:
        choose_website = "zaplata"

    # Get choice from OptionMenu
    choose_categories = ""
    if selected_category.get() == "it":
        choose_categories = "it"
    elif selected_category.get() == "administration":
        choose_categories = "administration"

    # Get data from SpinBox
    number_of_pages = int(pages.get())

    #Get data from Entry and create list -> if multiple keywords, split into elements
    keyword_list = words.get().split(",")

    #Bool if job is not found with selected criteria -> Will be false if any job is found
    job_not_found = True
    # Define counter(will be incrementing) for writing data in excel row
    row = 1


    if choose_website == "jobs" or choose_website == "jobs.bg":

        for page in range(1,number_of_pages * 15 + 1, 15): #pages go trough 15 in url ->1st page is 15, second 30...

            if choose_categories == "it":
                result = requests.get("https://www.jobs.bg/front_job_search.php?frompage= " + str(page) +"&categories%5B0%5D=56&term=#paging").text

            elif choose_categories == "administration":

                result = requests.get("https://www.jobs.bg/front_job_search.php?frompage= " + str(page) + "&categories%5B0%5D=38&term=#paging").text

            soup = bs4.BeautifulSoup(result, "lxml")



            jobs = soup.find_all('td', class_ = "offerslistRow")

            for job in jobs:
                try:
                    job_title = job.find('a').text.lower()
                except:
                    job_title = "N/A"

                if any(keyword in job_title for keyword in keyword_list):
                    try:
                        date = job.find('span', class_="card__subtitle").text.strip().replace("днес", str(today.strftime("%d"+ "." + "%m" + "." + "%y"))).replace("вчера", str(yesterday.strftime("%d"+ "." + "%m" + "." + "%y")))
                    except:
                        date = "N/A"

                    try:
                        description = job.find('div', class_="card__subtitle").text.lstrip()
                    except:
                        description = "N/A"
                    try:
                        more_info = "https://www.jobs.bg/" + job.a['href']
                    except:
                        more_info = "N/A"

                    job_not_found = False

                    # Printing ad in console to check if working

                    print(f"Job title: {job_title}")
                    print(f"Added : {date}")
                    print(f"Description: {description}")
                    print(f"More info : {more_info}")
                    print("-----------------------------------------------------")

                    #Writing data in Excel


                    worksheet.write(row, 0, job_title)
                    worksheet.write(row, 1, date)
                    worksheet.write(row, 2, description)
                    worksheet.write(row, 3, more_info)

                    #Incrementing row for next job ad

                    row += 1



        #save(workbook)

    elif choose_website == "zaplata" or choose_website == "zaplata.bg":

        for page in range(1, number_of_pages + 1):

            if choose_categories == "it":

                result = requests.get("https://www.zaplata.bg/it/" + '?page=' + str(page)).text

            elif choose_categories == "administration":

                result = requests.get("https://www.zaplata.bg/administrativni-deynosti/" + '?page=' + str(page)).text


            soup = bs4.BeautifulSoup(result, "lxml")

            jobs = soup.find_all('li', class_="c2")


        for job in jobs:
            #print("Searching...")
            job_title = job.find('a').text.lower()


            if any(keyword in job_title for keyword in keyword_list):
                try:
                    date, location = job.find('span', class_ = "location").text.split(",")
                except:
                    date = "N/A"
                    location = "N/A"
                try:
                    salary = job.find('span', class_ = "is_visibility_salary").text.replace("Заплата от: " , "").replace("до", "-")
                except:
                    salary = "N/A"
                try:
                    more_info = job.a['href']
                except:
                    more_info = "N/A"

                job_not_found = False

                worksheet.write('A1', "Job Title")
                worksheet.write('B1', "Date")
                worksheet.write('C1', 'Location')
                worksheet.write('D1', 'Salary')
                worksheet.write('E1', 'Link')
                worksheet.write(row, 0, job_title)
                worksheet.write(row, 1, date)
                worksheet.write(row, 2, location)
                worksheet.write(row, 3, salary)
                worksheet.write(row, 4, more_info)

                row += 1

                print(f"Job title: {job_title}")
                print(f"Location: {location}")
                print(f"Salary: {salary}")
                print(f"More info : {more_info}")

        #files = [('Excel Document', '.xlsx'), ('All Files', '*.*')]
        workbook2 = workbook.asksaveasfile(filetypes=files, defaultextension=files)
        workbook.close()

    if job_not_found:
        #print("Sorry, no job was found with this keyword...")
        messagebox.showerror("Result", "No result found with selected criteria.")
    else:
        messagebox.showinfo(title="File completed!" , message="File completed. Please find it in Result folder.")

button_submit = Button(window, text ="Search", command = submit_btn).grid(row = 12, column = 0, pady = 20)
window.mainloop()