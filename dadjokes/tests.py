from django.test import TestCase

from .models import Joke, Picture


class DadJokesAPITests(TestCase):
    def setUp(self):
        self.joke = Joke.objects.create(
            text="Why don't eggs tell jokes? They'd crack each other up.",
            contributor="Test User",
        )
        self.picture = Picture.objects.create(
            image_url="https://example.com/joke.jpg",
            contributor="Picture User",
        )

    def test_api_root_returns_random_joke_json(self):
        response = self.client.get("/dadjokes/api/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(response.json()["id"], self.joke.pk)

    def test_api_jokes_returns_all_jokes(self):
        response = self.client.get("/dadjokes/api/jokes")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["text"], self.joke.text)

    def test_api_joke_detail_returns_one_joke(self):
        response = self.client.get(f"/dadjokes/api/joke/{self.joke.pk}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["contributor"], self.joke.contributor)

    def test_api_pictures_returns_all_pictures(self):
        response = self.client.get("/dadjokes/api/pictures")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["image_url"], self.picture.image_url)

    def test_api_random_picture_returns_one_picture(self):
        response = self.client.get("/dadjokes/api/random_picture")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], self.picture.pk)

    def test_api_jokes_post_creates_new_joke(self):
        response = self.client.post(
            "/dadjokes/api/jokes",
            {
                "text": "I used to play piano by ear, now I use my hands.",
                "contributor": "Poster",
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Joke.objects.count(), 2)
        self.assertEqual(Joke.objects.order_by("-id").first().contributor, "Poster")
