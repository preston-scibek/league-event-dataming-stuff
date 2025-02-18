import re, requests, os, json
import jsbeautifier

#https://akamai.embed.rgpub.io/season-start-embed-2024/_nuxt/app.js?3a5a1e98e3f0aa4cbbc6

url = "https://assetcdn.rgpub.io/public/live/bundle-offload/cdd2cc2b-cac0-463a-bbbb-1a406e0909cc/65982085fd30071d2190d689/"

assets = []
asset_path = url
r = requests.get(asset_path + "app.328608.js")

assert(r.status_code == 200)

js = jsbeautifier.beautify(f"\n{r.text}")
with open('dist.js', 'w') as jfile:
    jfile.writelines(js)

for line in js.split("\n"):
    if "png" in line or "webm" in line or "jpg" in line:
        regex_str = r'^.*"((_\/lib)?.*(?:png|jpg|webm).*)"[^:]?.*$'
        m = re.search(regex_str, line)
        if m and m.group(1):
            print(f"{asset_path}{m.group(1)}")
            assets.append(f"{asset_path}{m.group(1)}")

fails = []
success = []
import subprocess
import concurrent.futures

def request_get(url):
    print(f"downloading asset for {url}")
    path = url.split(asset_path)[1]
    dir_path = "/".join(path.split("/")[0:-1])
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        try:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            with open(path, 'wb') as f:
                for chunk in r:
                    f.write(chunk)
        except:
            print(f"download failed for {url}")
            return False
        return True
    else:
        print(f"download failed for {url}")
        return False

with concurrent.futures.ProcessPoolExecutor(max_workers=32) as executor:
    for url, status in zip(assets, executor.map(request_get, assets)):
        if status:
            success.append(url)
        else:
            fails.append(url)
                
    

with open("failed_downloads.json", "w+") as jfile:
    json.dump(fails, jfile, indent=4)
with open("success_downloads.json", "w+") as jfile:
    json.dump(success, jfile, indent=4)

total_assets = len(assets)
print(f"Total Assets: {total_assets}\nFails: {len(fails)}\nSuccesses: {len(success)}")