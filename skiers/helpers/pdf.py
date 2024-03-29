# Scans all links in underdogtiming and gets a all the race data for every nordic race
import io, re
import requests
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from ..models import *

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Windows; Windows x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36"
}

blacklistedLinks = []


def scanPDFs(list):
    biglist = []
    for url in list:
        response = requests.get(url=url, headers=headers, timeout=120)
        on_fly_mem_obj = io.BytesIO(response.content)
        pdf_file = PdfReader(on_fly_mem_obj)
        biglist.append(parsePDF(pdf_file.pages, url))
    return biglist


def parsePDF(pages, url):
    page_text = []
    for page in pages:
        page_text.append(page.extract_text())
    return page_text


def mainPDFFunc():
    url = "https://www.underdogtiming.com/general-5"
    response = requests.get(url=url, headers=headers, timeout=120)
    soup = BeautifulSoup(response.content, "html.parser")
    segments = soup.find_all("p", class_="font_8")
    goodsegs = []
    goodtitle = []
    for seg in segments:
        backseg = seg.text
        seg = str(seg)
        if seg.find("Nordic") != -1 or seg.find("JNQ") != -1:
            minsoup = BeautifulSoup(seg, "html.parser")
            minseg = minsoup.find_all("a")
            for seg2 in minseg:
                if (
                    "underdogtiming.com/_files" in str(seg2["href"])
                    and str(seg2).find("Team") == -1
                    and str(seg2).find("Start") == -1
                    and str(seg2) not in blacklistedLinks
                ):
                    goodsegs.append(seg2["href"])
                    result = backseg.split("\xa0")
                    goodtitle.append(result[0])
    for index, segment in enumerate(goodsegs):
        if Sites.objects.filter(site=goodsegs[index], title=goodtitle[index]):
            None
        else:
            site = Sites(site=goodsegs[index], title=goodtitle[index])
            site.save()
    return goodsegs


def PDFreadline(text, url):
    title = str(Sites.objects.filter(site=url).first().title)
    if not title:
        title = url
    text = text.split("\\n")
    text_with_suffix = [[txt, title] for txt in text]
    return text_with_suffix


def PDFListedData(hrefs):
    allPDFdata = []
    datas = scanPDFs(hrefs)
    for data in datas:
        if all(element == "" for element in data) == False:
            allPDFdata.append(PDFreadline(str(data), hrefs[datas.index(data)]))
    return allPDFdata


def parseRacerData(data):
    lastUsedClass = None
    for sub in data:  # page in data
        for race in sub:  # line in page
            if race != "":
                try:
                    parsed_race = str(race[0]).split(" ")
                    parsed_race = [item for item in parsed_race if item != ""]
                    time_pattern = re.compile(r"^:(\d{2}:\d{2}.\d)$")
                    score_pattern = re.compile(r"\d+(\.\d+)?")
                    classKeywords = [
                        "VARSITY BOYS",
                        "VARSITY GIRLS",
                        "JUNIOR VARSITY BOYS",
                        "JUNIOR VARSITY GIRLS",
                        "BEGINNER BOYS",
                        "BEGINNER GIRLS",
                        "MIDDLE SCHOOL BOYS",
                        "MIDDLE SCHOOL GIRLS",
                    ]
                    class_search_list = " ".join(parsed_race).upper()
                    if class_search_list in classKeywords:
                        lastUsedClass = class_search_list
                    if (
                        parsed_race[0].isdigit()
                        and parsed_race[1].isdigit()
                        and time_pattern.match(parsed_race[2])
                        and score_pattern.match(parsed_race[3])
                        and parsed_race[4].isalpha()
                    ):
                        parsed_race = [parsed_race, race[1], lastUsedClass]
                        addRaceToDatabase(parsed_race)
                except Exception as e:
                    continue


def addRaceToDatabase(race):
    racer = racerExistsAlready(race[0])
    doesResultExistYet(race, racer)


def racerExistsAlready(race):
    firstname = None
    lastname = None
    elements_before_float = []
    for index, element in enumerate(race):
        if (
            element
            and element[0].isupper()
            and all(c.islower() or not c.isalpha() for c in element[1:])
            and not any(c.isdigit() for c in element)
        ):
            firstname = element
            lastname = race[index - 1]
            i = index - 1
            while i > 3:
                i -= 1
                elements_before_float.insert(0, race[i])
    racerQuery = Racer.objects.filter(firstname=firstname, lastname=lastname)
    if not racerQuery:
        new_racer = Racer(
            firstname=firstname, lastname=lastname, team=" ".join(elements_before_float)
        )
        new_racer.save()
        return new_racer
    else:
        return racerQuery


def doesResultExistYet(race, racer):
    truescore = additionalScoreShenaggings(race)
    objects = Result.objects.filter(
        racer=racer[0],
        time=race[0][2],
        bib=int(race[0][0]),
        place=int(race[0][1]),
        score=truescore,
        racename=race[1],
        level=race[2],
    )
    if not objects:
        racer_result = Result(
            racer=racer[0],
            time=race[0][2],
            bib=int(race[0][0]),
            place=int(race[0][1]),
            score=truescore,
            racename=race[1],
            level=race[2],
        )
        racer_result.save()
        return racer_result
    else:
        return None


def additionalScoreShenaggings(race):
    scores = (24, 22, 20, 18, 16, 14, 12, 10, 8, 6, 4, 2, 1)
    score = scores[int(race[0][1]) - 1] if 1 <= int(race[0][1]) <= len(scores) else 0
    return score


def DirectRacerHit(q):
    try:
        lastname = q[1].upper()
        firstname = q[0].lower().capitalize()
        racer = Racer.objects.filter(
            lastname__contains=lastname, firstname__contains=firstname
        )
        if racer:
            return "/racers/" + str(racer[0].id)
    except Exception as e:
        return None


def compareScore(score, racer):
    masterList = [{"racer": racer, "score": score}]
    for racer2 in Racer.objects.all():
        masterList.append({"racer": racer2, "score": calcTotalRacerScore(racer2)})
    sortedMasterList = sorted(masterList, key=lambda x: x["score"], reverse=True)
    original_racer_index = (
        next((i for i, d in enumerate(sortedMasterList) if d["racer"] == racer), None)
        + 1
    )
    return original_racer_index


def calcTotalRacerScore(racer):
    total = 0
    for result in Result.objects.filter(racer=racer):
        total = total + result.score
    return total


# Racer.objects.all().delete()
# Result.objects.all().delete()
# Sites.objects.all().delete()
