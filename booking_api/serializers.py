# ============================================================================
# booking_api/serializers.py - Updated with car_name and car_description
# ============================================================================

from rest_framework import serializers
from .models import (
    CarsDetail, CarImage,
    PackageDetails, LocationDetail, LocationImage,
    ReviewDetail, ReviewImage
)

class CarImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']

class CarsDetailSerializer(serializers.ModelSerializer):
    images = CarImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        help_text="Upload multiple images"
    )
    primary_image = serializers.SerializerMethodField()
    image_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CarsDetail
        fields = [
            'id', 'car_name', 'car_description', 'seating_capacity', 'extra_features',
            'images', 'uploaded_images', 'primary_image', 'image_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_primary_image(self, obj):
        primary = obj.images.filter(is_primary=True).first()
        if primary:
            request = self.context.get('request')
            return request.build_absolute_uri(primary.image.url) if request else primary.image.url
        return None
    
    def get_image_count(self, obj):
        return obj.images.count()
    
    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        car = CarsDetail.objects.create(**validated_data)
        
        for i, image in enumerate(uploaded_images):
            CarImage.objects.create(
                car=car,
                image=image,
                is_primary=(i == 0),
                order=i + 1
            )
        return car
    
    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        
        # Update car details
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Add new images if provided
        if uploaded_images:
            current_count = instance.images.count()
            for i, image in enumerate(uploaded_images):
                CarImage.objects.create(
                    car=instance,
                    image=image,
                    is_primary=(current_count == 0 and i == 0),  # Set as primary if no existing images
                    order=current_count + i + 1
                )
        
        return instance

class LocationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']

class LocationDetailSerializer(serializers.ModelSerializer):
    images = LocationImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    primary_image = serializers.SerializerMethodField()
    package_name = serializers.CharField(source='pkg_id.package_name', read_only=True)
    
    class Meta:
        model = LocationDetail
        fields = [
            'id', 'pkg_id', 'place_name', 'detail_summary', 'package_name',
            'images', 'uploaded_images', 'primary_image',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        location = LocationDetail.objects.create(**validated_data)
        
        for i, image in enumerate(uploaded_images):
            LocationImage.objects.create(
                location=location,
                image=image,
                is_primary=(i == 0),
                order=i + 1
            )
        return location
    
    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        
        # Update location details
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Add new images if provided
        if uploaded_images:
            current_count = instance.images.count()
            for i, image in enumerate(uploaded_images):
                LocationImage.objects.create(
                    location=instance,
                    image=image,
                    is_primary=(current_count == 0 and i == 0),  # Set as primary if no existing images
                    order=current_count + i + 1
                )
        
        return instance
    
    def get_primary_image(self, obj):
        primary = obj.images.filter(is_primary=True).first()
        if primary:
            request = self.context.get('request')
            return request.build_absolute_uri(primary.image.url) if request else primary.image.url
        return None

class PackageDetailsSerializer(serializers.ModelSerializer):
    locations = LocationDetailSerializer(many=True, read_only=True)
    locations_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageDetails
        fields = [
            'id', 'package_name', 'package_category', 'duration', 
            'location', 'locations', 'locations_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_locations_count(self, obj):
        return obj.locations.count()

class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ['id', 'image', 'alt_text', 'created_at']
        read_only_fields = ['id', 'created_at']

class ReviewDetailSerializer(serializers.ModelSerializer):
    images = ReviewImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    rating_stars = serializers.SerializerMethodField()
    
    class Meta:
        model = ReviewDetail
        fields = [
            'id', 'customer_name', 'cust_location', 'rating', 'rating_stars',
            'message_review', 'mail_authenticated_tag', 'customer_email',
            'images', 'uploaded_images', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_rating_stars(self, obj):
        return '★' * obj.rating + '☆' * (5 - obj.rating)
    
    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        review = ReviewDetail.objects.create(**validated_data)
        
        for image in uploaded_images:
            ReviewImage.objects.create(review=review, image=image)
        return review

# List serializers (simplified for performance) - UPDATED
class CarsDetailListSerializer(serializers.ModelSerializer):
    primary_image = serializers.SerializerMethodField()
    image_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CarsDetail
        fields = [
            'id', 'car_name', 'car_description', 'extra_features' ,'seating_capacity', 
            'primary_image', 'image_count', 'created_at'
        ]
    
    def get_primary_image(self, obj):
        primary = obj.images.filter(is_primary=True).first()
        if primary:
            request = self.context.get('request')
            return request.build_absolute_uri(primary.image.url) if request else primary.image.url
        return None
    
    def get_image_count(self, obj):
        return obj.images.count()

class PackageDetailsListSerializer(serializers.ModelSerializer):
    locations_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageDetails
        fields = ['id', 'package_name', 'package_category', 'duration', 'location', 'locations_count', 'created_at']
    
    def get_locations_count(self, obj):
        return obj.locations.count()