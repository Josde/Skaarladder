from locust import HttpUser, task


class HelloWorldUser(HttpUser):
    @task
    def hello_world(self):
        self.client.get("")
        self.client.get("challenge/55")
        self.client.get("error")
