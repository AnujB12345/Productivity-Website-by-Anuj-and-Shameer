import json
from datetime import time, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from dashboard.models import Goal
from todo.models import Todo
from notes.models import Note
from calendar_app.models import CalendarEvent


class GoalModelTest(TestCase):
    """Tests for the Goal model."""

    def test_goal_creation_and_defaults(self):
        goal = Goal.objects.create(username="testuser")
        self.assertEqual(goal.notes_goal, 5)
        self.assertEqual(goal.pomodoro_goal, 8)
        self.assertEqual(str(goal), "testuser's goal")

    def test_goal_unique_username(self):
        Goal.objects.create(username="testuser")
        with self.assertRaises(Exception):
            Goal.objects.create(username="testuser")


class DashboardViewTest(TestCase):
    """Tests for the dashboard view, logic, and POST handlers."""

    def setUp(self):
        self.client = Client()
        self.username = "testuser"
        self.dashboard_url = reverse("dashboard:dashboard")

        session = self.client.session
        session["username"] = self.username
        session.save()

    def test_dashboard_redirect_if_not_logged_in(self):
        session = self.client.session
        session.pop("username", None)
        session.save()

        response = self.client.get(self.dashboard_url)
        self.assertRedirects(response, reverse("users:login"))

    def test_dashboard_access_when_logged_in(self):
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard_page.html")

    def test_update_notes_goal_valid(self):
        response = self.client.post(
            self.dashboard_url,
            {"update_goal": "1", "notes_goal": "15"}
        )
        self.assertRedirects(response, self.dashboard_url)

        goal = Goal.objects.get(username=self.username)
        self.assertEqual(goal.notes_goal, 15)

    def test_update_notes_goal_invalid_ignored(self):
        Goal.objects.create(username=self.username, notes_goal=5)

        for invalid in ["-5", "0", "abc", ""]:
            self.client.post(
                self.dashboard_url,
                {"update_goal": "1", "notes_goal": invalid}
            )
            goal = Goal.objects.get(username=self.username)
            self.assertEqual(goal.notes_goal, 5)

    def test_update_pomodoro_goal_valid(self):
        response = self.client.post(
            self.dashboard_url,
            {"update_pomodoro_goal": "1", "pomodoro_goal": "12"}
        )
        self.assertRedirects(response, self.dashboard_url)

        goal = Goal.objects.get(username=self.username)
        self.assertEqual(goal.pomodoro_goal, 12)

    def test_week_over_week_and_total_calculations(self):
        now = timezone.now()

        Todo.objects.create(username=self.username, title="T1", checkbox=True, completed_at=now - timedelta(days=2))
        Todo.objects.create(username=self.username, title="T2", checkbox=True, completed_at=now - timedelta(days=3))
        Todo.objects.create(username=self.username, title="T3", checkbox=True, completed_at=now - timedelta(days=10))

        n1 = Note.objects.create(username=self.username, title="N1")
        Note.objects.filter(id=n1.id).update(created_at=now - timedelta(days=1))

        n2 = Note.objects.create(username=self.username, title="N2")
        Note.objects.filter(id=n2.id).update(created_at=now - timedelta(days=9))

        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.context["tasks_this_week"], 2)
        self.assertEqual(response.context["tasks_last_week"], 1)
        self.assertEqual(response.context["tasks_change"], 100)

        self.assertEqual(response.context["notes_this_week"], 1)
        self.assertEqual(response.context["notes_last_week"], 1)
        self.assertEqual(response.context["notes_change"], 0)

    def test_completion_rate_and_top_tasks(self):
        now = timezone.now()
        Todo.objects.create(username=self.username, title="T1", checkbox=True, completed_at=now)
        Todo.objects.create(username=self.username, title="T2", checkbox=True, completed_at=now)
        t_low = Todo.objects.create(username=self.username, title="T3", checkbox=False, priority=1)
        t_high = Todo.objects.create(username=self.username, title="T4", checkbox=False, priority=5)

        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.context["total_tasks"], 4)
        self.assertEqual(response.context["completion_rate"], 50)
        self.assertEqual(response.context["tasks_remaining"], 2)

        top_tasks = list(response.context["top_tasks"])
        self.assertEqual(top_tasks[0], t_high)
        self.assertEqual(top_tasks[1], t_low)

    def test_calendar_events_context(self):
        today = timezone.now().date()
        dummy_time = time(12, 0)

        CalendarEvent.objects.create(
            username=self.username, 
            title="E1", 
            date=today - timedelta(days=10), 
            time=dummy_time
        )
        CalendarEvent.objects.create(
            username=self.username, 
            title="E2", 
            date=today + timedelta(days=5), 
            time=dummy_time
        )

        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.context["events_done_last_month"], 1)
        self.assertEqual(response.context["events_upcoming"], 1)

    def test_chart_data_structure(self):
        response = self.client.get(self.dashboard_url)
        chart_data = json.loads(response.context["chart_data"])

        self.assertIn("labels", chart_data)
        self.assertEqual(len(chart_data["labels"]), 12)
        self.assertIn("tasks", chart_data)
        self.assertIn("notes", chart_data)
        self.assertIn("events", chart_data)
        self.assertEqual(len(chart_data["tasks"]), 12)