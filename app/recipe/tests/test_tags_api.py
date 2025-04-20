"""
Tests for the tags API.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core import models
from recipe.serializers import TagSerializer


TAGS_URL = reverse("recipe:tag-list")


def create_user(email="testtag@example.com", password="testpass123"):
    """Create a user."""
    return models.User.objects.create_user(email=email, password=password)


class PublicTagsApiTests(TestCase):
    """Test the publicly available tags API."""

    def setUp(self):
        """Set up the test client."""
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required."""
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test the private tags API."""

    def setUp(self):
        """Set up the test client."""
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags."""
        models.Tag.objects.create(user=self.user, name="Vegan")
        models.Tag.objects.create(user=self.user, name="Dessert")
        res = self.client.get(TAGS_URL)
        tags = models.Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for the authenticated user."""
        user2 = create_user(email="userexample2@example.com")
        models.Tag.objects.create(user=user2, name="Fruity")
        tag = models.Tag.objects.create(user=self.user, name="Comfort Food")
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], tag.name)
        self.assertEqual(res.data[0]["id"], tag.id)
