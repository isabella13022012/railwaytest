# imports
from playwright.async_api import async_playwright
from playwright.async_api import expect
import asyncio
import pickle
import pandas as pd
import random
import requests
import time
import gc
import json


# secrets
import os
API_KEY1 = os.environ["API_KEY1"]
API_KEY2 = os.environ["API_KEY2"]
rRhost = os.environ['rRhost']
rRpass = os.environ['rRpass']
rhost = os.environ['rhost']
rpass = os.environ['rpass']

# before anything, two connections to redis are established. these are reused in the script
import redis

rR = redis.Redis(
    host=rRhost, # to the race conditions db
    port=10276, # TCP port
    password=rRpass,
    decode_responses=True
)

r = redis.Redis(
    host=rhost, # to the actual db
    port=15572, # TCP port
    password=rpass,
    decode_responses=True
)



# set a list of european servers (these are set up on the vps)
EuropeanServers = [
    "al-tia-wg-001","al-tia-wg-003","al-tia-wg-004","at-vie-wg-001","at-vie-wg-002","at-vie-wg-003","at-vie-wg-101","at-vie-wg-102",
    "be-bru-wg-101","be-bru-wg-102","be-bru-wg-103","bg-sof-wg-001","bg-sof-wg-002","ch-zrh-wg-001","ch-zrh-wg-002","ch-zrh-wg-003",
    "ch-zrh-wg-005","ch-zrh-wg-006","ch-zrh-wg-201","ch-zrh-wg-202","ch-zrh-wg-401","ch-zrh-wg-402","ch-zrh-wg-404","ch-zrh-wg-502",
    "cy-nic-wg-001","cy-nic-wg-002","cz-prg-wg-101","cz-prg-wg-102","cz-prg-wg-201","cz-prg-wg-202","de-ber-wg-001","de-ber-wg-002",
    "de-ber-wg-003","de-ber-wg-004","de-ber-wg-101","de-ber-wg-102","de-ber-wg-103","de-dus-wg-001","de-dus-wg-002","de-dus-wg-003",
    "de-fra-wg-001","de-fra-wg-002","de-fra-wg-003","de-fra-wg-004","de-fra-wg-005","de-fra-wg-101","de-fra-wg-102","de-fra-wg-103",
    "de-fra-wg-104","de-fra-wg-303","de-fra-wg-401","de-fra-wg-402","de-fra-wg-403","dk-cph-wg-001","dk-cph-wg-102","dk-cph-wg-401",
    "dk-cph-wg-402","ee-tll-wg-001","ee-tll-wg-002","ee-tll-wg-003","es-bcn-wg-001","es-bcn-wg-002","es-bcn-wg-101","es-bcn-wg-102",
    "es-mad-wg-101","es-mad-wg-102","es-mad-wg-204","es-mad-wg-205","es-vlc-wg-001","es-vlc-wg-002","fi-hel-wg-001","fi-hel-wg-002",
    "fi-hel-wg-003","fi-hel-wg-101","fi-hel-wg-102","fi-hel-wg-103","fi-hel-wg-104","fi-hel-wg-201","fi-hel-wg-202","fi-hel-wg-203",
    "fr-bod-wg-001","fr-bod-wg-002","fr-mrs-wg-001","fr-mrs-wg-002","fr-par-wg-001","fr-par-wg-002","fr-par-wg-003","fr-par-wg-004",
    "fr-par-wg-006","fr-par-wg-007","fr-par-wg-101","fr-par-wg-102","fr-par-wg-103","fr-par-wg-301","fr-par-wg-302","gb-glw-wg-001",
    "gb-glw-wg-002","gb-lon-wg-001","gb-lon-wg-002","gb-lon-wg-003","gb-lon-wg-004","gb-lon-wg-005","gb-lon-wg-006","gb-lon-wg-007",
    "gb-lon-wg-008","gb-lon-wg-201","gb-lon-wg-202","gb-lon-wg-203","gb-lon-wg-204","gb-lon-wg-305","gb-lon-wg-306","gb-lon-wg-308",
    "gb-mnc-wg-001","gb-mnc-wg-002","gb-mnc-wg-003","gb-mnc-wg-004","gb-mnc-wg-201","gb-mnc-wg-202","gr-ath-wg-101","gr-ath-wg-102",
    "hr-zag-wg-001","hr-zag-wg-002","hu-bud-wg-101","hu-bud-wg-102","hu-bud-wg-201","hu-bud-wg-202","ie-dub-wg-101","ie-dub-wg-102",
    "ie-dub-wg-103","il-tlv-wg-101","il-tlv-wg-102","il-tlv-wg-103","it-mil-wg-001","it-mil-wg-002","it-mil-wg-003","it-mil-wg-201",
    "it-mil-wg-202","it-pmo-wg-001","it-pmo-wg-002","nl-ams-wg-001","nl-ams-wg-002","nl-ams-wg-003","nl-ams-wg-004","nl-ams-wg-005",
    "nl-ams-wg-006","nl-ams-wg-007","nl-ams-wg-008","nl-ams-wg-101","nl-ams-wg-102","nl-ams-wg-103","nl-ams-wg-201","nl-ams-wg-202",
    "nl-ams-wg-203","nl-ams-wg-301","nl-ams-wg-302","nl-ams-wg-303","no-osl-wg-001","no-osl-wg-002","no-osl-wg-003","no-osl-wg-101",
    "no-osl-wg-102","no-osl-wg-103","no-svg-wg-001","no-svg-wg-002","no-svg-wg-003","no-svg-wg-004","pl-waw-wg-101","pl-waw-wg-102",
    "pl-waw-wg-103","pl-waw-wg-201","pl-waw-wg-202","pt-lis-wg-201","pt-lis-wg-202","pt-lis-wg-301","pt-lis-wg-302","ro-buh-wg-001",
    "ro-buh-wg-002","rs-beg-wg-101","rs-beg-wg-102","se-got-wg-001","se-got-wg-002","se-got-wg-003","se-got-wg-004","se-got-wg-005",
    "se-got-wg-006","se-got-wg-007","se-got-wg-008","se-got-wg-101","se-mma-wg-001","se-mma-wg-002","se-mma-wg-003","se-mma-wg-004",
    "se-mma-wg-005","se-mma-wg-011","se-mma-wg-012","se-mma-wg-102","se-mma-wg-103","se-mma-wg-111","se-mma-wg-112","se-sto-wg-001",
    "se-sto-wg-002","se-sto-wg-003","se-sto-wg-007","se-sto-wg-008","se-sto-wg-009","se-sto-wg-010","se-sto-wg-011","se-sto-wg-012",
    "se-sto-wg-013","se-sto-wg-014","se-sto-wg-201","se-sto-wg-202","se-sto-wg-203","se-sto-wg-204","se-sto-wg-205","se-sto-wg-206",
    "se-sto-wg-207","se-sto-wg-208","se-sto-wg-209","si-lju-wg-001","si-lju-wg-002","sk-bts-wg-001","sk-bts-wg-002","tr-ist-wg-001",
    "tr-ist-wg-002","ua-iev-wg-001","ua-iev-wg-002"
]
basket = [] # this is where we put the server in use.


"""
This initial section, before even the functions, it to assign a unique value in the rR database where this script can read and write its own client IP.
This is done to make this app foolproof across different platforms, if the IP of each instance is dynamic or changes for whatever reason, this should
globally allow it to put its most current IP into the routing rules that permit wireguard to work with the VPS.
"""
for key in rR.scan_iter(): # scan DB for taken value that says 'false' (it's available as a PK)
    row = rR.hgetall(key)
    try:
        if row['taken'] == 'false':
            rR.hset(key, mapping={"taken":"true"})
            break
    except:
        continue

"""
This initialises the row with the client IP. With any luck, few write operations will be needed on this.
"""
IP = requests.get('https://api.ipify.org').text
rR.hset(key, mapping={"IP":IP})
primaryKey = key

### main function
async def PROCESS(p, id, url):
    global basket # set globals, for security
    global EuropeanServers
    global r
    global rR
    global primaryKey
    counter = 0 # this is just a simple counter that counts how many times a function passes. Once three passes have been completed, it registers all the pseudoPKs that have been allocated successfully and stops counting.
    ipKeys = [] # define this for use later

    
    def changeServer(EuropeanServers, basket): # paranoia about global variables.
        """
        This section is just a simple function that calls the api to switch server. It contains a small buffer at the end to account for race conditions.
        It assumes that ipKeys is not empty, but won't break without it.
        """
        EuropeanServers.remove(name)
        if len(basket) != 0: # row 1
            EuropeanServers.append(basket.pop())
        basket.append(name)
        time.sleep(5) # this is to allow any processes to finish... it might be a tad gratuitous but we'll see

        postUpRules = []
        preDownRules = []
        for key in ipKeys: # writes a list of ips that need to be added to the routing rules
            row = rR.hgetall(key)
            ip = row['IP']
            postUpRules.append(f'PostUp = ip route add {ip}/32 via 172.31.1.1 dev eth0')
            preDownRules.append(f'PreDown = ip route del {ip}/32 via 172.31.1.1 dev eth0') # this could be more efficient (checking file already there or smt)

        rules = [{'postup':postup, 'predown':predown} for postup, predown in list(zip(postUpRules, preDownRules))] # amend config
        R = requests.post(
            'http://167.233.207.49:7070/appendConfig',
            headers={
                "X-API-Key": API_KEY2,
                "Content-Type": "application/json",
                "Connection": "close",
            },
            json={
              "stub": name,
              "rules": rules
            }
        )

        r = requests.post(
            "http://167.233.207.49:8080/switch", # switch server
            headers={
                "X-API-Key": API_KEY1,
                "Content-Type": "application/json",
                "Connection": "close",
            },
            json={
                "server": name
            },
            timeout=(5, 5),
        )
        time.sleep(1) # give the other ones that have charged in a chance to evaulate if task is being done or not

    
    """
    This is where the tunnel to the VPS has to be set up
    """
    browser = await p.chromium.launch(
        proxy={
            "server": "http://167.233.207.49:8888"
        },
        headless=True
    )
    context = await browser.new_context()
    page = await context.new_page()
    try:
        proxies = {
            "http": "http://167.233.207.49:8888",
            "https": "http://167.233.207.49:8888",
        }
        print(requests.get("http://api.ipify.org", proxies=proxies, timeout=10).text)
        print('WARIO EPIC GAMING')
        await page.goto(url, wait_until="load")
        print('WARIO EPIC GAMING')
        await page.wait_for_timeout(10000)
        print('WARIO EPIC GAMING')
    except Exception as e:
        print(f"URL: {url}")
        print(f"EuropeanServers: {len(EuropeanServers)}")
        print(f"basket: {len(basket)}")
        C = 0
        for row in r.scan_iter():
            C+=1
        D = 0
        for row in rR.scan_iter():
            D+=1
        print(f"r: {C}")
        print(f"rR: {D}")
        print(f"counter: {counter}")
        raise ValueError

    def checkSupplies(r):
        """
        This small function runs an infinite loop that breaks if there is nothing in the database left to query.

        The function will return a key that is available and 'reserve' it by setting its completed value as 'true'.
        If all keys have been completed, it will return false, and this will be used later to control the flow.
        """
        while True:
            found = False
            for key in r.scan_iter(): # scan DB for completed value that says 'false' (it's available)
                row = r.hgetall(key)
                if row['completed'] == 'false':
                    r.hset(key, mapping={"completed":"true"})
                    return key
            if not found: # i.e. nothing on db is left
                break # break out of true loop
        return False

    def writeOutput(scripts, contactId, rR):
        scripts = str(scripts)
        """
        this tiny function updates the output dataframe
        """
        rR.hset(contactId, mapping={
            "scriptData":scripts
        }
              )


    def queue(rR, EuropeanServers, basket, PK):
        """
        This section of the function basically just checks if this replica has to wait before doing its task. The first row of the database
        I am using to save the results tells us how many instances have passed through here already. It is updated roughly every 10 passes (race conditions
        are irrelevant here as we're just trying to throttle as best we can).
    
        'light' is that row, it has two attributes, trafficLight and bodies which (misleadingly) represent a pseudo-boolean which says 'can you do your job
        yet?' and a counter of passes that have already been made under this 'swap'. Every time a function is completed, it adds to the counter.
    
        If over 10 passes have been made already, then it sets the pseudo-boolean to 'you can't do your job yet'.
        """
        light = rR.hgetall("Row1")
        if light['trafficLight'] == 'Green':
            if int(light['bodies']) >= 10:
                # update the row with this information.
                rR.hset("Row1", mapping={"trafficLight":"Red"})
                rR.hset("Row1", mapping={"bodies":"0"})
                time.sleep(1)
                if light['taken'] == 'false':
                    rR.hset("Row1", mapping={"taken":"true"}) # this sets a flag saying 'a worker is already doing the server, don't worry.'
                    changeServer(EuropeanServers, basket)
                    rR.hset("Row1", mapping={"taken":"false", "trafficLight":"Green"}) # when it's done, it tells others
                else:
                    time.sleep(5) # the queue
                    IP = requests.get('https://api.ipify.org').text # this is where all the other processes copy their client IP over to the database for writing ops.
                    rR.hset(PK, mapping={"IP":IP}) # this could still cause errors so you need to wrap everything
                    time.sleep(5) # make sure tunnel is active
        else:
            time.sleep(5) # the queue
            IP = requests.get('https://api.ipify.org').text # this is where all the other processes copy their client IP over to the database for writing ops.
            rR.hset(PK, mapping={"IP":IP}) # this could still cause errors so you need to wrap everything
            time.sleep(5) # make sure tunnel is active

    """
    This should be the infinite while loop function. uses checkSupplies. Basically the whole thing should be wrapped with a giant while loop that uses
    this thing to break if necessary

    why am i flagging this shit on the old table and not just checking the new one for the contactId?
    """

    while True:
        if counter < 3:
            counter+=1
        else:
            if len(ipKeys) == 0:
                for key in rR.scan_iter(): # scan DB for allocated pseudoPKs
                    row = rR.hgetall(key)
                    try:
                        if row['taken'] == 'true':
                            ipKeys.append(key)
                    except:
                        continue
        """
        Implementation of the checkSupplies function. False means nothing found.
        """
        key = checkSupplies(r)
        if key:
            row = r.hmget(key, ["contactId", "firstName", "lastName", "position", "linkedin"])
            contactId, firstName, lastName, positions, linkedinURL = row[0], row[1], row[2], row[3], row[4]
            r.hset(key, mapping={"completed":"true"}) # now to update this row
            light = rR.hgetall("Row1")
            newL = int(light['bodies'])+1
            rR.hset("Row1", mapping={"bodies":str(newL)})
        else:
            break

        """
        Implementation of the race conditions handler, 'queue'. This wraps the server swapper.
        """
        queue(rR, EuropeanServers, basket, primaryKey)


        """
        beginning of the lap
        """
        await context.clear_cookies()
        gc.disable()

        try:
            await page.goto(linkedinURL, wait_until="load", timeout=10000)
        except:
            scripts = []
            writeOutput(scripts, contactId, rR)
            continue
        cookies = await context.cookies()
        ### le
        trkCode = next((c for c in cookies if c["name"] == "trkCode"), None)
        valuetrkCode = trkCode["value"] if trkCode else "bf"

        trkInfo = next((c for c in cookies if c["name"] == "trkInfo"), None)
        valuetrkInfo = trkInfo["value"] if trkInfo else ""
        
        newURL = f"https://www.linkedin.com/authwall?trk={valuetrkCode}&trkInfo={valuetrkInfo}"
        try:
            await page.goto(newURL, wait_until='load', timeout=10000)
        except:
            continue
        
        try:
            await page.set_extra_http_headers({
                "Accept-Language": "en-US,en;q=0.9",
            })
            await page.goto(
                linkedinURL,
                referer="https://www.google.com/",
                wait_until="load",
                timeout=10000
            )
        except:
            continue
        
        try:
            await page.wait_for_selector("body")  # page is alive
            scripts = await page.evaluate("""
            () => Array.from(document.querySelectorAll("script"))
                .map(s => s.textContent.trim())
                .filter(t => t && (
                    t.startsWith("{") || t.startsWith("[")
                ))
            """)
        except:
            scripts = []
        writeOutput(scripts, contactId, rR)
        gc.enable()
        """
        this is the end of the bit
        """
    await context.close()

async def main():
    async with async_playwright() as p:
        tasks = [
            PROCESS(p, 1, 'https://www.google.com'),
        ]

        await asyncio.gather(*tasks)

asyncio.run(main())
