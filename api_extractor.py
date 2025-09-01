import requests
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sqlite3


Base = declarative_base()

class Anime(Base):
    __tablename__ = 'anime'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(Text)
    genres = Column(String)
    rating = Column(Integer)


query = '''


query($page:Int = 1 $id:Int $type:MediaType $isAdult:Boolean = false $search:String $format:[MediaFormat]$status:MediaStatus $countryOfOrigin:CountryCode $source:MediaSource $season:MediaSeason $seasonYear:Int $year:String $onList:Boolean $yearLesser:FuzzyDateInt $yearGreater:FuzzyDateInt $episodeLesser:Int $episodeGreater:Int $durationLesser:Int $durationGreater:Int $chapterLesser:Int $chapterGreater:Int $volumeLesser:Int $volumeGreater:Int $licensedBy:[Int]$isLicensed:Boolean $genres:[String]$excludedGenres:[String]$tags:[String]$excludedTags:[String]$minimumTagRank:Int $sort:[MediaSort]=[POPULARITY_DESC,SCORE_DESC]){Page(page:$page,perPage:100){pageInfo{total perPage currentPage lastPage hasNextPage}media(id:$id type:$type season:$season format_in:$format status:$status countryOfOrigin:$countryOfOrigin source:$source search:$search onList:$onList seasonYear:$seasonYear startDate_like:$year startDate_lesser:$yearLesser startDate_greater:$yearGreater episodes_lesser:$episodeLesser episodes_greater:$episodeGreater duration_lesser:$durationLesser duration_greater:$durationGreater chapters_lesser:$chapterLesser chapters_greater:$chapterGreater volumes_lesser:$volumeLesser volumes_greater:$volumeGreater licensedById_in:$licensedBy isLicensed:$isLicensed genre_in:$genres genre_not_in:$excludedGenres tag_in:$tags tag_not_in:$excludedTags minimumTagRank:$minimumTagRank sort:$sort isAdult:$isAdult){id title{userPreferred} description genres averageScore popularity}}}
'''
url = 'https://graphql.anilist.co'


engine = create_engine('sqlite:///anime.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
ids = set()


anime_list = []
for i in range(25):  # 25
    variables = {"page": i, "type": "ANIME", "sort": "SCORE_DESC"}
    response = requests.post(url, json={'query': query, 'variables': variables}).json()['data']['Page']['media']
    
    for entry in response:
        exists = session.query(Anime).filter_by(id=entry['id']).first()
        
        if not exists and entry['id'] not in ids:
            
            anime = Anime(
                id=entry['id'],
                title=entry['title']['userPreferred'],
                description=str(entry['description']),
                genres=" ".join(entry['genres']),
                rating=int(entry['averageScore']) if entry['averageScore'] else None
            )
            ids.add(entry['id'])
            anime_list.append(anime)


session.bulk_save_objects(anime_list)
session.commit()