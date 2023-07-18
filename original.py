import numpy as np
from PIL import Image
import imageio
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from sklearn.model_selection import train_test_split
import re
import string
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
import easyocr
import io
from PIL import Image
from requests.exceptions import MissingSchema
import spacy
from scipy.spatial.distance import cosine
nlp = spacy.load('en_core_web_md')
global result
result = None
global heading
heading = None

css="""
<style>
span{
    text-align: center;
    color:#2F3C7E;
}
section.egzxvld5{
    background-color: #FBEAEB;
}
div.e16nr0p34{
    color:#2F3C7E;
}
section.exg6vvm15{
    background-color: #FBEAEB;
    border: solid 3px #2F3C7E ;
}
small.euu6i2w0{
    color:#2F3C7E;
}
button.edgvbvh10{
    background-color: #2F3C7E;
    color:#FBEAEB;
    border: solid 3px #2F3C7E ;
}
input.st-cj{
    background-color: #FBEAEB;
    color:#2F3C7E;
    border: solid 3px #2F3C7E ;
}
button.edgvbvh5{
    background-color: #2F3C7E;
    color:#FBEAEB;
    border: solid 3px #2F3C7E ;
}
button>div>p{
    color:#FBEAEB;
}


</style>
"""


st.markdown(css,unsafe_allow_html=True)

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('fakenewsdetection-392610-ec79934e2745.json', scope)
client = gspread.authorize(credentials)

spreadsheet_url= 'https://docs.google.com/spreadsheets/d/1DoRSy7XixePfmV7_fwZ6pOIhWGu4I5DnjfgYBeaEoUg/edit?usp=sharing'
spreadsheet = client.open_by_url(spreadsheet_url)
worksheet = spreadsheet.get_worksheet(0)

def is_valid_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an exception for 4xx or 5xx status codes
        return True
    except requests.exceptions.RequestException:
        return False



def extract_url(sentence):
    url_pattern = r'[https?://|www\.]\S+'
    match = re.search(url_pattern, sentence)
    words = re.findall(url_pattern,sentence)
    print("words",words)
    url = words[-1]
    text = sentence[:match.start()].strip()
    return url, text

def are_sentences_similar(sentence1, sentence2, similarity_threshold=0.8):
    s1 = sentence1.lower()
    s2= sentence2.lower()
    doc1 = nlp(s1)
    doc2 = nlp(s2)
    similarity_score = 1 - cosine(doc1.vector, doc2.vector)
    return similarity_score

def scraper(Title):
    print(Title)
    url = 'https://news.google.com/search'
    params = {'q': Title, 'hl': 'en-US', 'gl': 'US', 'ceid': 'US:en'}
    response = requests.get(url, params=params)
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = soup.find_all('a', class_='DY5T1d')
    count = 0
    i = 0
    list1 = []
    list1.append(Title)
    for article in articles:
        title = article.text
        url = 'https://news.google.com' + article['href'][1:]
        list1.append(title)
        count += 1
        if count == 3:
            break
    print("using similarity")
    l= len(list1)
    print(l)
    if l>=4:
        news1 = are_sentences_similar(list1[0],list1[1])
        news2 = are_sentences_similar(list1[0],list1[2])
        news3 = are_sentences_similar(list1[0],list1[3])
    elif l>1:
        return "Fake News"
    else:
        return "Irrelavant"
    print(news1,news2,news3)
    if ((news1>0.5 and news2>0.5) and news3>0.3) or (news1>0.3 and (news2>0.5 and news3>0.5)) or ((news1>0.5 and news1>0.5) and news2>0.3):
        return "Real News"
    elif news1>0.1 and news2>0.1 and news3>0.1:
        return "Fake News"
    else:
        return "Irrelavant"
    
def text_extraction(pic):
    img = Image.open(pic)
    print(img)
    reader = easyocr.Reader(['en'])
    results = reader.readtext(img)
    a = ""
    for res in results:
        a = a+" " + res[1]
    print(a)
    return a

def image_extraction(url):
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    image_element = soup.find('meta', property='og:image')
    image_url = image_element['content'] if image_element else None
    print("using textextraction")
    a=text(image_url)
    print("used text extract")
    return a

def text(image_url):
    image_response = requests.get(image_url)
    image = Image.open(io.BytesIO(image_response.content))
    reader = easyocr.Reader(['en'])
    results = reader.readtext(image)
    a = ""
    for res in results:
        a = a+" " + res[1]
    print(a)
    if a:
        return a
    else:
        return None

# def extract_instagram_captions(post_url):
#     # response = requests.get(post_url)
#     # soup = BeautifulSoup(response.text, 'html.parser')
#     # caption_element = soup.select_one('meta[property="og:description"]')
#     # caption = caption_element['content'] if caption_element else ''
#     # a = caption.split('\"')
#     # print(a)
#     # return a[-2]
#     try:
#         # Check if the URL starts with "http://" or "https://"
#         if not url.startswith("http://") and not url.startswith("https://"):
#             # If not, add "https://" as the default schema
#             url = "https://" + url
        
#         # Check if the URL is None

#         response = requests.get(url)
#         soup = BeautifulSoup(response.text, 'html.parser')
#         caption_element = soup.select_one('meta[property="og:description"]')
#         caption = caption_element['content'] if caption_element else ''
#         a = caption.split('\"')
#         print(a)
#         return a[-2]  # Check if the response has an HTTP error status

#         # Your scraping code here...

#     except requests.exceptions.HTTPError as e:
#         print(f"HTTP error: {e}")
#     except requests.exceptions.MissingSchema as e:
#         print(f"Invalid URL: {url}")
#     except requests.exceptions.ConnectionError as e:
#         print(f"Connection error: {e}")
#     except ValueError as e:
#         print("URL is None")
#     except Exception as e:
#         print(f"An error occurred: {e}")

def extract_instagram_captions(post_url: str) -> str:
    try:
        response = requests.get(post_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        caption_element = soup.select_one('meta[property="og:description"]')
        caption = caption_element['content'] if caption_element else ''
        return caption
    except MissingSchema:
        corrected_url = 'https://' + post_url
        return extract_instagram_captions(corrected_url)
    
    # if not post_url.startswith('http://') and not post_url.startswith('https://'):
    #     corrected_url = 'https://' + post_url
    #     return extract_instagram_captions(corrected_url)
    
def extract_headline(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    headline_element = soup.find('h1')
    headline = headline_element.text.strip() if headline_element else 'Headline not found'
    return headline

def insta_scrapper(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    meta_tag = soup.find('meta', attrs={'property': 'og:description'})
    content = meta_tag.get('content')
    username = content.split('@')[-1].split()[0]
    qwerty = username
    print(qwerty)
    df = pd.read_csv("trusted_sources.csv")
    instagram_acc = df["Instagram"].tolist()
    if qwerty in instagram_acc:
        return "Real News"
    else:
        a = extract_instagram_captions(url)
        print(a)
        
        w = scraper(a)
        return w

def realnews_url(title):
    print('query',title)
    search_url = f"https://news.google.com/search?q={title}&hl=en-US&gl=US&ceid=US%3Aen"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    urlelement = soup.find_all('a', {'class': 'VDXfz'})
    print("url element:", urlelement)
    if urlelement is not None:
        link = urlelement[0].get('href')
        firsturl = f"https://news.google.com{link}"
        return firsturl
    else:
        return "Not Found"
    
st.title("FAKE NEWS DETECTOR")
st.write("""Instructions:\n1. There are 4 formats to give the input - Title only, URL only, Title and URL only, Image only.\n2. Please ensure not to give any other forms of input.\n3. Make sure the content in Image or URL or Title are in English only.""")
with st.form("my_form"):
    pic = st.file_uploader("Upload an image", type=['jpg', 'jpeg', 'png'])
    Title = st.text_input("Enter title", disabled=False)
    url = st.text_input("Enter url", disabled=False)
    submit_button = st.form_submit_button(label='SUBMIT')

if submit_button:
    print("title:",Title)
    print("pic:", pic)
    print("url", url)
    print("submitted")
    # if news_message(Title) == True and Title:
    if not url.startswith('http://') and not url.startswith('https://') and url != "":
        url = 'https://' + url
        
    if is_valid_url(url):
        print("The URL is valid and accessible.")
    else:
        print("The URL is not valid or not accessible.")

    
    if Title!="":
        if pic == None:
            if url == "":
                if 'http' in Title or 'https' in Title or 'www' in Title:
                    a,b = extract_url(Title)
                    print(a,b)
                    if "instagram.com" in a:
                        w = extract_instagram_captions(a)
                        print(w)
                        if w==None:
                            result= "Invalid URL"
                        else:
                            if are_sentences_similar(w, b):
                                result = scraper(b)
                                heading = b
                            else:
                                result = "Content in Title and the Url doesn't match"
                    else:
                        print("extracting headline")
                        headline = extract_headline(a)
                        print(headline)
                        print("extracted headline")
                        if are_sentences_similar(headline, b):
                            result = scraper(b)
                            heading = b
                        else:
                            result = "Content in Title and the Url doesn't match"
                else:
                    print("using scraper 1")
                    result = scraper(Title)
                    heading = Title
                # st.write('Result: ',result)
                print("used scraper 1")
            else:
                if is_valid_url(url):
                    print("")
                    if "instagram.com" in url:
                        w = extract_instagram_captions(url)
                        print(w)
                        if are_sentences_similar(w, Title):
                            result = scraper(Title)
                            heading = Title
                        else:
                            result = "Content in Title and the Url doesn't match"
                    else:
                        print("extracting headline")
                        headline = extract_headline(url)
                        print("extracted headline")
                        if are_sentences_similar(headline, Title):
                            result = scraper(Title)
                            heading = Title
                        else:
                            result = "Content in Title and the Url doesn't match"
                else:
                    result = "Invalid Url"
    elif url != "" and Title == "" and pic == None and is_valid_url(url):
        if "instagram.com" in url:
            if image_extraction(url)==None or are_sentences_similar(image_extraction(url),extract_instagram_captions(url))>0.8 :
                print("using ig scraper")
                result = insta_scrapper(url)
                print("used insta scrapper")
                heading = extract_instagram_captions(url)
            else:
                result = "Content in caption and image are not matched"
        else:
            print("extracting headline")
            headline = extract_headline(url)
            print("extracted headline")
            print("using scraper 7")
            result = scraper(headline)
            heading = extract_headline(url)
            print("used scraper 7")
    elif pic != None:
        heading = text_extraction(pic)
        if heading==None:
            result="No text in the image"
        else:
            result = scraper(heading)
    elif is_valid_url(url)==False:
        result="Invalid URL"
    else:
        result = "Irrelavant"
    if result == "Fake News":
        realurl = realnews_url(heading)
        print("url:", realurl)
        comment = "Real News :" + realurl
    if url and result=="Fake News" and "instagram.com" in url:
        data = [url,comment]
        print(data)
        worksheet.append_row(data)
    st.write(f"Result: {result}")
    if result == "Fake News":
        st.write(comment)
    print("____________________________")






