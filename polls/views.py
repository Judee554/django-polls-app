from django.contrib import messages
from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic, View

from .models import Choice, Question


def published_questions():
    return Question.objects.filter(pub_date__lte=timezone.now())


def add_question_navigation(context, question):
    questions = published_questions()
    current_pk = question.pk
    context["next_question"] = questions.filter(pk__gt=current_pk).order_by("pk").first()
    context["prev_question"] = questions.filter(pk__lt=current_pk).order_by("-pk").first()
    return context


def build_question_cards(questions):
    cards = []
    for question in questions:
        choices = list(question.choice_set.all())
        total_votes = sum(choice.votes for choice in choices)
        choice_rows = []

        for choice in choices:
            percentage = 0 if total_votes == 0 else round((choice.votes / total_votes) * 100)
            choice_rows.append(
                {
                    "choice": choice,
                    "percentage": percentage,
                }
            )

        leading_choice = max(choices, key=lambda choice: choice.votes, default=None)
        cards.append(
            {
                "question": question,
                "choices": choice_rows,
                "total_votes": total_votes,
                "choice_count": len(choices),
                "leading_choice": leading_choice,
            }
        )

    return cards


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        return published_questions().prefetch_related("choice_set").order_by("-pub_date")[:5]


class DetailView(generic.DetailView):
    template_name = "polls/detail.html"

    def get_queryset(self):
        return published_questions().prefetch_related("choice_set")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return add_question_navigation(context, self.object)


class ResultsView(generic.DetailView):
    template_name = "polls/results.html"

    def get_queryset(self):
        return published_questions().prefetch_related("choice_set")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["questions"] = [self.object]
        context["question_cards"] = build_question_cards([self.object])
        context["all_questions"] = published_questions().order_by("pk")
        return add_question_navigation(context, self.object)


class ResultsSelectView(generic.ListView):
    template_name = "polls/results_select.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        return published_questions().prefetch_related("choice_set").order_by("-pub_date")


class ResultsMultiView(View):
    template_name = "polls/results.html"

    def get(self, request):
        ids = request.GET.getlist("question_ids")
        questions = published_questions().order_by("pk").prefetch_related("choice_set")
        if ids:
            questions = questions.filter(id__in=ids)

        context = {
            "questions": questions,
            "question_cards": build_question_cards(questions),
            "all_questions": published_questions().order_by("pk"),
        }
        return render(request, self.template_name, context)


class MultiVoteView(View):
    template_name = "polls/multi_vote.html"

    def get(self, request):
        questions = published_questions().order_by("pk").prefetch_related("choice_set")
        return render(request, self.template_name, {"questions": questions})

    def post(self, request):
        questions = list(published_questions().order_by("pk"))
        submitted_votes = 0

        for question in questions:
            choice_id = request.POST.get(f"question_{question.id}")
            if not choice_id:
                continue

            try:
                choice = question.choice_set.get(pk=choice_id)
            except Choice.DoesNotExist:
                return render(
                    request,
                    self.template_name,
                    {
                        "questions": published_questions().order_by("pk").prefetch_related("choice_set"),
                        "error_message": "One of the selected answers is invalid. Please review your choices and try again.",
                    },
                )

            choice.votes = F("votes") + 1
            choice.save(update_fields=["votes"])
            submitted_votes += 1

        if submitted_votes == 0:
            return render(
                request,
                self.template_name,
                {
                    "questions": published_questions().order_by("pk").prefetch_related("choice_set"),
                    "error_message": "Select at least one answer before submitting.",
                },
            )

        messages.success(
            request,
            f"{submitted_votes} response{'s' if submitted_votes != 1 else ''} submitted successfully.",
        )
        return HttpResponseRedirect(reverse("polls:results_multi"))


def vote(request, question_id):
    question = get_object_or_404(
        published_questions().prefetch_related("choice_set"),
        pk=question_id,
    )
    selected_choice_id = request.POST.get("choice")

    if not selected_choice_id:
        context = {
            "question": question,
            "error_message": "Select an answer before submitting your vote.",
        }
        context = add_question_navigation(context, question)
        return render(request, "polls/detail.html", context)

    try:
        selected_choice = question.choice_set.get(pk=selected_choice_id)
    except Choice.DoesNotExist:
        context = {
            "question": question,
            "error_message": "That answer is no longer available. Please choose another option.",
        }
        context = add_question_navigation(context, question)
        return render(request, "polls/detail.html", context)

    selected_choice.votes = F("votes") + 1
    selected_choice.save(update_fields=["votes"])

    messages.success(request, "Your vote was submitted successfully.")
    return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
