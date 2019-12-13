"""jobSearch URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path("", views.home, name="home")
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path("", Home.as_view(), name="home")
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path("blog/", include("blog.urls"))
"""
import xadmin
from django.urls import path, include
from django.views import static
from django.conf import settings
from django.conf.urls import url
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter

from job.views import IndexView, JobSummary, JobDetailQuery, JobDetailTable, JobDownload
from job.views import JobDetailViewSet


job_detail_drf = JobDetailViewSet.as_view({"get": "list"})

urlpatterns = [
    path("xadmin/", xadmin.site.urls),
    url(r"^docs/", include_docs_urls(title="全职搜")),
    url(r"^static/(?P<path>.*)$", static.serve, {"document_root": settings.STATIC_ROOT}, name="static"),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url(r"^$", IndexView.as_view(), name="index"),
    url(r"^users/", include(("users.urls", "users"), namespace="users")),
    url(r"^job_summary/$", JobSummary.as_view(), name="job_summary"),
    url(r"^job_detail/$", JobDetailQuery.as_view(), name="job_detail"),
    url(r"^job_detail_table/$", JobDetailTable.as_view(), name="job_detail_table"),
    url(r"^download_job_detail/$", JobDownload.as_view(), name="download_job_detail"),
    url(r"^job_detail_drf/$", job_detail_drf, name="job_detail_drf"),

]
