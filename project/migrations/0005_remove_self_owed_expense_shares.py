from django.db import migrations


def remove_self_owed_expense_shares(apps, schema_editor):
    ExpenseShare = apps.get_model("project", "ExpenseShare")
    for share in ExpenseShare.objects.select_related("expense"):
        if share.user_id == share.expense.created_by_id:
            share.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("project", "0004_chore_completed_at_expenseshare_paid_at"),
    ]

    operations = [
        migrations.RunPython(remove_self_owed_expense_shares, migrations.RunPython.noop),
    ]
