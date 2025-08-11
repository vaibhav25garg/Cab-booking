# booking_api/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
import uuid
import os

def car_image_upload_path(instance, filename):
    """Generate upload path for car images"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('cars', str(instance.car.id), filename)

def location_image_upload_path(instance, filename):
    """Generate upload path for location images"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('locations', str(instance.location.id), filename)

def review_image_upload_path(instance, filename):
    """Generate upload path for review images"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('reviews', str(instance.review.id), filename)

class CarsDetail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seating_capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(50)]
    )
    extra_features = models.JSONField(default=list, help_text="List of extra features")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cars_detail'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Car {self.id} - {self.seating_capacity} seats"

class CarImage(models.Model):
    """Separate model for car images"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    car = models.ForeignKey(
        CarsDetail, 
        on_delete=models.CASCADE, 
        related_name='images'
    )
    image = models.ImageField(upload_to=car_image_upload_path)
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False, help_text="Primary image for the car")
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'car_images'
        ordering = ['order', '-created_at']
        unique_together = ['car', 'order']
    
    def __str__(self):
        return f"Image for {self.car} - Order {self.order}"
    
    def save(self, *args, **kwargs):
        # Ensure only one primary image per car
        if self.is_primary:
            CarImage.objects.filter(car=self.car, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)

class PackageDetails(models.Model):
    CATEGORY_CHOICES = [
        ('adventure', 'Adventure'),
        ('family', 'Family'),
        ('romantic', 'Romantic'),
        ('business', 'Business'),
        ('pilgrimage', 'Pilgrimage'),
        ('wildlife', 'Wildlife'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    package_name = models.CharField(max_length=200)
    package_category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    duration = models.PositiveIntegerField(help_text="Duration in days")
    location = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'package_details'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.package_name} - {self.duration} days"

class LocationDetail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pkg_id = models.ForeignKey(
        PackageDetails, 
        on_delete=models.CASCADE, 
        related_name='locations'
    )
    place_name = models.CharField(max_length=200)
    detail_summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'location_detail'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.place_name} - {self.pkg_id.package_name}"

class LocationImage(models.Model):
    """Separate model for location images"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    location = models.ForeignKey(
        LocationDetail, 
        on_delete=models.CASCADE, 
        related_name='images'
    )
    image = models.ImageField(upload_to=location_image_upload_path)
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False, help_text="Primary image for the location")
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'location_images'
        ordering = ['order', '-created_at']
        unique_together = ['location', 'order']
    
    def __str__(self):
        return f"Image for {self.location.place_name} - Order {self.order}"
    
    def save(self, *args, **kwargs):
        # Ensure only one primary image per location
        if self.is_primary:
            LocationImage.objects.filter(location=self.location, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)

class ReviewDetail(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_name = models.CharField(max_length=100)
    cust_location = models.CharField(max_length=200)
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    message_review = models.TextField()
    mail_authenticated_tag = models.BooleanField(default=False)
    customer_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'review_detail'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer_name} - {self.rating} stars"

class ReviewImage(models.Model):
    """Separate model for review images (customer photos)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    review = models.ForeignKey(
        ReviewDetail, 
        on_delete=models.CASCADE, 
        related_name='images'
    )
    image = models.ImageField(upload_to=review_image_upload_path)
    alt_text = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'review_images'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Image for review by {self.review.customer_name}"

# Alternative: Generic Image Model (if you want even more flexibility)
class Image(models.Model):
    """Generic image model that can be used for any entity"""
    IMAGE_TYPES = [
        ('car', 'Car Image'),
        ('location', 'Location Image'),
        ('review', 'Review Image'),
        ('package', 'Package Image'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image_type = models.CharField(max_length=20, choices=IMAGE_TYPES)
    entity_id = models.UUIDField(help_text="ID of the related entity")
    image = models.ImageField(upload_to='uploads/%Y/%m/%d/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'generic_images'
        ordering = ['order', '-created_at']
        indexes = [
            models.Index(fields=['image_type', 'entity_id']),
        ]
    
    def __str__(self):
        return f"{self.image_type.title()} Image - Order {self.order}"