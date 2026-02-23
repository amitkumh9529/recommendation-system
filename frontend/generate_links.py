# add to generate_links.py or run separately
import urllib.request, zipfile, os, shutil

print("Downloading MovieLens 1M for movie titles...")
urllib.request.urlretrieve(
    "https://files.grouplens.org/datasets/movielens/ml-1m.zip",
    "ml-1m.zip"
)

with zipfile.ZipFile("ml-1m.zip") as z:
    with z.open("ml-1m/movies.dat") as f:
        data = f.read()

with open("frontend/public/movies.dat", "wb") as f:
    f.write(data)

print("✅ movies.dat saved to frontend/public/movies.dat")
os.remove("ml-1m.zip")