from bs4 import BeautifulSoup
import requests
import re
import tweepy
import os

def twitter_api():
    twitter_api_key = os.environ.get("TWITTER_API_KEY")
    twitter_api_key_secret = os.environ.get("TWITTER_API_SECRET")
    twitter_access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
    twitter_access_token_secret = os.environ.get("TWITTER_ACCESS_SECRET")
    auth = tweepy.OAuthHandler(twitter_api_key, twitter_api_key_secret)
    auth.set_access_token(twitter_access_token, twitter_access_token_secret)
    twitter_api = tweepy.API(auth)
    return twitter_api

def get_celeb_name_and_image_from_famous_birthdays(url):
    # get name
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    celeb_data = {}

    celebrity_element = soup.find("a", "face face person-item")
    celebrity_name_and_age = celebrity_element.find("div", "name").text
    comma_position = celebrity_name_and_age.find(",")
    celebrity_name_with_linebreaks = celebrity_name_and_age[:comma_position]
    celebrity_name = celebrity_name_with_linebreaks.replace("\n", "")
    celeb_data["-NAME-"] = celebrity_name

    # get image url
    celebrity_image_url_unshortened = celebrity_element.attrs["style"]
    celebrity_image_url_with_parentheses = re.findall(r"(?P<url>https?://[^\s]+)", celebrity_image_url_unshortened)
    celebrity_image_url = celebrity_image_url_with_parentheses[0].replace(')','')
    celeb_data["-URL-"] = celebrity_image_url

    return celeb_data

def search_for_user_on_twitter(celeb_name):
    user = twitter_api().search_users(celeb_name, 1)
    username = "@" + user[0]._json["screen_name"]
    return username

def prepare_media_for_upload(celeb_image_url):
    # download image of celeb (from URL)
    response = requests.get(celeb_image_url, stream=True)
    with open("/Users/patrick/Git/6ix9ine_bot/images/celeb.jpg", "wb") as celeb_img:
        celeb_img.write(response.content)

    # create media ids
    filenames = ["/Users/patrick/Git/6ix9ine_bot/images/6ix9ine.jpg",
                 "/Users/patrick/Git/6ix9ine_bot/images/celeb.jpg"]
    media_ids = []
    for filename in filenames:
        try:
            res = twitter_api().media_upload(filename)
            media_ids.append(res.media_id)
        except tweepy.error.TweepError as e:
                print(e)
                continue
    return media_ids

def format_for_tweet(celeb_name, screen_name):
    tweet_str = f"BREAKING NEWS! 6ix9ine testifies that {celeb_name} ({screen_name}) " \
                "has been confirmed as a member of Nine Trey Bloods."
    return tweet_str

celeb_data_today = get_celeb_name_and_image_from_famous_birthdays("https://www.famousbirthdays.com/")
username = search_for_user_on_twitter(celeb_data_today["-NAME-"])
final_tweet_string = format_for_tweet(celeb_data_today["-NAME-"],username)
twitter_api().update_status(status = final_tweet_string, media_ids=prepare_media_for_upload(celeb_data_today['-URL-']))

