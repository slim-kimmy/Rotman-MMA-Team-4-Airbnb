import requests

ACCESS_KEY = "-L-dg1bu_MX3KBd-fI8iKia-TUyBTDGKdlQklReg1JA"  # replace with your Unsplash access key


def search_unsplash(query, per_page=1):
    url = "https://api.unsplash.com/search/photos"
    headers = {"Authorization": f"Client-ID {ACCESS_KEY}"}
    params = {"query": query, "per_page": per_page, "orientation": "landscape"}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    results = data.get("results", [])
    if results:
        first = results[0]
        return {
            "image_url": first["urls"]["regular"],
            "photographer": first["user"]["name"],
            "photographer_link": first["user"]["links"]["html"],
        }
    return None


# Example usage
print(search_unsplash("beach house"))
