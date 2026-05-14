from django.test import Client, TestCase

from projects.models import Project
from users.models import User


class ProjectTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="proj@example.com",
            name="Project",
            surname="Owner",
            password="testpass123",
        )
        self.client = Client()
        self.client.login(username="proj@example.com", password="testpass123")

    def test_project_list(self):
        response = self.client.get("/projects/list/")
        self.assertEqual(response.status_code, 200)

    def test_create_project(self):
        response = self.client.post(
            "/projects/create-project/",
            {
                "name": "Test Project",
                "description": "A test project",
                "status": "open",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Project.objects.filter(name="Test Project").exists())

    def test_project_detail(self):
        project = Project.objects.create(
            name="Detail Project",
            owner=self.user,
            status="open",
        )
        project.participants.add(self.user)
        response = self.client.get(f"/projects/{project.id}/")
        self.assertEqual(response.status_code, 200)

    def test_cannot_join_closed_project(self):
        other_user = User.objects.create_user(
            email="member@example.com",
            name="Member",
            surname="User",
            password="testpass123",
        )
        project = Project.objects.create(
            name="Closed Project",
            owner=self.user,
            status="closed",
        )
        project.participants.add(self.user)

        client = Client()
        client.login(username="member@example.com", password="testpass123")
        response = client.post(f"/projects/{project.id}/toggle-participate/")

        self.assertEqual(response.status_code, 400)
        self.assertFalse(project.participants.filter(pk=other_user.pk).exists())

    def test_guest_does_not_see_create_project_button(self):
        Project.objects.create(
            name="Visible Project",
            owner=self.user,
            status="open",
        )

        guest_client = Client()
        response = guest_client.get("/projects/list/")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "+ Создать проект")

    def test_project_list_has_pagination_controls(self):
        for idx in range(13):
            project = Project.objects.create(
                name=f"Project {idx}",
                owner=self.user,
                status="open",
            )
            project.participants.add(self.user)

        response = self.client.get("/projects/list/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "?page=2")
