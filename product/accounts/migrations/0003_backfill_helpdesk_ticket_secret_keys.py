import uuid

from django.db import migrations
from django.db.models import Q


def backfill_ticket_secret_keys(apps, schema_editor):
    Ticket = apps.get_model("helpdesk", "Ticket")
    database = schema_editor.connection.alias
    tickets = Ticket.objects.using(database).filter(
        Q(secret_key="") | Q(secret_key__isnull=True)
    )

    for ticket_id in tickets.values_list("pk", flat=True).iterator():
        Ticket.objects.using(database).filter(pk=ticket_id).update(
            secret_key=str(uuid.uuid4())
        )


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_alter_userinformation_notes"),
        ("helpdesk", "0039_alter_ticketchange_field"),
    ]

    operations = [
        migrations.RunPython(backfill_ticket_secret_keys, migrations.RunPython.noop),
    ]
