from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_delete_role_models"),
    ]

    operations = [
        migrations.RenameField(
            model_name="userprofile",
            old_name="Date_of_birth",
            new_name="date_of_birth",
        ),
        migrations.AddField(
            model_name="userprofile",
            name="agency_name",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="assigned_maintenance_requests",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="assigned_properties",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="clients_managed_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="license_documents",
            field=models.JSONField(
                blank=True, help_text="Agent license documents", null=True
            ),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="license_expiration_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="license_id",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="maintenance_requests_handled_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="ownership_documents",
            field=models.JSONField(
                blank=True, help_text="Owner ownership documents", null=True
            ),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="preferred_locations",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="properties_managed_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="properties_owned_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="properties_rented_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="rental_history_rating",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="tenant_documents",
            field=models.JSONField(
                blank=True, help_text="Tenant documents", null=True
            ),
        ),
    ]
