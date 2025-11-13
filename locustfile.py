# locustfile.py
from locust import HttpUser, task, between

class FileAPIUser(HttpUser):
    wait_time = between(1, 2)

    @task(3)
    def health(self):
        self.client.get("/health")

    @task(2)
    def list_files(self):
        self.client.get("/files")
    