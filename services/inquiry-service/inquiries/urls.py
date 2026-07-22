from django.urls import path

from . import views

urlpatterns = [
    path("", views.CreateInquiryView.as_view()),
    path("mine", views.MyInquiriesView.as_view()),
    path("received", views.ReceivedInquiriesView.as_view()),
    path("<str:pk>/respond", views.RespondToInquiryView.as_view()),
]
