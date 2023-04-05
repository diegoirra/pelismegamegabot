import requests, time, datetime
from bs4 import BeautifulSoup
import tweepy
from creds import api_key, api_secret_key, access_token, access_token_secret, bearer 

def init_twitter(bearer, api_key, api_secret_key, access_token, access_token_secret):
    client = tweepy.Client(bearer, api_key, api_secret_key, access_token, access_token_secret, return_type=dict)
    print(f"Logged in as: {client.get_me()}")
    return client

def tweet_movie(client,pelicula):        
    # text= f"{pelicula['titulo']} {pelicula['link']} {pelicula['poster']}"    
    text= f"New movie uploaded!\n{pelicula['titulo']}\n{pelicula['link']}"
    print(text)
    print(client.create_tweet(text=text))

def delete_all_tweets(client):
    all_tweets = []
    me_id = client.get_me()['id']
    for tweet in tweepy.Cursor(client.get_users_tweets(me_id)).items():
        all_tweets.append(tweet)
    for tweet in all_tweets:
        client.delete_tweet(tweet.id)
    return

def get_peliculas(url):
    response = requests.get(url)    
    soup = BeautifulSoup(response.text, "html.parser")
    
    contenido = soup.find("div", id="contenido")
    peliculas = contenido.find_all('div', class_='pelicula')    
    peliculas_parsed = [{ 
                "id": pelicula_div["id"], 
                "titulo": pelicula_div.find("h2").a["title"],
                "poster": pelicula_div.find("div", class_="poster marco-sinopsis").a.img["data-lazy-src"],
                "link": pelicula_div.find("div", class_="poster marco-sinopsis").a["href"]  
            } for pelicula_div in peliculas]
    
    return peliculas_parsed

def main():
    url = "https://www.pelismkvhd.com/"
    
    print("Welcome to PelisMega Bot!")
    print("We tweet every time there's a new movie")
    client = init_twitter(bearer, api_key, api_secret_key, access_token, access_token_secret)
    
    client.create_tweet(text=f"""I've restarted!
                        I dont persist so maybe check if you missed anything in the meantime
                        {url}
                        """
                        )
        
    print()
    last_movie = get_peliculas(url)[0]
    previous_last_movie_id = last_movie['id']
    # previous_last_movie_id = "post-64844"
    
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
            except ConnectionError:
                print(f"{now}: ERROR: Connection Error due to no Wifi")
                print(f"{now}: Sleeping extra to reconnect...")
                time.sleep(3000)
                continue
            
            last_movie=next_movie = peliculas.pop(0)        
            while next_movie['id'] != previous_last_movie_id:
                tweet_movie(client, next_movie)
                next_movie = peliculas.pop(0)           
            
            previous_last_movie_id = last_movie['id'] 
        else:
            print(f"{now}: Not in active time")
            time.sleep(3600)

        print()
        print(f"{now}: Sleeping...")
        time.sleep(300)
        print()
    
    
    



if __name__ == '__main__':
    main()

