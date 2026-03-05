from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic, View

from .models import Choice, Question

# Index page: list latest 5 questions
class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        return Question.objects.order_by("-pub_date")[:5]

# Detail page: show question + prev/next navigation
class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_pk = self.object.pk
        context['next_question'] = Question.objects.filter(pk__gt=current_pk).order_by('pk').first()
        context['prev_question'] = Question.objects.filter(pk__lt=current_pk).order_by('-pk').first()
        return context

# Single question results page with navigation and link to full results
class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Wrap the single question in a list for the template loop
        context['questions'] = [self.object]
        # Navigation to adjacent results pages
        current_pk = self.object.pk
        context['next_question'] = Question.objects.filter(pk__gt=current_pk).order_by('pk').first()
        context['prev_question'] = Question.objects.filter(pk__lt=current_pk).order_by('-pk').first()
        # All questions for the "jump to any question" list
        context['all_questions'] = Question.objects.order_by('pk')
        return context

# Multi-question results page
class ResultsMultiView(View):
    template_name = "polls/results.html"

    def get(self, request):
        ids = request.GET.getlist("question_ids")
        if ids:
            questions = Question.objects.filter(id__in=ids)
        else:
            questions = Question.objects.all()
        return render(request, self.template_name, {"questions": questions})

# Multi-question vote page
class MultiVoteView(View):
    template_name = "polls/multi_vote.html"

    def get(self, request):
        questions = Question.objects.order_by('pk')  # Show all questions
        return render(request, self.template_name, {"questions": questions})

    def post(self, request):
        questions = Question.objects.all()
        for question in questions:
            choice_id = request.POST.get(f"question_{question.id}")
            if choice_id:
                choice = get_object_or_404(Choice, pk=choice_id, question=question)
                choice.votes = F("votes") + 1
                choice.save()
        return HttpResponseRedirect(reverse("polls:results_multi"))

# Voting for a single question
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))