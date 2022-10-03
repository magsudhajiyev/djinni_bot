from urllib import response
from bs4 import BeautifulSoup as bs
import requests
import json

class Bot:
    def __init__(self, data):
        self.MAIN_URL = data["main_url"]
        self.EMAIL = data["email"]
        self.PASSWORD = data["password"]
        self.CV_URL = data["cv_url"]
        self.MESSAGE = data["message"]
        self.KEYWORD = data["keyword"]
        self.client = requests.Session()
        
    def start(self):
        self.client = requests.Session()
        self.client.get(self.MAIN_URL)
        csrftoken = self.client.cookies["csrftoken"]

        login_url = self.MAIN_URL+'/login'

        login_data = dict(email=self.EMAIL, password=self.PASSWORD, csrfmiddlewaretoken=csrftoken)
        headers = {
            "origin": self.MAIN_URL,
            "referer": login_url,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
        }

        response = self.client.post(login_url, data=login_data, headers=headers)

        if response.status_code != 200:
            print("Something went wrong with login")
            exit(0)
        else:
            self.get_proclomations()

    def get_proclomations(self):
        url = self.MAIN_URL+'/jobs/?keywords='+self.KEYWORD
        proclomation_page = self.client.get(url)

        if proclomation_page.status_code != 200:
                print("Something went wrong with displaying the jobs")
                exit(0)
        else:
            self.get_jobs(proclomation_page)
    
    def get_jobs(self, proclomation_page):
        soup = bs(proclomation_page.text, "html.parser")
        jobs = soup.find_all("li", {"class": "list-jobs__item"})

        self.loop_jobs(jobs)

    def loop_jobs(self, jobs):
        for job in jobs:
            job_link = job.find("a", {"class": "profile"}).get("href")
            job_page = self.client.get(self.MAIN_URL + job_link)

            print(self.MAIN_URL + job_link)
            
            if job_page.status_code != 200:
                print("Something went wrong with applying to a job")
            else:
                self.apply(job_page, job_link)
    
    def apply(self, job_page, job_link):
        job_pageSoup = bs(job_page.text, "html.parser")

        csrftoken = job_pageSoup.find("input", {"name": "csrfmiddlewaretoken"}).get("value")
        application_data = dict(message=self.MESSAGE, cv_url=self.CV_URL, csrfmiddlewaretoken=csrftoken)
        headers = {
            "origin": "https://djinni.co",
            "referer": self.MAIN_URL + job_link,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
        }
        
        response = self.client.post(self.MAIN_URL + job_link, data=application_data, headers=headers)
        print(response)

with open('config.json') as config_file:
        data = json.load(config_file)

bot = Bot(data)
bot.start()