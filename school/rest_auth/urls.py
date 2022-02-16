from django.urls import re_path
from rest_auth.views import UserRegistrationAPIView, UserLoginView, MemberAPIView, PassResetAPIView

urlpatterns = [
    re_path(r"^sign-up/$", UserRegistrationAPIView.as_view()),  # Registration
    re_path(r"^login/$", UserLoginView.as_view()),  # Login (to get jwt token)
    re_path(r"^reset-pass/$", PassResetAPIView.as_view()),

    re_path(r"^$", MemberAPIView.as_view()),  # Listing API
    re_path(r"^(?P<pk>[\w\d-]+)/$", MemberAPIView.as_view()),  # pk can be UUID also (if defined as UUID in models)
]