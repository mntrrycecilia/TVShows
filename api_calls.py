import requests

def get_shows():
    url = "https://api.tvmaze.com/shows"
    response = requests.get(url)

    if response.status_code == 200:
        shows = response.json()
        # Include image URLs in the show data
        for show in shows:
            show['image_url'] = show['image']['medium'] if show['image'] else None
        return shows
    else:
        return None

def search_tv_shows(query):
    url = f"https://api.tvmaze.com/search/shows?q={query}"
    response = requests.get(url)
    if response.status_code == 200:
        search_results = response.json()
        # Extract show data and include image URLs
        shows = []
        for result in search_results:
            show = result['show']
            shows.append({
                'title': show['name'],
                'genres': show['genres'],
                'language': show['language'],
                'summary': show['summary'],
                'image_url': show['image']['medium'] if show['image'] else None
            })
        return shows
    return None

