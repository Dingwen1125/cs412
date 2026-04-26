# File: models.py
# Author: Dingwen Yang(laoba@bu.edu), 4/19/2026
# Description: Define the data models for households, shared expenses, chores, expense shares, and messages in the project app.

from decimal import Decimal

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Household(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    move_in_date = models.DateField()
    members = models.ManyToManyField(User, related_name="roommate_households", blank=True)

    class Meta:
        ordering = ["name", "id"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("project_household_detail", kwargs={"pk": self.pk})

    def get_member_count(self):
        return self.members.count()


class Expense(models.Model):
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name="expenses")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_expenses")
    title = models.CharField(max_length=100)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    expense_date = models.DateField()
    category = models.CharField(max_length=100)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-expense_date", "-id"]

    def __str__(self):
        return f"{self.title} (${self.amount})"

    def get_absolute_url(self):
        return reverse("project_expense_detail", kwargs={"pk": self.pk})

    def get_total_shared_amount(self):
        return sum((share.amount_owed for share in self.shares.all()), Decimal("0.00"))

    def get_remaining_amount(self):
        return self.amount - self.get_total_shared_amount()


class Chore(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
    ]

    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name="chores")
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chores")
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["due_date", "id"]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def get_absolute_url(self):
        return reverse("project_chore_detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        if self.status == "completed" and self.completed_at is None:
            self.completed_at = timezone.now()
        elif self.status != "completed":
            self.completed_at = None
        super().save(*args, **kwargs)


class ExpenseShare(models.Model):
    PAID_STATUS_CHOICES = [
        ("unpaid", "Unpaid"),
        ("paid", "Paid"),
    ]

    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name="shares")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="expense_shares")
    amount_owed = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    paid_status = models.CharField(max_length=10, choices=PAID_STATUS_CHOICES, default="unpaid")
    paid_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["expense", "user"]
        unique_together = [("expense", "user")]

    def __str__(self):
        return f"{self.user.username} owes ${self.amount_owed} for {self.expense.title}"

    def get_absolute_url(self):
        return reverse("project_expense_share_detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        if self.paid_status == "paid" and self.paid_at is None:
            self.paid_at = timezone.now()
        elif self.paid_status != "paid":
            self.paid_at = None
        super().save(*args, **kwargs)


class Message(models.Model):
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name="messages")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="roommate_messages")
    title = models.CharField(max_length=100)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("project_message_detail", kwargs={"pk": self.pk})


class MessageComment(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="roommate_message_comments")
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self):
        return f"Comment by {self.author.username} on {self.message.title}"
