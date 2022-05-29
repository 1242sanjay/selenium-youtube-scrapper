import smtplib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import os
import json

YOUTUBE_TRENDING_URL = 'https://www.youtube.com/feed/trending'

def get_driver():
  chrome_options = Options()
  chrome_options.add_argument('--no-sandbox')
  chrome_options.add_argument('--headless')
  chrome_options.add_argument('--disable-dev-shm-usage')
  driver = webdriver.Chrome(options = chrome_options)
  return driver

def get_videos(driver):
  VIDEO_DIV_TAG = 'ytd-video-renderer'
  driver.get(YOUTUBE_TRENDING_URL)
  videos = driver.find_elements(By.TAG_NAME, VIDEO_DIV_TAG)
  return videos

def parse_video(video):
  title_tag = video.find_element(By.ID, 'video-title')
  title = title_tag.text
  url = title_tag.get_attribute('href')
  
  thumbnail_url = video.find_element(By.TAG_NAME, 'img').get_attribute('src')
  
  channel_div = video.find_element(By.CLASS_NAME, 'style-scope ytd-channel-name')
  channel_name = channel_div.text
  channel_url_tag = channel_div.find_element(By.TAG_NAME, 'a')
  channel_url = channel_url_tag.get_attribute('href')
  
  view_div = video.find_element(By.ID, 'metadata-line')
  span_tags = view_div.find_elements(By.TAG_NAME, 'span')
  views = span_tags[0].text
  uploaded = span_tags[1].text

  description = video.find_element(By.ID, 'description-text').text

  return{
    'title' : title,
    'url' : url,
    'thumbnail_url' : thumbnail_url,
    'channel' : channel_name,
    'channel_url' : channel_url,
    'views' : views,
    'uploaded' : uploaded,
    'description' : description
  }


def sendEmail(body):
  try:
    server_ssl = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server_ssl.ehlo()
    
    SENDER_EMAIL = 'dsaiandmldl@gmail.com'
    SENDER_PASSWORD = os.environ['GMAIL_PASSWORD']
    RECIEVER_EMAIL = '1242sanjay@gmail.com'
    subject = 'Youtube trending videos'
    
    email_text = f"""\
    From: {SENDER_EMAIL}
    To: {RECIEVER_EMAIL}
    Subject: {subject}
    {body}
    """
    
    server_ssl.login(SENDER_EMAIL, SENDER_PASSWORD)
    server_ssl.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, email_text)
    server_ssl.close()
    print('Email sent successfully...')
  except:
    print('Something went wrong...')



if __name__=="__main__":
  print("Creating driver")
  driver = get_driver()


  print('Fetching trending videos')
  videos = get_videos(driver)
  print(f'found {len(videos)} videos')

  # title, url, thumbnail_url, channel, views, uploaded, description
  print('Parsing top 10 videos')
  videos_data = [parse_video(video) for video in videos[:10]]
  print(videos_data)

  print('Save the data into a CSV file')
  videos_df = pd.DataFrame(videos_data)
  videos_df.to_csv('trending.csv', index = None)

  print('Send an email with results')
  body = json.dumps(videos_data, indent = 2)
  sendEmail(body)
  print('Finished...')