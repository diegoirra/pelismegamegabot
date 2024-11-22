import requests, time, datetime
from bs4 import BeautifulSoup
import tweepy
from creds import api_key, api_secret_key, access_token, access_token_secret, bearer 

def init_twitter(bearer, api_key, api_secret_key, access_token, access_token_secret):
    client = tweepy.Client(bearer, api_key, api_secret_key, access_token, access_token_secret, return_type=dict)
    print(f"Logged in as: {client.get_me()['data']}")
    return client

def init_api():
    auth = tweepy.OAuthHandler(consumer_key=api_key, consumer_secret=api_secret_key)
    auth.set_access_token(key=access_token, secret=access_token_secret)
    return tweepy.API(auth)    

def get_movie_poster(url):
    response = requests.get(url)    
    soup = BeautifulSoup(response.text, "html.parser")
    
    print("Getting HD movie poster from ", url)
    poster = soup.find("img", id="poster")
    if not poster:
        print("WARNING: Poster not found.")
        return ""

    print(f"Poster: {poster}")
    print()
    poster_hd = poster['data-lazy-src']
    return poster_hd
    

def upload_poster(poster):
    api = init_api()    
    
    #def download_poster ?
    response = requests.get(poster)
    with open("poster.png", "wb") as file:
        file.write(response.content)    
    
    media = api.media_upload("poster.png")    
    print("Uploaded poster as:", media)
    return media.media_id

def tweet_movie(client,pelicula):        
    text= f"""New movie uploaded!\n{pelicula['titulo']}\n{pelicula['link']}"""

    hd_poster = get_movie_poster(pelicula['link'])
    if hd_poster:
        poster_id = upload_poster(hd_poster)
        print("Tweeted succesfully: ", client.create_tweet(text=text, media_ids=[poster_id]))
    else:
        print("Tweeted succesfully: ", client.create_tweet(text=text))
    print(text)    
    

def delete_all_tweets(client):
    all_tweets = []
    me_id = client.get_me()['data']['id']
    for tweet in tweepy.Cursor(client.get_users_tweets(me_id)).items():
        all_tweets.append(tweet)
    for tweet in all_tweets:
        client.delete_tweet(tweet.id)
    return

def get_peliculas(url):
    response = requests.get(url)    
    soup = BeautifulSoup(response.text, "html.parser")
    
    contenido = soup.find("div", id="contenido")
    if not contenido:
        print("WARNING: Contenido not found.")
        print(f"Request response: {response}")
        print(f"Soup HTML parser: soup")
        print(f"Contenido: {contenido}")
        print()
        return {}

    peliculas = contenido.find_all('div', class_='pelicula')    
    peliculas_parsed = [{ 
                "id": pelicula_div["id"], 
                "titulo": pelicula_div.find("h2").a["title"],                
                "link": pelicula_div.find("div", class_="poster marco-sinopsis").a["href"]  
            } for pelicula_div in peliculas]
    
    return peliculas_parsed

def main():
    url = "https://www.pelismkvhd.com/"
    
    print("Welcome to PelisMega Bot!")
    print("We tweet every time there's a new movie")
    client = init_twitter(bearer, api_key, api_secret_key, access_token, access_token_secret)      
    client.create_tweet(text=f"""I've restarted at {datetime.datetime.now().time()}!
I dont persist so maybe check if you missed anything from last update
                        {url}""",
                        )
        
    print()
    last_movie = get_peliculas(url)[0]
    previous_last_movie_id = last_movie['id']
    
    # delete_all_tweets(client)
    # tweet_movie(client, last_movie)

    print(f"Last movie is {last_movie}")
    print()
    print("Not tweeting this one")
    print(f"Check yourself at {url}")
    print()
    
    while True:
        now = datetime.datetime.now().time()
        start_time = datetime.time(6, 0, 0) 
        end_time = datetime.time(21, 0, 0)
        
        if start_time <= now <= end_time:
            print(f"Checking movies at {url}")
            
            try:
                peliculas = get_peliculas(url)
            except requests.exceptions.ConnectionError:
                print(f"{now}: ERROR: Connection Error due to no Wifi")
                print(f"{now}: Sleeping extra to reconnect...")
                print()
                time.sleep(3000)
                continue
            
            if peliculas:
                last_movie=next_movie = peliculas.pop(0)        
            while next_movie['id'] != previous_last_movie_id:
                tweet_movie(client, next_movie)
                next_movie = peliculas.pop(0)           
            
            previous_last_movie_id = last_movie['id'] 
        else:
            print(f"{now}: Not in active time")
            time.sleep(1800)

        print()
        print(f"{now}: Sleeping...")
        time.sleep(300)
        print()
    
    
    



if __name__ == '__main__':
    main()

