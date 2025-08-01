# Generated manually for enhanced Profile model
from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        # Remove the old phone_number field
        migrations.RemoveField(
            model_name='profile',
            name='phone_number',
        ),
        # Update bio field
        migrations.AlterField(
            model_name='profile',
            name='bio',
            field=models.TextField(blank=True, help_text='Tell us about yourself and your interests in wildlife (max 500 characters)', max_length=500),
        ),
        # Add new phone_number field with validation
        migrations.AddField(
            model_name='profile',
            name='phone_number',
            field=models.CharField(blank=True, help_text='Contact phone number', max_length=17, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.", regex='^\\+?1?\\d{9,15}$')]),
        ),
        # Add newsletter subscription field
        migrations.AddField(
            model_name='profile',
            name='newsletter_subscription',
            field=models.BooleanField(default=True, help_text='Receive updates about new tours and conservation news'),
        ),
        # Add timestamps
        migrations.AddField(
            model_name='profile',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Update Meta options
        migrations.AlterModelOptions(
            name='profile',
            options={'verbose_name': 'User Profile', 'verbose_name_plural': 'User Profiles'},
        ),
    ]
