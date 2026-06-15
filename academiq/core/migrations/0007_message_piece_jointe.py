from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_tarif_niveau'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='piece_jointe',
            field=models.FileField(blank=True, null=True, upload_to='messages/'),
        ),
    ]
