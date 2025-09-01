import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

Base = declarative_base()

class Anime(Base):
    __tablename__ = 'anime'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(Text)
    genres = Column(String)
    rating = Column(Integer)

engine = create_engine('sqlite:///anime.db')
Session = sessionmaker(bind=engine)
session = Session()

anime_df = pd.read_sql_table('anime', engine)

tfidf = TfidfVectorizer(stop_words="english")
tfidf_matrix = tfidf.fit_transform(anime_df["genres"])
tfidf = TfidfVectorizer(stop_words="english")
tfidf_matrix_2 = tfidf.fit_transform(anime_df["description"])


cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
cosine_sim_2 = linear_kernel(tfidf_matrix_2, tfidf_matrix_2)

def find_similar_title(title, threshold=70):
    titles = anime_df['title'].tolist()
    matches = process.extract(title, titles, scorer=fuzz.token_sort_ratio)
    best_matches = [match for match in matches if match[1] >= threshold]
    if not best_matches:
        return None, None
    best_match_title = best_matches[0][0]
    idx = anime_df[anime_df['title'] == best_match_title].index[0]
    return idx, best_match_title


def get_anime_by_id(idx):
    try:
        anime = anime_df.loc[idx]
        return anime
    except  KeyError or IndexingError:
        return None
    


def get_recommendations(idx):
    # idx, matched_title = find_similar_title(title)
    sim_scores = list(enumerate(cosine_sim[idx]))
    # sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores_2 = enumerate(cosine_sim_2[idx])
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