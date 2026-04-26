from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import ChoreForm, ExpenseForm, ExpenseShareForm
from .models import Chore, Expense, ExpenseShare, Household, HouseholdJoinRequest, Message, MessageComment


class MessagePermissionTests(TestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(username="alice", password="password123")
        self.user_b = User.objects.create_user(username="bob", password="password123")

        self.household_a = Household.objects.create(
            name="Apartment A",
            address="1 A St",
            move_in_date="2026-01-01",
        )
        self.household_b = Household.objects.create(
            name="Apartment B",
            address="2 B St",
            move_in_date="2026-01-01",
        )
        self.household_a.members.add(self.user_a)
        self.household_b.members.add(self.user_b)

        self.message_a = Message.objects.create(
            household=self.household_a,
            author=self.user_a,
            title="A message",
            body="For apartment A only.",
        )
        self.message_b = Message.objects.create(
            household=self.household_b,
            author=self.user_b,
            title="B message",
            body="For apartment B only.",
        )

    def test_user_only_sees_own_household_messages(self):
        self.client.login(username="alice", password="password123")
        response = self.client.get(reverse("project_message_list"))

        self.assertContains(response, "A message")
        self.assertContains(response, "For apartment A only.")
        self.assertNotContains(response, "B message")
        self.assertNotContains(response, "<th>Posted</th>", html=True)
        self.assertNotContains(response, "<th>Comments</th>", html=True)

    def test_user_cannot_view_other_household_message_detail(self):
        self.client.login(username="alice", password="password123")
        response = self.client.get(reverse("project_message_detail", kwargs={"pk": self.message_b.pk}))

        self.assertEqual(response.status_code, 404)

    def test_user_can_comment_on_own_household_message(self):
        self.client.login(username="alice", password="password123")
        response = self.client.post(
            reverse("project_message_comment_create", kwargs={"pk": self.message_a.pk}),
            {"body": "I can help with this."},
        )

        self.assertRedirects(response, self.message_a.get_absolute_url())
        self.assertTrue(
            MessageComment.objects.filter(
                message=self.message_a,
                author=self.user_a,
                body="I can help with this.",
            ).exists()
        )

    def test_user_cannot_comment_on_other_household_message(self):
        self.client.login(username="alice", password="password123")
        response = self.client.post(
            reverse("project_message_comment_create", kwargs={"pk": self.message_b.pk}),
            {"body": "I should not be here."},
        )

        self.assertEqual(response.status_code, 404)
        self.assertFalse(MessageComment.objects.filter(message=self.message_b).exists())


class CompletedRecordCleanupTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="password123")
        self.household = Household.objects.create(
            name="Apartment A",
            address="1 A St",
            move_in_date="2026-01-01",
        )
        self.household.members.add(self.user)
        self.expense = Expense.objects.create(
            household=self.household,
            created_by=self.user,
            title="Groceries",
            amount=Decimal("20.00"),
            expense_date="2026-01-02",
            category="Food",
        )

    def test_paid_expense_share_is_deleted_after_one_week(self):
        share = ExpenseShare.objects.create(
            expense=self.expense,
            user=self.user,
            amount_owed=Decimal("20.00"),
            paid_status="paid",
        )
        ExpenseShare.objects.filter(pk=share.pk).update(paid_at=timezone.now() - timedelta(days=8))

        self.client.login(username="alice", password="password123")
        self.client.get(reverse("project_my_expense_shares"))

        self.assertFalse(ExpenseShare.objects.filter(pk=share.pk).exists())

    def test_recent_paid_expense_share_is_kept(self):
        share = ExpenseShare.objects.create(
            expense=self.expense,
            user=self.user,
            amount_owed=Decimal("20.00"),
            paid_status="paid",
        )
        ExpenseShare.objects.filter(pk=share.pk).update(paid_at=timezone.now() - timedelta(days=6))

        self.client.login(username="alice", password="password123")
        self.client.get(reverse("project_my_expense_shares"))

        self.assertTrue(ExpenseShare.objects.filter(pk=share.pk).exists())

    def test_completed_chore_is_deleted_after_one_week(self):
        chore = Chore.objects.create(
            household=self.household,
            assigned_to=self.user,
            title="Vacuum",
            due_date="2026-01-03",
            status="completed",
        )
        Chore.objects.filter(pk=chore.pk).update(completed_at=timezone.now() - timedelta(days=8))

        self.client.login(username="alice", password="password123")
        self.client.get(reverse("project_chore_list"))

        self.assertFalse(Chore.objects.filter(pk=chore.pk).exists())

    def test_recent_completed_chore_is_kept(self):
        chore = Chore.objects.create(
            household=self.household,
            assigned_to=self.user,
            title="Dishes",
            due_date="2026-01-03",
            status="completed",
        )
        Chore.objects.filter(pk=chore.pk).update(completed_at=timezone.now() - timedelta(days=6))

        self.client.login(username="alice", password="password123")
        self.client.get(reverse("project_chore_list"))

        self.assertTrue(Chore.objects.filter(pk=chore.pk).exists())


class ExpenseSplitFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="password123")
        self.roommate = User.objects.create_user(username="bob", password="password123")
        self.household = Household.objects.create(
            name="Apartment A",
            address="1 A St",
            move_in_date="2026-01-01",
        )
        self.household.members.add(self.user, self.roommate)

    def test_share_users_excludes_current_user(self):
        form = ExpenseForm(user=self.user, initial={"household": self.household.pk})

        self.assertNotIn(self.user, form.fields["share_users"].queryset)
        self.assertIn(self.roommate, form.fields["share_users"].queryset)

    def test_expense_split_can_include_current_user_separately(self):
        self.client.login(username="alice", password="password123")
        response = self.client.post(
            reverse("project_expense_create"),
            {
                "household": self.household.pk,
                "title": "Dinner",
                "amount": "30.00",
                "expense_date": "2026-01-04",
                "category": "Food",
                "notes": "",
                "include_self": "on",
                "share_users": [self.roommate.pk],
            },
        )

        expense = Expense.objects.get(title="Dinner")
        self.assertRedirects(response, expense.get_absolute_url())
        self.assertEqual(expense.shares.count(), 1)
        self.assertFalse(expense.shares.filter(user=self.user).exists())
        self.assertTrue(expense.shares.filter(user=self.roommate, amount_owed=Decimal("15.00")).exists())

    def test_expense_split_can_exclude_current_user(self):
        self.client.login(username="alice", password="password123")
        response = self.client.post(
            reverse("project_expense_create"),
            {
                "household": self.household.pk,
                "title": "Supplies",
                "amount": "12.00",
                "expense_date": "2026-01-04",
                "category": "Home",
                "notes": "",
                "share_users": [self.roommate.pk],
            },
        )

        expense = Expense.objects.get(title="Supplies")
        self.assertRedirects(response, expense.get_absolute_url())
        self.assertEqual(expense.shares.count(), 1)
        self.assertFalse(expense.shares.filter(user=self.user).exists())
        self.assertTrue(expense.shares.filter(user=self.roommate, amount_owed=Decimal("12.00")).exists())

    def test_expense_share_form_excludes_expense_creator(self):
        expense = Expense.objects.create(
            household=self.household,
            created_by=self.user,
            title="Utilities",
            amount=Decimal("50.00"),
            expense_date="2026-01-04",
            category="Bills",
        )

        form = ExpenseShareForm(expense=expense)

        self.assertNotIn(self.user, form.fields["user"].queryset)
        self.assertIn(self.roommate, form.fields["user"].queryset)

    def test_what_i_owe_hides_existing_self_owed_share(self):
        expense = Expense.objects.create(
            household=self.household,
            created_by=self.user,
            title="Old self share",
            amount=Decimal("10.00"),
            expense_date="2026-01-04",
            category="Other",
        )
        ExpenseShare.objects.create(
            expense=expense,
            user=self.user,
            amount_owed=Decimal("10.00"),
        )

        self.client.login(username="alice", password="password123")
        response = self.client.get(reverse("project_my_expense_shares"))

        self.assertNotContains(response, "Old self share")

    def test_who_owes_me_shows_roommates_who_owe_current_user(self):
        my_expense = Expense.objects.create(
            household=self.household,
            created_by=self.user,
            title="Shared dinner",
            amount=Decimal("30.00"),
            expense_date="2026-01-04",
            category="Food",
        )
        paid_expense = Expense.objects.create(
            household=self.household,
            created_by=self.user,
            title="Paid dinner",
            amount=Decimal("30.00"),
            expense_date="2026-01-04",
            category="Food",
        )
        roommate_expense = Expense.objects.create(
            household=self.household,
            created_by=self.roommate,
            title="Roommate bill",
            amount=Decimal("20.00"),
            expense_date="2026-01-04",
            category="Bills",
        )
        paid_share = ExpenseShare.objects.create(
            expense=paid_expense,
            user=self.roommate,
            amount_owed=Decimal("15.00"),
            paid_status="paid",
        )
        unpaid_share = ExpenseShare.objects.create(
            expense=my_expense,
            user=self.roommate,
            amount_owed=Decimal("8.00"),
        )
        ExpenseShare.objects.create(
            expense=roommate_expense,
            user=self.user,
            amount_owed=Decimal("10.00"),
        )
        ExpenseShare.objects.create(
            expense=my_expense,
            user=self.user,
            amount_owed=Decimal("15.00"),
        )

        self.client.login(username="alice", password="password123")
        response = self.client.get(reverse("project_who_owes_me"))

        self.assertContains(response, "Shared dinner")
        self.assertContains(response, "bob")
        self.assertContains(response, "$8.00")
        self.assertNotContains(response, "$15.00")
        self.assertNotContains(response, "Roommate bill")
        self.assertNotContains(response, "<th>Household</th>", html=True)
        self.assertNotContains(response, "<th>Status</th>", html=True)
        self.assertFalse(any(share.user == self.user for share in response.context["shares"]))
        self.assertNotIn(paid_share, response.context["shares"])
        self.assertIn(unpaid_share, response.context["shares"])


class HouseholdSwitchVisibilityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="password123")
        self.roommate = User.objects.create_user(username="bob", password="password123")
        self.old_household = Household.objects.create(
            name="Old Apartment",
            address="1 Old St",
            move_in_date="2026-01-01",
        )
        self.current_household = Household.objects.create(
            name="Current Apartment",
            address="2 Current St",
            move_in_date="2026-02-01",
        )
        self.old_household.members.add(self.roommate)
        self.current_household.members.add(self.user, self.roommate)

        self.old_expense = Expense.objects.create(
            household=self.old_household,
            created_by=self.user,
            title="Old rent",
            amount=Decimal("100.00"),
            expense_date="2026-01-05",
            category="Rent",
        )
        self.current_expense = Expense.objects.create(
            household=self.current_household,
            created_by=self.user,
            title="Current groceries",
            amount=Decimal("40.00"),
            expense_date="2026-02-05",
            category="Food",
        )
        self.old_chore = Chore.objects.create(
            household=self.old_household,
            assigned_to=self.user,
            title="Old dishes",
            due_date="2026-01-06",
        )
        self.current_chore = Chore.objects.create(
            household=self.current_household,
            assigned_to=self.user,
            title="Current vacuum",
            due_date="2026-02-06",
        )
        self.old_message = Message.objects.create(
            household=self.old_household,
            author=self.user,
            title="Old note",
            body="Old household message.",
        )
        self.current_message = Message.objects.create(
            household=self.current_household,
            author=self.user,
            title="Current note",
            body="Current household message.",
        )
        self.old_owed_to_me = ExpenseShare.objects.create(
            expense=self.old_expense,
            user=self.roommate,
            amount_owed=Decimal("50.00"),
        )
        roommate_old_expense = Expense.objects.create(
            household=self.old_household,
            created_by=self.roommate,
            title="Old utilities",
            amount=Decimal("20.00"),
            expense_date="2026-01-07",
            category="Bills",
        )
        self.old_i_owe = ExpenseShare.objects.create(
            expense=roommate_old_expense,
            user=self.user,
            amount_owed=Decimal("10.00"),
        )

    def test_expenses_are_limited_to_current_household(self):
        self.client.login(username="alice", password="password123")
        response = self.client.get(reverse("project_expense_list"))

        self.assertContains(response, "Current groceries")
        self.assertNotContains(response, "Old rent")
        self.assertEqual(
            self.client.get(reverse("project_expense_detail", kwargs={"pk": self.old_expense.pk})).status_code,
            404,
        )

    def test_messages_are_limited_to_current_household(self):
        self.client.login(username="alice", password="password123")
        response = self.client.get(reverse("project_message_list"))

        self.assertContains(response, "Current note")
        self.assertNotContains(response, "Old note")
        self.assertEqual(
            self.client.get(reverse("project_message_detail", kwargs={"pk": self.old_message.pk})).status_code,
            404,
        )

    def test_chores_are_limited_to_current_household(self):
        self.client.login(username="alice", password="password123")
        response = self.client.get(reverse("project_chore_list"))

        self.assertContains(response, "Current vacuum")
        self.assertNotContains(response, "Old dishes")
        self.assertEqual(
            self.client.get(reverse("project_chore_detail", kwargs={"pk": self.old_chore.pk})).status_code,
            404,
        )

    def test_debt_pages_still_show_cross_household_records(self):
        self.client.login(username="alice", password="password123")

        what_i_owe = self.client.get(reverse("project_my_expense_shares"))
        who_owes_me = self.client.get(reverse("project_who_owes_me"))

        self.assertContains(what_i_owe, "Old utilities")
        self.assertIn(self.old_i_owe, what_i_owe.context["shares"])
        self.assertContains(who_owes_me, "Old rent")
        self.assertIn(self.old_owed_to_me, who_owes_me.context["shares"])

    def test_expense_and_chore_forms_only_offer_current_household(self):
        expense_form = ExpenseForm(user=self.user)
        chore_form = ChoreForm(user=self.user)

        self.assertNotIn(self.old_household, expense_form.fields["household"].queryset)
        self.assertIn(self.current_household, expense_form.fields["household"].queryset)
        self.assertNotIn(self.old_household, chore_form.fields["household"].queryset)
        self.assertIn(self.current_household, chore_form.fields["household"].queryset)


class HouseholdJoinSearchTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="password123")
        self.household_a = Household.objects.create(
            name="Bright House",
            address="100 Beacon Street",
            move_in_date="2026-01-01",
        )
        self.household_b = Household.objects.create(
            name="Quiet Loft",
            address="200 Commonwealth Ave",
            move_in_date="2026-01-01",
        )

    def test_join_household_search_matches_name(self):
        self.client.login(username="alice", password="password123")
        response = self.client.get(reverse("project_join_household"), {"q": "bright"})

        self.assertContains(response, "Bright House")
        self.assertNotContains(response, "Quiet Loft")
        self.assertNotContains(response, "<select", html=False)
        self.assertEqual(list(response.context["search_results"]), [self.household_a])

    def test_join_household_search_matches_address(self):
        self.client.login(username="alice", password="password123")
        response = self.client.get(reverse("project_join_household"), {"q": "commonwealth"})

        self.assertContains(response, "Quiet Loft")
        self.assertNotContains(response, "Bright House")
        self.assertNotContains(response, "<select", html=False)
        self.assertEqual(list(response.context["search_results"]), [self.household_b])

    def test_join_household_result_button_creates_join_request(self):
        self.client.login(username="alice", password="password123")
        response = self.client.post(
            reverse("project_join_household"),
            {"household_id": self.household_a.pk},
        )

        self.assertRedirects(response, reverse("project_home"))
        self.assertFalse(self.household_a.members.filter(pk=self.user.pk).exists())
        self.assertTrue(HouseholdJoinRequest.objects.filter(household=self.household_a, user=self.user).exists())

    def test_manager_can_approve_join_request(self):
        manager = User.objects.create_user(username="manager", password="password123")
        self.household_a.manager = manager
        self.household_a.save()
        self.household_a.members.add(manager)
        join_request = HouseholdJoinRequest.objects.create(household=self.household_a, user=self.user)

        self.client.login(username="manager", password="password123")
        response = self.client.post(reverse("project_household_join_request_approve", kwargs={"pk": join_request.pk}))

        self.assertRedirects(response, self.household_a.get_absolute_url())
        self.assertTrue(self.household_a.members.filter(pk=self.user.pk).exists())
        self.assertFalse(HouseholdJoinRequest.objects.filter(pk=join_request.pk).exists())

    def test_manager_can_transfer_manager_to_roommate(self):
        manager = User.objects.create_user(username="manager", password="password123")
        roommate = User.objects.create_user(username="roommate", password="password123")
        self.household_a.manager = manager
        self.household_a.save()
        self.household_a.members.add(manager, roommate)

        self.client.login(username="manager", password="password123")
        response = self.client.post(
            reverse("project_household_transfer_manager", kwargs={"pk": self.household_a.pk}),
            {"manager_id": roommate.pk},
        )

        self.assertRedirects(response, self.household_a.get_absolute_url())
        self.household_a.refresh_from_db()
        self.assertEqual(self.household_a.manager, roommate)

    def test_join_requests_appear_on_messages_page_without_transfer_controls(self):
        manager = User.objects.create_user(username="manager", password="password123")
        applicant = User.objects.create_user(username="applicant", password="password123")
        roommate = User.objects.create_user(username="roommate", password="password123")
        self.household_a.manager = manager
        self.household_a.save()
        self.household_a.members.add(manager, roommate)
        HouseholdJoinRequest.objects.create(household=self.household_a, user=applicant)

        self.client.login(username="manager", password="password123")
        response = self.client.get(reverse("project_message_list"))

        self.assertContains(response, "Join Requests")
        self.assertContains(response, "applicant")
        self.assertContains(response, "Approve")
        self.assertNotContains(response, "Transfer Manager")
        self.assertNotContains(response, "New Manager")

    def test_empty_join_requests_do_not_appear_on_messages_page(self):
        manager = User.objects.create_user(username="manager", password="password123")
        self.household_a.manager = manager
        self.household_a.save()
        self.household_a.members.add(manager)

        self.client.login(username="manager", password="password123")
        response = self.client.get(reverse("project_message_list"))

        self.assertNotContains(response, "Join Requests")
        self.assertNotContains(response, "No pending join requests.")


class HomeAndHouseholdStatusTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="password123")
        self.household = Household.objects.create(
            name="Apartment A",
            address="1 A St",
            move_in_date="2026-01-01",
        )
        self.other_household = Household.objects.create(
            name="Apartment B",
            address="2 B St",
            move_in_date="2026-01-01",
        )
        self.household.members.add(self.user)
        Expense.objects.create(
            household=self.household,
            created_by=self.user,
            title="Current expense",
            amount=Decimal("12.00"),
            expense_date="2026-01-01",
            category="Food",
        )
        Expense.objects.create(
            household=self.other_household,
            created_by=self.user,
            title="Other expense",
            amount=Decimal("12.00"),
            expense_date="2026-01-01",
            category="Food",
        )
        Chore.objects.create(
            household=self.household,
            assigned_to=self.user,
            title="Current chore",
            due_date="2026-01-02",
        )
        Chore.objects.create(
            household=self.other_household,
            assigned_to=self.user,
            title="Other chore",
            due_date="2026-01-02",
        )
        Message.objects.create(
            household=self.household,
            author=self.user,
            title="Current message",
            body="Hello.",
        )
        Message.objects.create(
            household=self.other_household,
            author=self.user,
            title="Other message",
            body="Hello.",
        )

    def test_home_counts_current_household_only(self):
        self.client.login(username="alice", password="password123")
        response = self.client.get(reverse("project_home"))

        self.assertEqual(response.context["expense_count"], 1)
        self.assertEqual(response.context["chore_count"], 1)
        self.assertEqual(response.context["message_count"], 1)

    def test_home_counts_are_zero_without_login_or_household(self):
        response = self.client.get(reverse("project_home"))

        self.assertEqual(response.context["expense_count"], 0)
        self.assertEqual(response.context["chore_count"], 0)
        self.assertEqual(response.context["message_count"], 0)

        self.household.members.remove(self.user)
        self.client.login(username="alice", password="password123")
        response = self.client.get(reverse("project_home"))

        self.assertEqual(response.context["expense_count"], 0)
        self.assertEqual(response.context["chore_count"], 0)
        self.assertEqual(response.context["message_count"], 0)

    def test_protected_project_pages_redirect_anonymous_users_to_login(self):
        protected_urls = [
            reverse("project_household_list"),
            reverse("project_expense_list"),
            reverse("project_my_expense_shares"),
            reverse("project_who_owes_me"),
            reverse("project_chore_list"),
            reverse("project_message_list"),
            reverse("project_join_household"),
            reverse("project_household_create"),
            reverse("project_expense_create"),
            reverse("project_chore_create"),
        ]

        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.url.startswith("/project/login/"))

    def test_user_can_leave_current_household(self):
        self.client.login(username="alice", password="password123")
        response = self.client.post(reverse("project_leave_household"))

        self.assertRedirects(response, reverse("project_home"))
        self.assertFalse(self.household.members.filter(pk=self.user.pk).exists())

    def test_manager_cannot_leave_before_transferring_manager(self):
        self.household.manager = self.user
        self.household.save()

        self.client.login(username="alice", password="password123")
        response = self.client.post(reverse("project_leave_household"))

        self.assertRedirects(response, self.household.get_absolute_url())
        self.assertTrue(self.household.members.filter(pk=self.user.pk).exists())
        self.household.refresh_from_db()
        self.assertEqual(self.household.manager, self.user)

    def test_manager_can_leave_after_transferring_manager(self):
        roommate = User.objects.create_user(username="roommate", password="password123")
        self.household.members.add(roommate)
        self.household.manager = roommate
        self.household.save()

        self.client.login(username="alice", password="password123")
        response = self.client.post(reverse("project_leave_household"))

        self.assertRedirects(response, reverse("project_home"))
        self.assertFalse(self.household.members.filter(pk=self.user.pk).exists())
        self.household.refresh_from_db()
        self.assertEqual(self.household.manager, roommate)

    def test_household_creator_becomes_manager(self):
        self.client.login(username="alice", password="password123")
        response = self.client.post(
            reverse("project_household_create"),
            {
                "name": "Managed Home",
                "address": "3 Manager St",
                "move_in_date": "2026-03-01",
            },
        )

        household = Household.objects.get(name="Managed Home")
        self.assertRedirects(response, household.get_absolute_url())
        self.assertEqual(household.manager, self.user)
        self.assertTrue(household.members.filter(pk=self.user.pk).exists())
