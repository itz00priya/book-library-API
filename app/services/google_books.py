import httpx

async def fetch_book_details(isbn: str):
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()
        
        if "items" in data:
            volume_info = data["items"][0]["volumeInfo"]
            return {
                "title": volume_info.get("title"),
                "author": ", ".join(volume_info.get("authors", ["Unknown"])),
                "description": volume_info.get("description", ""),
                "isbn": isbn
            }
        return None