from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User

# 1. Kisan (Farmer) Model
class Farmer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# 2. Doodh Collection Model
class MilkCollection(models.Model):
    SHIFT_CHOICES = (
        ('Morning', 'Morning'),
        ('Evening', 'Evening'),
    )
    
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    litres = models.DecimalField(max_digits=5, decimal_places=2)
    fat = models.DecimalField(max_digits=4, decimal_places=2)
    price_per_litre = models.DecimalField(max_digits=5, decimal_places=2)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    shift = models.CharField(choices=SHIFT_CHOICES, max_length=10)
    date = models.DateField(auto_now_add=True)
    collected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # 🆕 Naye fields Payment track karne ke liye
    is_paid = models.BooleanField(default=False)
    paid_date = models.DateField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.litres and self.price_per_litre:
            self.total_amount = Decimal(str(self.litres)) * Decimal(str(self.price_per_litre))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.farmer.name} - {self.litres}L ({self.shift})"