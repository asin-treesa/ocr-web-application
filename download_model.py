import urllib.request

url = "https://raw.githubusercontent.com/oyyd/frozen_east_text_detection.pb/master/frozen_east_text_detection.pb"

print("Downloading model... This may take a few minutes...")

urllib.request.urlretrieve(url, "frozen_east_text_detection.pb")

print("Download completed!")
