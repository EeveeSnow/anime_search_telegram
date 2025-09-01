import pandas as pd
import requests


# from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# base_url = "https://myanimelist.net/topanime.php"

query = '''
query($page:Int = 1 $id:Int $type:MediaType $isAdult:Boolean = false $search:String $format:[MediaFormat]$status:MediaStatus $countryOfOrigin:CountryCode $source:MediaSource $season:MediaSeason $seasonYear:Int $year:String $onList:Boolean $yearLesser:FuzzyDateInt $yearGreater:FuzzyDateInt $episodeLesser:Int $episodeGreater:Int $durationLesser:Int $durationGreater:Int $chapterLesser:Int $chapterGreater:Int $volumeLesser:Int $volumeGreater:Int $licensedBy:[Int]$isLicensed:Boolean $genres:[String]$excludedGenres:[String]$tags:[String]$excludedTags:[String]$minimumTagRank:Int $sort:[MediaSort]=[POPULARITY_DESC,SCORE_DESC]){Page(page:$page,perPage:100){pageInfo{total perPage currentPage lastPage hasNextPage}media(id:$id type:$type season:$season format_in:$format status:$status countryOfOrigin:$countryOfOrigin source:$source search:$search onList:$onList seasonYear:$seasonYear startDate_like:$year startDate_lesser:$yearLesser startDate_greater:$yearGreater episodes_lesser:$episodeLesser episodes_greater:$episodeGreater duration_lesser:$durationLesser duration_greater:$durationGreater chapters_lesser:$chapterLesser chapters_greater:$chapterGreater volumes_lesser:$volumeLesser volumes_greater:$volumeGreater licensedById_in:$licensedBy isLicensed:$isLicensed genre_in:$genres genre_not_in:$excludedGenres tag_in:$tags tag_not_in:$excludedTags minimumTagRank:$minimumTagRank sort:$sort isAdult:$isAdult){id title{userPreferred} description genres averageScore popularity}}}
'''
url = 'https://graphql.anilist.co'
anime_list = []
for i in range(25): # scrape 25 pages, each page has 100 anime
    variables = {
    "page":i,"type":"ANIME","sort":"SCORE_DESC"
    }

    response = requests.post(url, json={'query': query, 'variables': variables}).json()['data']['Page']['media']
    for entry in response: # for each entry
        id = entry['id']# get the id
        title = entry['title']['userPreferred']# get the title
        genres = " ".join(entry['genres']) # get the genres
        description = str(entry['description'])
        rating = int(entry['averageScore']) # get the rating
        # popularity = int(entry['popularity']) # get the popularity
        anime_list.append([title, id, description, genres, rating]) # append the data to the list
# Create a dataframe from the list and rename the columns
anime_df = pd.DataFrame(anime_list, columns=["title", "id", "description", "genres", "rating"])

# Create a TF-IDF vectorizer object and fit it on the genres column
tfidf = TfidfVectorizer(stop_words="english")
tfidf_matrix = tfidf.fit_transform(anime_df["genres"])
tfidf = TfidfVectorizer(stop_words="english")
tfidf_matrix_2 = tfidf.fit_transform(anime_df["description"])

# Compute the cosine similarity matrix from the TF-IDF matrix
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
cosine_sim_2 = linear_kernel(tfidf_matrix_2, tfidf_matrix_2)

# Define a function that takes an anime title as input and returns a list of 10 most similar anime based on genre similarity
def get_recommendations(title):
    idx = anime_df[anime_df["title"] == title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    # sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores_2 = list(enumerate(cosine_sim_2[idx]))
    sim_scores_avg = map(lambda x, y: (x[0], y[1] * x[1]), sim_scores, sim_scores_2)
    sim_scores_avg = sorted(sim_scores_avg, key=lambda x: x[1], reverse=True)
    sim_indices = [i[0] for i in sim_scores_avg[1:11]]
    return (anime_df["title"].iloc[sim_indices].values, anime_df["id"].iloc[sim_indices].values)

# from fuzzywuzzy import process
# def get_recommendations_2(title):
#     title = process.extractOne(title, anime_df['title'])[0]
#     return get_recomendations(title)


# liked_animes = ["Boku no Kokoro no Yabai Yatsu", "Boku no Kokoro no Yabai Yatsu 2nd Season"]

# for anime in liked_animes:
#     print(f"If you like {anime}, you might also like:")
#     data = get_recommendations(anime)
#     for i in range(10):
#         print(f"{i+1}. '{data[0][i]}' link to anilist.co: https://anilist.co/anime/{data[1][i]}")
#     print()