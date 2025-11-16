from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from .models import Task


class TaskAPITests(APITestCase):
    def setUp(self):
        # --- Utilisateur "normal" ---
        self.user = User.objects.create_user(
            username='dylan',
            email='dylan@example.com',
            password='motdepasse123'
        )

        # Récupérer un access token via SimpleJWT
        token_url = reverse('token_obtain_pair')  # /api/token/
        response = self.client.post(
            token_url,
            {'username': 'dylan', 'password': 'motdepasse123'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.access_token = response.data['access']

        # Mettre le header Authorization par défaut pour tous les appels
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Créer une tâche de base
        self.task = Task.objects.create(
            title='Tâche initiale',
            completed=False,
        )

        # URLs
        self.list_url = reverse('task-list-create')                    # /api/tasks/
        self.detail_url = reverse('task-detail', args=[self.task.pk])  # /api/tasks/<id>/

    # --- LIST ---

    def test_list_tasks(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Tâche initiale')

    # --- CREATE ---

    def test_create_task(self):
        payload = {
            'title': 'Nouvelle tâche',
            'completed': False
        }

        response = self.client.post(self.list_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)
        self.assertEqual(Task.objects.latest('id').title, 'Nouvelle tâche')

    # --- READ (DETAIL) ---

    def test_retrieve_task_detail(self):
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.task.id)
        self.assertEqual(response.data['title'], self.task.title)


    # --- UPDATE ---

    def test_update_task_put(self):
        payload = {
            'title': 'Titre modifié',
            'completed': True
        }

        response = self.client.put(self.detail_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Titre modifié')
        self.assertTrue(self.task.completed)

    def test_partial_update_task_patch(self):
        payload = {'completed': True}

        response = self.client.patch(self.detail_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.task.refresh_from_db()
        self.assertTrue(self.task.completed)

    # --- DELETE (admin only) ---

    def test_delete_task_forbidden_for_non_admin(self):
        # user normal -> doit être 403
        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Task.objects.filter(pk=self.task.pk).exists())

    def test_delete_task_allowed_for_admin(self):
        # On transforme l'user en admin **et staff** (important si ta vue teste is_staff)
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        # Pas besoin de regénérer un token : request.user est chargé depuis la DB
        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(pk=self.task.pk).exists())
