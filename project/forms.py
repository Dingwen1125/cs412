# File: forms.py
# Author: Dingwen Yang(laoba@bu.edu), 4/19/2026
# Description: Define forms for user registration, household membership, expense creation and splitting, chores, and messages in the project app.

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Chore, Expense, ExpenseShare, Household, Message, MessageComment


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "email", "first_name", "last_name", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user


class HouseholdForm(forms.ModelForm):
    class Meta:
        model = Household
        fields = ["name", "address", "move_in_date"]
        widgets = {
            "move_in_date": forms.DateInput(attrs={"type": "date"}),
        }


class ExpenseForm(forms.ModelForm):
    include_self = forms.BooleanField(
        required=False,
        initial=True,
        label="I should pay part of this expense",
    )
    share_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select other household members who should split this expense.",
        label="Other roommates who owe part of this expense",
    )

    class Meta:
        model = Expense
        fields = ["household", "title", "amount", "expense_date", "category", "notes", "include_self", "share_users"]
        widgets = {
            "expense_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        self.user = user
        super().__init__(*args, **kwargs)
        allowed_households = Household.objects.all()
        if user is not None:
            allowed_households = Household.objects.filter(members=user)
        self.fields["household"].queryset = allowed_households

        selected_household = None
        household_id = self.data.get("household") or self.initial.get("household")
        if household_id:
            selected_household = allowed_households.filter(pk=household_id).first()
        elif user is not None:
            selected_household = allowed_households.first()

        if selected_household is not None:
            share_user_queryset = selected_household.members.all()
            if user is not None:
                share_user_queryset = share_user_queryset.exclude(pk=user.pk)
            self.fields["share_users"].queryset = share_user_queryset
            self.initial.setdefault("household", selected_household.pk)
        else:
            self.fields["share_users"].queryset = User.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        household = cleaned_data.get("household")
        include_self = cleaned_data.get("include_self")
        share_users = cleaned_data.get("share_users")

        if not household:
            return cleaned_data

        valid_users = household.members.all()
        valid_share_users = valid_users
        if self.user is not None:
            valid_share_users = valid_share_users.exclude(pk=self.user.pk)
        self.fields["share_users"].queryset = valid_share_users

        if not include_self and not share_users:
            raise ValidationError("Select at least one roommate who should pay part of this expense.")

        if include_self and self.user is not None and not valid_users.filter(pk=self.user.pk).exists():
            raise ValidationError("You must be a member of this household to include yourself in the split.")

        valid_user_ids = set(valid_share_users.values_list("id", flat=True))
        invalid_users = [user.username for user in share_users if user.id not in valid_user_ids]
        if invalid_users:
            raise ValidationError(
                f"These users are not valid roommates for this split: {', '.join(invalid_users)}."
            )

        return cleaned_data


class ExpenseShareForm(forms.ModelForm):
    class Meta:
        model = ExpenseShare
        fields = ["user", "amount_owed", "paid_status"]

    def __init__(self, *args, **kwargs):
        expense = kwargs.pop("expense", None)
        super().__init__(*args, **kwargs)
        if expense is not None:
            self.fields["user"].queryset = expense.household.members.exclude(pk=expense.created_by_id)


class ChoreForm(forms.ModelForm):
    class Meta:
        model = Chore
        fields = ["household", "assigned_to", "title", "description", "due_date", "status"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        allowed_households = Household.objects.all()
        if user is not None:
            allowed_households = Household.objects.filter(members=user)
        self.fields["household"].queryset = allowed_households

        selected_household = None
        household_id = self.data.get("household") or self.initial.get("household")
        if household_id:
            selected_household = allowed_households.filter(pk=household_id).first()
        elif user is not None:
            selected_household = allowed_households.first()

        if selected_household is not None:
            self.fields["assigned_to"].queryset = selected_household.members.all().order_by("username")
            self.initial.setdefault("household", selected_household.pk)
        else:
            self.fields["assigned_to"].queryset = User.objects.none()


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["title", "body"]


class MessageCommentForm(forms.ModelForm):
    class Meta:
        model = MessageComment
        fields = ["body"]
        labels = {
            "body": "Comment",
        }
