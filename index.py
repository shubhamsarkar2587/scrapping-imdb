import requests, json, pprint, os, time, random
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# base url init and setup
base_url = "https://www.imdb.com/chart/top/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}


def fetchUrl(url):
    # requests and parsing using beautiful soup
    url = requests.get(url, headers=headers)
    parsed_data = BeautifulSoup(url.text, "html.parser")
    return parsed_data


def getSingleMovieDetails(movie_url):
    options = Options()
    options.add_argument("window-size=700,600")
    from fake_useragent import UserAgent

    ua = UserAgent()
    user_agent = ua.random
    print(user_agent)
    options.add_argument(f"user-agent={user_agent}")
    driver = webdriver.Chrome(options=options)

    driver.get(movie_url)

    video_url = None

    try:
        # Wait for the video element to be present
        video_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[1]/div[2]/div[2]/div[2]/div[1]/div/div/div/div[2]/div[4]",
                )
            )
        )

        # Once the video element is found, find the video source
        video_element = WebDriverWait(video_div, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, './/video[@class="jw-video jw-reset"]')
            )
        )
        video_url = video_element.get_attribute("src")
        time.sleep(3)
    except Exception as e:
        print("Error:", e)
    finally:
        driver.quit()

    print(video_url)
    return video_url


def getTop250MoviesList():
    req_parsed_data = fetchUrl(base_url)
    req_list_ul = req_parsed_data.find("ul", "compact-list-view")
    all_movie_cards = req_list_ul.find_all("li", "ipc-metadata-list-summary-item")

    count = 1
    movie_list = []
    # looping through movie list cards
    for movie_card in all_movie_cards:
        print(f"\n============== movie_scrapped={count} ================")

        single_movie_detail = {
            "movie_position": count,
            "movie_name": "",
            "movie_release_year": "",
            "movie_duration": "",
            "movie_age_certificate": "",
            "movie_imdb_rating": "",
            "movie_imdb_rating_providers": "",
            "movie_img_url": "",
            "movie_imdb_link": "",
            "movie_video_url": "",
        }

        movie_img_ele = movie_card.find("img")
        if movie_img_ele != None:
            single_movie_detail["movie_img_url"] = movie_img_ele.get("src")

        # getting movie details
        movie_details_div = movie_card.find("div", "cli-children")

        movie_title_ele = movie_details_div.find("h3", "ipc-title__text")
        if movie_title_ele != None:
            movie_title_split = movie_title_ele.get_text().split(" ", 1)
            movie_txt = ""
            if len(movie_title_split) > 1:
                movie_txt = movie_title_split[1]
            else:
                movie_txt = movie_title_ele.get_text()
            single_movie_detail["movie_name"] = movie_txt

        # movie meta data
        movie_meta_data = movie_details_div.find_all("span", "cli-title-metadata-item")
        if movie_meta_data[0] != None:
            single_movie_detail["movie_release_year"] = movie_meta_data[0].get_text()
        if movie_meta_data[1] != None:
            single_movie_detail["movie_duration"] = movie_meta_data[1].get_text()
        if len(movie_meta_data) > 2 and movie_meta_data[2] != None:
            single_movie_detail["movie_age_certificate"] = movie_meta_data[2].get_text()

        # movie imdb rating
        imdb_rating_ele = movie_details_div.find("span", "ipc-rating-star")
        if imdb_rating_ele != None:
            movie_rating_split = imdb_rating_ele.get_text().replace("\xa0", " ").split()
            if movie_rating_split[0] != None:
                single_movie_detail["movie_imdb_rating"] = movie_rating_split[0]
            if movie_rating_split[1] != None:
                single_movie_detail["movie_imdb_rating_providers"] = (
                    movie_rating_split[1].replace("(", "").replace(")", "")
                )
            else:
                single_movie_detail["movie_imdb_rating"] = imdb_rating_ele.get_text()

        # movie url
        movie_poster_div = movie_card.find("div", "ipc-poster")
        imdb_url_ele = movie_poster_div.find("a")
        if imdb_url_ele != None:
            imdb_movie_page_url = "https://www.imdb.com/" + imdb_url_ele.get("href")
            single_movie_detail["movie_imdb_link"] = imdb_movie_page_url
            imdb_movie_url = getSingleMovieDetails(imdb_movie_page_url)
            single_movie_detail["movie_video_url"] = imdb_movie_url

        movie_list.append(single_movie_detail)
        count += 1

    return movie_list


movie_data = {"title": "IMDb Top 250 Movies", "data": []}
movie_data["data"] = getTop250MoviesList()

file_name = "imdb_movies_data/imdb_top_250_movies.json"
with open(file_name, "w") as file:
    json.dump(movie_data, file, indent=2)

# pprint.pprint(movie_data)
