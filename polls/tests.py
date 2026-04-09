import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Choice, Question


def create_question(question_text, days):
    return Question.objects.create(
        question_text=question_text,
        pub_date=timezone.now() + datetime.timedelta(days=days),
    )


def create_question_with_choices(question_text, days, choice_texts=None):
    question = create_question(question_text, days)
    for choice_text in choice_texts or ["Option A", "Option B"]:
        Choice.objects.create(question=question, choice_text=choice_text)
    return question


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        future_question = create_question("Future question", 30)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        old_question = Question(
            question_text="Old question",
            pub_date=timezone.now() - datetime.timedelta(days=1, seconds=1),
        )
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        recent_question = Question(
            question_text="Recent question",
            pub_date=timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59),
        )
        self.assertIs(recent_question.was_published_recently(), True)


class QuestionIndexViewTests(TestCase):
    def test_root_url_redirects_to_polls_index(self):
        response = self.client.get("/")
        self.assertRedirects(response, reverse("polls:index"))

    def test_no_questions(self):
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls available yet.")
        self.assertEqual(list(response.context["latest_question_list"]), [])

    def test_past_question_is_displayed(self):
        question = create_question("Past question", -1)
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(list(response.context["latest_question_list"]), [question])

    def test_future_question_is_not_displayed(self):
        create_question("Future question", 2)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls available yet.")
        self.assertEqual(list(response.context["latest_question_list"]), [])

    def test_past_question_appears_before_older_questions(self):
        older_question = create_question("Older question", -30)
        newer_question = create_question("Newer question", -2)
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(
            list(response.context["latest_question_list"]),
            [newer_question, older_question],
        )


class QuestionDetailViewTests(TestCase):
    def test_future_question_returns_404(self):
        future_question = create_question_with_choices("Future question", 5)
        response = self.client.get(reverse("polls:detail", args=(future_question.id,)))
        self.assertEqual(response.status_code, 404)

    def test_past_question_is_displayed(self):
        past_question = create_question_with_choices("Past question", -2)
        response = self.client.get(reverse("polls:detail", args=(past_question.id,)))
        self.assertContains(response, past_question.question_text)


class ResultsViewTests(TestCase):
    def test_future_question_results_return_404(self):
        future_question = create_question_with_choices("Future results", 3)
        response = self.client.get(reverse("polls:results", args=(future_question.id,)))
        self.assertEqual(response.status_code, 404)

    def test_results_selector_hides_future_questions(self):
        visible_question = create_question("Visible question", -1)
        create_question("Hidden future question", 2)
        response = self.client.get(reverse("polls:results_select"))
        self.assertContains(response, visible_question.question_text)
        self.assertNotContains(response, "Hidden future question")

    def test_results_multi_filters_selected_questions(self):
        included_question = create_question_with_choices("Included question", -1)
        create_question_with_choices("Excluded question", -1)
        response = self.client.get(
            reverse("polls:results_multi"),
            {"question_ids": [included_question.id]},
        )
        self.assertEqual(list(response.context["questions"]), [included_question])


class VotingFlowTests(TestCase):
    def test_single_vote_increments_votes_and_shows_success_message(self):
        question = create_question_with_choices("Best option?", -1)
        choice = question.choice_set.first()

        response = self.client.post(
            reverse("polls:vote", args=(question.id,)),
            {"choice": choice.id},
            follow=True,
        )

        choice.refresh_from_db()
        self.assertEqual(choice.votes, 1)
        self.assertContains(response, "Your vote was submitted successfully.")

    def test_single_vote_without_choice_shows_error(self):
        question = create_question_with_choices("Pick one", -1)
        response = self.client.post(reverse("polls:vote", args=(question.id,)))
        self.assertContains(response, "Select an answer before submitting your vote.")
        self.assertEqual(question.choice_set.first().votes, 0)

    def test_single_vote_with_invalid_choice_shows_error(self):
        question = create_question_with_choices("Pick one", -1)
        response = self.client.post(
            reverse("polls:vote", args=(question.id,)),
            {"choice": 9999},
        )
        self.assertContains(response, "That answer is no longer available.")

    def test_multi_vote_requires_at_least_one_selection(self):
        create_question_with_choices("Question one", -1)
        response = self.client.post(reverse("polls:multi_vote"))
        self.assertContains(response, "Select at least one answer before submitting.")

    def test_multi_vote_submits_multiple_answers(self):
        question_one = create_question_with_choices("Question one", -1)
        question_two = create_question_with_choices("Question two", -1)
        choice_one = question_one.choice_set.first()
        choice_two = question_two.choice_set.first()

        response = self.client.post(
            reverse("polls:multi_vote"),
            {
                f"question_{question_one.id}": choice_one.id,
                f"question_{question_two.id}": choice_two.id,
            },
            follow=True,
        )

        choice_one.refresh_from_db()
        choice_two.refresh_from_db()
        self.assertEqual(choice_one.votes, 1)
        self.assertEqual(choice_two.votes, 1)
        self.assertContains(response, "2 responses submitted successfully.")
