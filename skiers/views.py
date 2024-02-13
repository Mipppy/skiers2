from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from .helpers.pdf import * 
from .models import *
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt


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

@csrf_exempt
def search(request):
    if request.method == "POST":
        q = request.POST["query"].split(" ")
        bq = q
        if q[0] == "god":
            return HttpResponseRedirect("racers/7514")

        if len(q) > 1:
            try:
                lastname = q[1].upper()
                firstname = q[0].lower().capitalize()
                racer = Racer.objects.filter(lastname__contains=lastname, firstname__contains=firstname)
                if racer:
                    return HttpResponseRedirect("racers/"+str(racer[0].id))

            except Exception as e:
                None

        else:
            bq.append(" ")
            all_matching_racers = Racer.objects.filter(firstname__contains=q[0].lower().capitalize(), lastname__contains=bq[1].upper())
            return render(request, "skiers/search.html", {"racers": all_matching_racers})