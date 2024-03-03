from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from .helpers.pdf import *
from .models import *
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt


def index(request):
    races = Sites.objects.all()
    boyracers = []
    girlracers = []
    vbResults = Result.objects.filter(level="VARSITY BOYS")
    vgResults = Result.objects.filter(level="VARSITY GIRLS")
    for result in vbResults:
        result.racer.team = " ".join(str(result.racer.team).split(" ")[1:])
        boyracers.append({"racer":result.racer, "score": calcTotalRacerScore(result.racer)})
    for result in vgResults:
        result.racer.team = " ".join(str(result.racer.team).split(" ")[1:])
        girlracers.append({"racer":result.racer, "score": calcTotalRacerScore(result.racer)})
    boyracers = [dict(t) for t in {tuple(d.items()) for d in boyracers}]
    girlracers = [dict(t) for t in {tuple(d.items()) for d in girlracers}]
    sorted_boyracers = sorted(boyracers, key=lambda x: x['score'], reverse=True)
    sorted_girlracers = sorted(girlracers, key=lambda x: x['score'], reverse=True)
    return render(request, "skiers/index.html", {
        "races": races,
        "b": sorted_boyracers[:10],
        "g": sorted_girlracers[:10]
    })


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
  totalScore = calcTotalRacerScore(racer)
  scorePos = compareScore(totalScore, racer)
  return render(request, "skiers/racer.html", {
      "racer": racer,
      "results": results,
      "totalScore": totalScore
  })


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
    hit = DirectRacerHit(q)
    if hit:
      return HttpResponseRedirect(hit)
    else:
      bq.append(" ")
      all_matching_racers_first = Racer.objects.filter(
          firstname__icontains=bq[0])
      all_matching_racers_last = Racer.objects.filter(
          lastname__icontains=bq[0])
      all_matching_racers = list(
          set(
              list(all_matching_racers_last) +
              list(all_matching_racers_first)))
      for racer in all_matching_racers:
        racer.team = " ".join(str(racer.team).split(" ")[1:])
      teams = []
      for racer2 in Racer.objects.filter(team__icontains=bq[0]):
        teams.append(" ".join(str(racer2.team).split(" ")[1:]))
      teams = sorted(list(set(teams)))
      return render(request, "skiers/search.html", {
          "racers": all_matching_racers,
          "teams": teams
      })


def teams(request, name):
  racers = []
  for racer2 in Racer.objects.filter(team__icontains=name):
    racer2.team = " ".join(str(racer2.team).split(" ")[1:])
    racers.append(racer2)
  racers = list(set(racers))
  return render(request, "skiers/team.html", {
      "racers": racers,
      "team": racers[0].team
  })


def all_teams(request):
  teams = []
  for racer2 in Racer.objects.all():
    racer2.team = " ".join(str(racer2.team).split(" ")[1:])
    teams.append(racer2.team)
  teams = sorted(list(set(teams)))
  return render(request, "skiers/all_team.html", {"teams": teams})
