import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class UserRegistrationTest(TestCase):
    def test_register_new_user(self):
        client = Client()
        response = client.post(
            "/users/register/",
            {
                "name": "Test",
                "surname": "User",
                "email": "test@example.com",
                "password": "testpass123",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/projects/list/")
        self.assertTrue(User.objects.filter(email="test@example.com").exists())

    def test_login_with_email(self):
        User.objects.create_user(
            email="testlogin@example.com",
            name="Test",
            surname="Login",
            password="testpass123",
        )
        client = Client()
        response = client.post(
            "/users/login/",
            {
                "email": "testlogin@example.com",
                "password": "testpass123",
            },
        )
        self.assertEqual(response.status_code, 302)

    def test_user_detail_page(self):
        user = User.objects.create_user(
            email="detail@example.com",
            name="Detail",
            surname="Test",
            password="testpass123",
        )
        client = Client()
        response = client.get(f"/users/{user.id}/")
        self.assertEqual(response.status_code, 200)

    def test_user_list_page(self):
        client = Client()
        response = client.get("/users/list/")
        self.assertEqual(response.status_code, 200)

    def test_add_user_skill_returns_skill_name(self):
        user = User.objects.create_user(
            email="skills@example.com",
            name="Skill",
            surname="Owner",
            password="testpass123",
        )
        client = Client()
        client.login(username="skills@example.com", password="testpass123")

        response = client.post(
            f"/users/{user.id}/skills/add/",
            data=json.dumps({"name": "Python"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["name"], "Python")
        self.assertTrue(user.skills.filter(name="Python").exists())

    def test_edit_profile_contains_email_field(self):
        user = User.objects.create_user(
            email="edit@example.com",
            name="Edit",
            surname="Profile",
            password="testpass123",
        )
        client = Client()
        client.login(username="edit@example.com", password="testpass123")

        response = client.get(f"/users/{user.id}/edit/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="email"')
