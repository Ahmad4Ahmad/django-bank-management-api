from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from django.core.mail import send_mail
from .models import User
from .serializers import UserSerializer, UserLoginSerializer
from drf_spectacular.utils import extend_schema

@extend_schema(tags=['User'])
class UserCreateView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            # Send a welcome email
            send_mail(
                'Welcome to Our Bank!',
                f'Welcome, {user.email}! Thank you for creating an account.',
                'from@example.com',  # Replace with your sender email
                [user.email],
                fail_silently=False,
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except ValidationError as e:
            return Response({"errors": e.detail}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=['User'])
class UserUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

@extend_schema(tags=['User'])
class UserDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()

@extend_schema(tags=['User'])
class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        response_data = Response({'refresh': str(refresh), 'access': str(refresh.access_token)})
        return response_data

@extend_schema(tags=['User'])
class UserLogoutView(generics.GenericAPIView):
    def post(self, request):
        try:
            # Get the refresh token from the request
            refresh_token = request.data.get('refresh')

            # Blacklist the refresh token
            token = OutstandingToken.objects.get(token=refresh_token)
            BlacklistedToken.objects.create(token=token)

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except OutstandingToken.DoesNotExist:
            return Response({'detail': 'Token not found'}, status=status.HTTP_400_BAD_REQUEST)