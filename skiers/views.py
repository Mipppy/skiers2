from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from .helpers.pdf import * 
from .models import *
from django.urls import reverse


def index(request):
    races = Sites.objects.all()
    racers = []
    for result in Result.objects.all():
        if result.place == 1:
            result.racer.team = " ".join(str(result.racer.team).split(" ")[1:])
            racers.append(result)
    racers = racers[:20]
    return render(request, "skiers/index.html", {"races": races, "racers": racers})

def rescan(request):
    hrefs = mainPDFFunc()
    allPDFdata = PDFListedData(hrefs)
    parseRacerData(allPDFdata)
    return HttpResponseRedirect(reverse("index"))

def racer(request, id):
    racer = Racer.objects.get(id=id)
    results = Result.objects.filter(racer=racer)
    racer.team = " ".join(str(racer.team).split(" ")[1:])
    racer.lastname = racer.lastname.lower().capitalize()[:-1]
    return render(request, "skiers/racer.html", {"racer": racer, "results": results})

def tracked_racers(request):
    racer = Racer.objects.all()
    for race in racer:
        race.team = " ".join(str(race.team).split(" ")[1:])
    return render(request, "skiers/tracked_racers.html", {"racers": racer})
