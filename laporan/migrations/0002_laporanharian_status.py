# Generated manually for status field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("laporan", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="laporanharian",
            name="status",
            field=models.CharField(
                choices=[
                    ("Dalam Proses", "Dalam Proses"),
                    ("Selesai", "Selesai"),
                ],
                default="Dalam Proses",
                max_length=20,
                verbose_name="Status",
            ),
        ),
    ]
