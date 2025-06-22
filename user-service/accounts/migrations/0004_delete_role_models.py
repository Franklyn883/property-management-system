from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_alter_customuser_phone_number"),
    ]

    operations = [
        migrations.DeleteModel(
            name="AgentProfile",
        ),
        migrations.DeleteModel(
            name="ManagerProfile",
        ),
        migrations.DeleteModel(
            name="OwnerProfile",
        ),
        migrations.DeleteModel(
            name="TenantProfile",
        ),
    ]
