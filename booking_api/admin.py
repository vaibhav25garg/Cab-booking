# booking_api/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import (
    CarsDetail, CarImage, 
    PackageDetails, LocationDetail, LocationImage,
    ReviewDetail, ReviewImage
)

class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'order', 'image_preview']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 100px; height: 60px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Preview"

@admin.register(CarsDetail)
class CarsDetailAdmin(admin.ModelAdmin):
    list_display = ['id', 'seating_capacity', 'primary_image_preview', 'image_count', 'created_at']
    list_filter = ['seating_capacity', 'created_at']
    search_fields = ['id', 'seating_capacity']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [CarImageInline]
    
    fieldsets = (
        ('Car Information', {
            'fields': ('id', 'seating_capacity', 'extra_features')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def primary_image_preview(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image and primary_image.image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 40px; object-fit: cover; border-radius: 4px;" />',
                primary_image.image.url
            )
        return "No primary image"
    primary_image_preview.short_description = "Primary Image"
    
    def image_count(self, obj):
        count = obj.images.count()
        return format_html(
            '<span style="background: #007cba; color: white; padding: 2px 6px; border-radius: 3px;">{}</span>',
            count
        )
    image_count.short_description = "Images"

@admin.register(CarImage)
class CarImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'car_info', 'image_preview', 'is_primary', 'order', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['car__id', 'alt_text']
    list_editable = ['is_primary', 'order']
    readonly_fields = ['image_preview_large']
    
    def car_info(self, obj):
        return f"{obj.car.seating_capacity} seats"
    car_info.short_description = "Car"
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 40px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Preview"
    
    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 200px; object-fit: contain;" />',
                obj.image.url
            )
        return "No image"
    image_preview_large.short_description = "Image Preview"

class LocationImageInline(admin.TabularInline):
    model = LocationImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'order', 'image_preview']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 100px; height: 60px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Preview"

class LocationDetailInline(admin.StackedInline):
    model = LocationDetail
    extra = 0
    fields = ['place_name', 'detail_summary']
    show_change_link = True

@admin.register(PackageDetails)
class PackageDetailsAdmin(admin.ModelAdmin):
    list_display = ['package_name', 'package_category', 'duration', 'location', 'locations_count', 'created_at']
    list_filter = ['package_category', 'duration', 'created_at']
    search_fields = ['package_name', 'location', 'package_category']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [LocationDetailInline]
    
    fieldsets = (
        ('Package Information', {
            'fields': ('package_name', 'package_category', 'duration', 'location')
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def locations_count(self, obj):
        count = obj.locations.count()
        return format_html(
            '<span style="background: #28a745; color: white; padding: 2px 6px; border-radius: 3px;">{}</span>',
            count
        )
    locations_count.short_description = "Locations"

@admin.register(LocationDetail)
class LocationDetailAdmin(admin.ModelAdmin):
    list_display = ['place_name', 'package_info', 'primary_image_preview', 'image_count', 'created_at']
    list_filter = ['pkg_id__package_category', 'created_at']
    search_fields = ['place_name', 'pkg_id__package_name', 'detail_summary']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [LocationImageInline]
    
    fieldsets = (
        ('Location Information', {
            'fields': ('pkg_id', 'place_name', 'detail_summary')
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def package_info(self, obj):
        return f"{obj.pkg_id.package_name} ({obj.pkg_id.duration}d)"
    package_info.short_description = "Package"
    
    def primary_image_preview(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image and primary_image.image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 40px; object-fit: cover; border-radius: 4px;" />',
                primary_image.image.url
            )
        return "No primary image"
    primary_image_preview.short_description = "Primary Image"
    
    def image_count(self, obj):
        count = obj.images.count()
        return format_html(
            '<span style="background: #007cba; color: white; padding: 2px 6px; border-radius: 3px;">{}</span>',
            count
        )
    image_count.short_description = "Images"

@admin.register(LocationImage)
class LocationImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'location_info', 'image_preview', 'is_primary', 'order', 'created_at']
    list_filter = ['is_primary', 'created_at', 'location__pkg_id__package_category']
    search_fields = ['location__place_name', 'location__pkg_id__package_name', 'alt_text']
    list_editable = ['is_primary', 'order']
    readonly_fields = ['image_preview_large']
    
    def location_info(self, obj):
        return f"{obj.location.place_name}"
    location_info.short_description = "Location"
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 40px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Preview"
    
    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 200px; object-fit: contain;" />',
                obj.image.url
            )
        return "No image"
    image_preview_large.short_description = "Image Preview"

class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 1
    fields = ['image', 'alt_text', 'image_preview']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 100px; height: 60px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Preview"

@admin.register(ReviewDetail)
class ReviewDetailAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'rating_stars', 'cust_location', 'mail_authenticated_tag', 'image_count', 'created_at']
    list_filter = ['rating', 'mail_authenticated_tag', 'created_at', 'cust_location']
    search_fields = ['customer_name', 'customer_email', 'cust_location', 'message_review']
    readonly_fields = ['id', 'created_at']
    list_editable = ['mail_authenticated_tag']
    inlines = [ReviewImageInline]
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer_name', 'customer_email', 'cust_location')
        }),
        ('Review Details', {
            'fields': ('rating', 'message_review', 'mail_authenticated_tag')
        }),
        ('System Information', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        colors = {5: '#28a745', 4: '#6f42c1', 3: '#fd7e14', 2: '#dc3545', 1: '#dc3545'}
        return format_html(
            '<span style="color: {}; font-size: 16px;">{}</span>',
            colors.get(obj.rating, '#6c757d'),
            stars
        )
    rating_stars.short_description = "Rating"
    
    def image_count(self, obj):
        count = obj.images.count()
        return format_html(
            '<span style="background: #007cba; color: white; padding: 2px 6px; border-radius: 3px;">{}</span>',
            count
        )
    image_count.short_description = "Images"

@admin.register(ReviewImage)
class ReviewImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'review_info', 'image_preview', 'created_at']
    list_filter = ['created_at', 'review__rating']
    search_fields = ['review__customer_name', 'review__customer_email', 'alt_text']
    readonly_fields = ['image_preview_large']
    
    def review_info(self, obj):
        return f"{obj.review.customer_name} ({obj.review.rating}★)"
    review_info.short_description = "Review"
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 40px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Preview"
    
    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 200px; object-fit: contain;" />',
                obj.image.url
            )
        return "No image"
    image_preview_large.short_description = "Image Preview"

# Custom Admin Site Configuration
admin.site.site_header = "Travel Booking Admin"
admin.site.site_title = "Travel Booking"
admin.site.index_title = "Welcome to Travel Booking Administration"