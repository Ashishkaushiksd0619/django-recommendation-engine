
from django.db import models
from django.contrib.auth.models import User

class Chain(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Canteen(models.Model):
    name = models.CharField(max_length=100)
    chain = models.ForeignKey(Chain, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

class Food(models.Model):
    title = models.CharField(max_length=200)
    canteen = models.ForeignKey(Canteen, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    num_orders = models.IntegerField(default=0)
    category = models.CharField(max_length=100)
    avg_rating = models.FloatField(default=0)
    num_rating = models.IntegerField(default=0)
    tags = models.CharField(max_length=200)

    def __str__(self):
        return self.title

class Promotion(models.Model):
    PROMO_LEVELS = [('local', 'Local'), ('national', 'National')]
    code = models.CharField(max_length=50)
    discount_percent = models.FloatField()
    canteen = models.ForeignKey(Canteen, on_delete=models.CASCADE, null=True, blank=True)
    chain = models.ForeignKey(Chain, on_delete=models.CASCADE, null=True, blank=True)
    level = models.CharField(max_length=10, choices=PROMO_LEVELS)
    valid_from = models.DateField()
    valid_to = models.DateField()

    def __str__(self):
        return f"{self.code} ({self.level})"

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart: {self.user.username} - {self.food.title}"

class ViewingHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Viewed: {self.user.username} - {self.food.title}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    home_canteen = models.ForeignKey(Canteen, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.user.username} Profile"

class NewAndSpecial(models.Model):
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    is_special = models.BooleanField(default=False)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        status = "Special" if self.is_special else "New"
        return f"{self.food.title} - {status}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ordered {self.food.title}"