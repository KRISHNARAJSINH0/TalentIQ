import time
from locust import HttpUser, task, between


class ResumeAILoadUser(HttpUser):
    """
    Simulates production candidate actions to benchmark application latency and system load.
    """
    wait_time = between(1, 3)

    def on_start(self):
        """Simulates candidate authentication and token acquisition."""
        self.auth_headers = {}
        # Pre-authenticate or login user
        with self.client.post("/api/auth/login/", json={
            "username": "candidate1",
            "password": "password123"
        }, catch_response=True) as response:
            if response.status_code == 200:
                tokens = response.json()
                access_token = tokens.get("access")
                self.auth_headers = {"Authorization": f"Bearer {access_token}"}
            else:
                # Use fallback guest state if credentials not preset
                response.success()

    @task(3)
    def view_resumes(self):
        """Browse uploaded resumes."""
        self.client.get("/api/resumes/", headers=self.auth_headers)

    @task(2)
    def view_ats_dashboard(self):
        """Browse ATS reports and recommendations list."""
        self.client.get("/api/ats/", headers=self.auth_headers)

    @task(2)
    def get_notifications(self):
        """Poll user notifications."""
        self.client.get("/api/notifications/unread/", headers=self.auth_headers)

    @task(1)
    def view_portfolio_profile(self):
        """Simulates public user traffic viewing the portfolio pages."""
        # Browse public/authorized portfolio link
        self.client.get("/api/portfolio/", headers=self.auth_headers)
