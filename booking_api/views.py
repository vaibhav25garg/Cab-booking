# ============================================================================
# booking_api/views.py - Updated with car_name and car_description search
# ============================================================================

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg
from django.core.cache import cache
from django.core.mail import send_mail

import uuid
from .models import (
    CarsDetail, CarImage, PackageDetails, LocationDetail, 
    LocationImage, ReviewDetail, ReviewImage
)
from .serializers import (
    CarsDetailSerializer, CarsDetailListSerializer,
    PackageDetailsSerializer, PackageDetailsListSerializer,
    LocationDetailSerializer, ReviewDetailSerializer,
    CarImageSerializer, LocationImageSerializer, ReviewImageSerializer
)

class CarsDetailViewSet(viewsets.ModelViewSet):
    queryset = CarsDetail.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['seating_capacity']
    search_fields = ['car_name', 'car_description', 'seating_capacity']  # Updated search fields
    ordering_fields = ['created_at', 'seating_capacity', 'car_name']  # Added car_name to ordering
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CarsDetailListSerializer
        return CarsDetailSerializer
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_images(self, request, pk=None):
        car = self.get_object()
        images = request.FILES.getlist('images')
        
        if not images:
            return Response({'error': 'No images provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        created_images = []
        for i, image in enumerate(images):
            car_image = CarImage.objects.create(
                car=car, image=image, order=car.images.count() + i + 1
            )
            created_images.append(CarImageSerializer(car_image, context={'request': request}).data)
        
        return Response({
            'message': f'{len(created_images)} images added successfully',
            'images': created_images
        }, status=status.HTTP_201_CREATED)

class PackageDetailsViewSet(viewsets.ModelViewSet):
    queryset = PackageDetails.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['package_category', 'duration']
    search_fields = ['package_name', 'location']
    ordering_fields = ['created_at', 'duration']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PackageDetailsListSerializer
        return PackageDetailsSerializer
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get all available categories"""
        categories = [{'value': choice[0], 'label': choice[1]} 
                     for choice in PackageDetails.CATEGORY_CHOICES]
        return Response(categories)

class LocationDetailViewSet(viewsets.ModelViewSet):
    queryset = LocationDetail.objects.all()
    serializer_class = LocationDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['pkg_id']
    search_fields = ['place_name', 'detail_summary']
    ordering = ['-created_at']

class ReviewDetailViewSet(viewsets.ModelViewSet):
    queryset = ReviewDetail.objects.all()
    serializer_class = ReviewDetailSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['rating', 'mail_authenticated_tag']
    search_fields = ['customer_name', 'cust_location']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']

    def get_permissions(self):
        # Allow unauthenticated access for create, list, retrieve, and verify
        if self.action in ['create', 'list', 'retrieve', 'verify']:
            return []
        return [IsAuthenticated()]

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        total_reviews = self.queryset.count()
        avg_rating = self.queryset.aggregate(Avg('rating'))['rating__avg'] or 0

        rating_stats = {}
        for i in range(1, 6):
            rating_stats[f'{i}_star'] = self.queryset.filter(rating=i).count()

        return Response({
            'total_reviews': total_reviews,
            'average_rating': round(avg_rating, 2),
            'rating_distribution': rating_stats,
            'verified_reviews': self.queryset.filter(mail_authenticated_tag=True).count()
        })

    def create(self, request, *args, **kwargs):
        """Create review with email verification"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review = serializer.save()

        # Generate verification token and store in cache
        verification_token = str(uuid.uuid4())
        cache.set(f'verify_review_{verification_token}', review.id, timeout=86400)  # 24 hours

        verification_url = f"{request.build_absolute_uri('/api/reviews/verify/')}?token={verification_token}"

        # Send email to owner for approval
        OWNER_EMAIL = "vaibhavgarg977@gmail.com"
        send_mail(
            subject="New Review Pending Approval",
            message=(
                f"A new review has been submitted:\n\n"
                f"Customer: {review.customer_name}\n"
                f"Rating: {review.rating}\n"
                f"Location: {review.cust_location}\n\n"
                f"Approve here: {verification_url}"
            ),
            from_email='vaibhavgarg977@gmail.com',
            recipient_list=[OWNER_EMAIL],
            fail_silently=False,
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def verify(self, request):
        """Verify review via email link"""
        token = request.query_params.get('token')
        review_id = cache.get(f'verify_review_{token}')

        if review_id:
            review = ReviewDetail.objects.get(id=review_id)
            review.mail_authenticated_tag = True
            review.save()
            cache.delete(f'verify_review_{token}')
            return Response({'message': 'Review verified successfully'})

        return Response({'error': 'Invalid or expired token'}, status=400)