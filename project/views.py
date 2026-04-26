"""Define views for the roommate manager project app."""

from decimal import Decimal, ROUND_DOWN
from datetime import timedelta

from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, TemplateView, View

from .forms import (
    ChoreForm,
    ExpenseForm,
    ExpenseShareForm,
    HouseholdForm,
    MessageCommentForm,
    MessageForm,
    UserRegistrationForm,
)
from .models import Chore, Expense, ExpenseShare, Household, Message


def get_user_household(user):
    """Return the first household joined by the user."""
    if not user.is_authenticated:
        return None
    return Household.objects.filter(members=user).first()


def cleanup_completed_records():
    """Delete paid expense shares and completed chores older than seven days."""
    cutoff = timezone.now() - timedelta(days=7)
    ExpenseShare.objects.filter(paid_status="paid", paid_at__lte=cutoff).delete()
    Chore.objects.filter(status="completed", completed_at__lte=cutoff).delete()


class ProjectHomeView(TemplateView):
    """Display the project dashboard."""

    template_name = "project/home.html"

    def dispatch(self, request, *args, **kwargs):
        """Clean old completed records before showing the home page."""
        cleanup_completed_records()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Add dashboard counts to the template context."""
        context = super().get_context_data(**kwargs)
        context["expense_count"] = Expense.objects.count()
        context["chore_count"] = Chore.objects.count()
        context["message_count"] = Message.objects.count()
        return context


@method_decorator(never_cache, name="dispatch")
@method_decorator(ensure_csrf_cookie, name="dispatch")
class ProjectLoginView(LoginView):
    """Display the project login page."""

    template_name = "project/login.html"
    redirect_authenticated_user = True
    next_page = reverse_lazy("project_home")


class ProjectLogoutView(LogoutView):
    """Log out the current user and return to the project home page."""

    next_page = reverse_lazy("project_home")


class HouseholdListView(ListView):
    """Display all households."""

    model = Household
    template_name = "project/household_list.html"
    context_object_name = "households"


class HouseholdDetailView(DetailView):
    """Display one household."""

    model = Household
    template_name = "project/household_detail.html"
    context_object_name = "household"


class ExpenseListView(LoginRequiredMixin, ListView):
    """Display expenses for the user's current household."""

    model = Expense
    template_name = "project/expense_list.html"
    context_object_name = "expenses"

    def get_queryset(self):
        """Return expenses that belong to the user's current household."""
        cleanup_completed_records()
        household = get_user_household(self.request.user)
        if household is None:
            return Expense.objects.none()
        return Expense.objects.filter(household=household).annotate(share_count=Count("shares"))


class ExpenseDetailView(DetailView):
    """Display one expense in the user's current household."""

    model = Expense
    template_name = "project/expense_detail.html"
    context_object_name = "expense"

    def dispatch(self, request, *args, **kwargs):
        """Clean old completed records before showing an expense."""
        cleanup_completed_records()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """Return expenses that belong to the user's current household."""
        household = get_user_household(self.request.user)
        if household is None:
            return Expense.objects.none()
        return Expense.objects.filter(household=household)

    def get_context_data(self, **kwargs):
        """Add share totals and the share form to the template context."""
        context = super().get_context_data(**kwargs)
        context["share_form"] = kwargs.get("share_form", ExpenseShareForm(expense=self.object))
        context["total_shared"] = self.object.get_total_shared_amount()
        context["remaining_amount"] = self.object.get_remaining_amount()
        return context


class ChoreListView(ListView):
    """Display chores for the user's current household."""

    model = Chore
    template_name = "project/chore_list.html"
    context_object_name = "chores"

    def get_queryset(self):
        """Return chores that belong to the user's current household."""
        cleanup_completed_records()
        household = get_user_household(self.request.user)
        if household is None:
            return Chore.objects.none()
        return Chore.objects.filter(household=household)


class ChoreDetailView(DetailView):
    """Display one chore in the user's current household."""

    model = Chore
    template_name = "project/chore_detail.html"
    context_object_name = "chore"

    def dispatch(self, request, *args, **kwargs):
        """Clean old completed records before showing a chore."""
        cleanup_completed_records()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """Return chores that belong to the user's current household."""
        household = get_user_household(self.request.user)
        if household is None:
            return Chore.objects.none()
        return Chore.objects.filter(household=household)


class ExpenseShareDetailView(DetailView):
    """Display one expense share owed by the current user."""

    model = ExpenseShare
    template_name = "project/expense_share_detail.html"
    context_object_name = "share"

    def get_queryset(self):
        """Return expense shares assigned to the current user."""
        if self.request.user.is_authenticated:
            return ExpenseShare.objects.filter(user=self.request.user)
        return ExpenseShare.objects.none()


class MarkExpenseSharePaidView(LoginRequiredMixin, View):
    """Mark an expense share as paid."""

    def post(self, request, pk):
        """Set the selected expense share to paid."""
        share = get_object_or_404(ExpenseShare, pk=pk, user=request.user)
        share.paid_status = "paid"
        share.save()

        next_url = request.POST.get("next")
        if next_url:
            return redirect(next_url)
        return redirect("project_expense_share_detail", pk=share.pk)


class MyExpenseShareListView(LoginRequiredMixin, ListView):
    """Display expense shares owed by the current user."""

    model = ExpenseShare
    template_name = "project/my_expense_shares.html"
    context_object_name = "shares"

    def get_queryset(self):
        """Return expense shares where the current user owes someone else."""
        cleanup_completed_records()
        return ExpenseShare.objects.filter(user=self.request.user).exclude(expense__created_by=self.request.user).select_related(
            "expense",
            "expense__created_by",
            "expense__household",
        ).order_by("paid_status", "-expense__expense_date", "-id")

    def get_context_data(self, **kwargs):
        """Add the unpaid total to the template context."""
        context = super().get_context_data(**kwargs)
        unpaid_shares = [share for share in context["shares"] if share.paid_status == "unpaid"]
        context["unpaid_total"] = sum((share.amount_owed for share in unpaid_shares), Decimal("0.00"))
        return context


class WhoOwesMeListView(LoginRequiredMixin, ListView):
    """Display unpaid expense shares owed to the current user."""

    model = ExpenseShare
    template_name = "project/who_owes_me.html"
    context_object_name = "shares"

    def get_queryset(self):
        """Return unpaid expense shares from expenses created by the current user."""
        cleanup_completed_records()
        return ExpenseShare.objects.filter(
            expense__created_by=self.request.user,
            paid_status="unpaid",
        ).exclude(user=self.request.user).select_related(
            "user",
            "expense",
            "expense__household",
        ).order_by("paid_status", "-expense__expense_date", "-id")

    def get_context_data(self, **kwargs):
        """Add the unpaid total to the template context."""
        context = super().get_context_data(**kwargs)
        unpaid_shares = [share for share in context["shares"] if share.paid_status == "unpaid"]
        context["unpaid_total"] = sum((share.amount_owed for share in unpaid_shares), Decimal("0.00"))
        return context


class ExpenseShareCreateView(LoginRequiredMixin, View):
    """Create an expense share for an expense in the user's current household."""

    def post(self, request, pk):
        """Save a new expense share for the selected expense."""
        expense = get_object_or_404(Expense, pk=pk, household__members=request.user)
        form = ExpenseShareForm(request.POST, expense=expense)
        if form.is_valid():
            share = form.save(commit=False)
            share.expense = expense
            share.save()
            return redirect(expense.get_absolute_url())

        context = {
            "expense": expense,
            "share_form": form,
            "total_shared": expense.get_total_shared_amount(),
            "remaining_amount": expense.get_remaining_amount(),
        }
        return self.render_to_response(context)

    def render_to_response(self, context):
        """Render the expense detail page with form errors."""
        return render(self.request, "project/expense_detail.html", context)


@method_decorator(never_cache, name="dispatch")
@method_decorator(ensure_csrf_cookie, name="dispatch")
class RegisterUserView(CreateView):
    """Create a new user account."""

    form_class = UserRegistrationForm
    template_name = "project/form.html"

    def dispatch(self, request, *args, **kwargs):
        """Redirect authenticated users away from registration."""
        if request.user.is_authenticated:
            return redirect("project_home")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Add registration page labels to the template context."""
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Create Account"
        context["submit_label"] = "Create Account"
        return context

    def form_valid(self, form):
        """Save and log in the new user."""
        user = form.save()
        login(self.request, user, backend="django.contrib.auth.backends.ModelBackend")
        return redirect("project_home")


class HouseholdCreateView(LoginRequiredMixin, CreateView):
    """Create a household and add the current user to it."""

    model = Household
    form_class = HouseholdForm
    template_name = "project/form.html"

    def get_context_data(self, **kwargs):
        """Add household creation labels to the template context."""
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Create Household"
        context["submit_label"] = "Create Household"
        return context

    def form_valid(self, form):
        """Save the household and add the current user as a member."""
        response = super().form_valid(form)
        self.object.members.add(self.request.user)
        return response


class JoinHouseholdView(LoginRequiredMixin, TemplateView):
    """Search for and join a household."""

    template_name = "project/join_household.html"

    def get_context_data(self, **kwargs):
        """Add household search results to the template context."""
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get("q", "").strip()
        context["page_title"] = "Join Household"
        context["search_query"] = search_query
        context["search_results"] = self.get_search_results(search_query)
        return context

    def get_search_results(self, search_query):
        """Return households matching the search query by name or address."""
        if not search_query:
            return Household.objects.none()
        return Household.objects.filter(
            Q(name__icontains=search_query) | Q(address__icontains=search_query)
        )

    def post(self, request, *args, **kwargs):
        """Move the current user into the selected household."""
        selected_household = get_object_or_404(Household, pk=request.POST.get("household_id"))
        for household in Household.objects.filter(members=self.request.user).exclude(pk=selected_household.pk):
            household.members.remove(self.request.user)
        selected_household.members.add(self.request.user)
        return redirect("project_home")


class ExpenseCreateView(LoginRequiredMixin, CreateView):
    """Create an expense and split it among selected household members."""

    model = Expense
    form_class = ExpenseForm
    template_name = "project/form.html"

    def get_form_kwargs(self):
        """Pass the current user into the expense form."""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        """Add expense creation labels to the template context."""
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Record Expense"
        context["submit_label"] = "Save Expense"
        context["form_note"] = "Choose whether you are included, then select any other roommates who should split this expense."
        return context

    def form_valid(self, form):
        """Save the expense and create shares for selected users."""
        share_users = list(form.cleaned_data["share_users"])
        if form.cleaned_data["include_self"]:
            share_users.insert(0, self.request.user)
        form.instance.created_by = self.request.user
        self.object = form.save()
        self.create_expense_shares(share_users)
        return redirect(self.object.get_absolute_url())

    def create_expense_shares(self, share_users):
        """Create expense shares by evenly splitting the expense amount."""
        total_amount = self.object.amount
        member_count = len(share_users)
        if member_count == 0:
            return

        share_amount = (total_amount / member_count).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
        assigned_total = share_amount * member_count
        remainder = total_amount - assigned_total

        for index, user_obj in enumerate(share_users):
            amount_owed = share_amount
            if index == member_count - 1:
                amount_owed += remainder
            if user_obj == self.object.created_by:
                continue
            ExpenseShare.objects.create(
                expense=self.object,
                user=user_obj,
                amount_owed=amount_owed,
            )


class ChoreCreateView(LoginRequiredMixin, CreateView):
    """Create a chore for the current household."""

    model = Chore
    form_class = ChoreForm
    template_name = "project/form.html"

    def get_form_kwargs(self):
        """Pass the current user into the chore form."""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        """Add chore creation labels to the template context."""
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Assign Chore"
        context["submit_label"] = "Save Chore"
        return context


class MarkChoreCompletedView(LoginRequiredMixin, View):
    """Mark a chore as completed."""

    def post(self, request, pk):
        """Set the chore to completed when assigned to the current user."""
        chore = get_object_or_404(Chore, pk=pk)
        if chore.assigned_to_id == request.user.id:
            chore.status = "completed"
            chore.save()
        return redirect(chore.get_absolute_url())


class MessageListView(LoginRequiredMixin, ListView):
    """Display messages for the user's current household."""

    model = Message
    template_name = "project/message_list.html"
    context_object_name = "messages"

    def get_queryset(self):
        """Return messages for the user's current household."""
        household = get_user_household(self.request.user)
        if household is None:
            return Message.objects.none()
        return Message.objects.filter(household=household).select_related("author", "household")

    def get_context_data(self, **kwargs):
        """Add the current household to the template context."""
        context = super().get_context_data(**kwargs)
        context["household"] = get_user_household(self.request.user)
        return context


class MessageCreateView(LoginRequiredMixin, CreateView):
    """Create a message for the user's current household."""

    model = Message
    form_class = MessageForm
    template_name = "project/form.html"

    def dispatch(self, request, *args, **kwargs):
        """Redirect users without a household to the join page."""
        if get_user_household(request.user) is None:
            return redirect("project_join_household")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Add message creation labels to the template context."""
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Post Message"
        context["submit_label"] = "Post Message"
        return context

    def form_valid(self, form):
        """Save the message for the current household."""
        form.instance.author = self.request.user
        form.instance.household = get_user_household(self.request.user)
        return super().form_valid(form)


class MessageDetailView(LoginRequiredMixin, DetailView):
    """Display one household message and its comments."""

    model = Message
    template_name = "project/message_detail.html"
    context_object_name = "message"

    def get_queryset(self):
        """Return messages visible to the current household member."""
        return Message.objects.filter(household__members=self.request.user).select_related(
            "author",
            "household",
        ).prefetch_related("comments__author")

    def get_context_data(self, **kwargs):
        """Add the comment form to the template context."""
        context = super().get_context_data(**kwargs)
        context["comment_form"] = MessageCommentForm()
        return context


class MessageCommentCreateView(LoginRequiredMixin, View):
    """Create a comment on a household message."""

    def post(self, request, pk):
        """Save a comment for a message visible to the current user."""
        message = get_object_or_404(Message, pk=pk, household__members=request.user)
        form = MessageCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.message = message
            comment.author = request.user
            comment.save()
            return redirect(message.get_absolute_url())

        return render(
            request,
            "project/message_detail.html",
            {
                "message": message,
                "comment_form": form,
            },
        )
