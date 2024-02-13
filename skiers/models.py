from django.db import models

# Create your models here.
class Sites(models.Model):
    site = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    
class Racer(models.Model):
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    team = models.CharField(max_length=50)
class Result(models.Model):
    racer = models.ForeignKey(Racer, on_delete=models.CASCADE)
    time = models.CharField(max_length=100)
    bib = models.IntegerField()
    place = models.IntegerField()
    score = models.FloatField()
    racename = models.CharField(max_length=200)
