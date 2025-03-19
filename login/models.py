from django.db import models
from django.contrib.auth.models import User

class RecommendationInput(models.Model):
    class Meta:
        app_label = 'login'

    TRANSPORT_CHOICES = [
        ('bus', '버스'),
        ('subway', '지하철'),
        ('car', '자가용'),
    ]
    
    FACILITY_CHOICES = [
        ('convenience_store', '편의점'),
        ('mart', '마트'),
        ('laundry', '세탁소'),
    ]
    
    PROPERTY_TYPE_CHOICES = [
        ('jeonse', '전세'),
        ('monthly', '월세'),
        ('sale', '매매'),
    ]
    
    age = models.PositiveIntegerField()
    transport = models.CharField(max_length=10, choices=TRANSPORT_CHOICES)
    facility = models.CharField(max_length=20, choices=FACILITY_CHOICES)
    property_type = models.CharField(max_length=10, choices=PROPERTY_TYPE_CHOICES)
    desired_location = models.CharField(max_length=100)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=30, blank=True)
    image_link = models.URLField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
