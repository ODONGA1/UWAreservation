# Generated manually to fix migration dependencies

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tours', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='park',
            name='image',
            field=models.ImageField(blank=True, help_text='Park cover image', null=True, upload_to='parks/'),
        ),
        migrations.AddField(
            model_name='tour',
            name='image',
            field=models.ImageField(blank=True, help_text='Tour cover image', null=True, upload_to='tours/'),
        ),
        migrations.AddField(
            model_name='tour',
            name='max_participants',
            field=models.PositiveIntegerField(default=10, help_text='Maximum number of participants allowed'),
        ),
        migrations.AlterField(
            model_name='tour',
            name='description',
            field=models.TextField(help_text='Detailed tour description'),
        ),
        migrations.AlterField(
            model_name='tour',
            name='duration',
            field=models.DurationField(help_text='Duration of the tour (e.g., 2 days, 4 hours)'),
        ),
        migrations.AlterField(
            model_name='tour',
            name='price',
            field=models.DecimalField(decimal_places=2, help_text='Price per person in USD', max_digits=10),
        ),
    ]
