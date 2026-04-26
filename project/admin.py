from django.contrib import admin

from .models import Chore, Expense, ExpenseShare, Household, Message, MessageComment


@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "move_in_date", "get_member_count")
    search_fields = ("name", "address")
    filter_horizontal = ("members",)


class ExpenseShareInline(admin.TabularInline):
    model = ExpenseShare
    extra = 1


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("title", "household", "created_by", "amount", "expense_date", "category")
    list_filter = ("household", "category", "expense_date")
    search_fields = ("title", "notes", "created_by__username")
    inlines = [ExpenseShareInline]


@admin.register(Chore)
class ChoreAdmin(admin.ModelAdmin):
    list_display = ("title", "household", "assigned_to", "due_date", "status", "completed_at")
    list_filter = ("household", "status", "due_date", "completed_at")
    search_fields = ("title", "description", "assigned_to__username")


@admin.register(ExpenseShare)
class ExpenseShareAdmin(admin.ModelAdmin):
    list_display = ("expense", "user", "amount_owed", "paid_status", "paid_at")
    list_filter = ("paid_status", "paid_at", "expense__household")
    search_fields = ("expense__title", "user__username")


class MessageCommentInline(admin.TabularInline):
    model = MessageComment
    extra = 1


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("title", "household", "author", "created_at")
    list_filter = ("household", "created_at")
    search_fields = ("title", "body", "author__username")
    inlines = [MessageCommentInline]


@admin.register(MessageComment)
class MessageCommentAdmin(admin.ModelAdmin):
    list_display = ("message", "author", "created_at")
    list_filter = ("message__household", "created_at")
    search_fields = ("message__title", "body", "author__username")
