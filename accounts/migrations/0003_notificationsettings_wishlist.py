# Generated manually

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0002_enhanced_profile'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_bookings', models.BooleanField(default=True, help_text='Receive booking confirmations and updates')),
                ('email_promotions', models.BooleanField(default=True, help_text='Receive promotional offers and new tour announcements')),
                ('email_reminders', models.BooleanField(default=True, help_text='Receive tour reminders and preparation tips')),
                ('email_updates', models.BooleanField(default=True, help_text='Receive general updates and newsletters')),
                ('sms_reminders', models.BooleanField(default=False, help_text='Receive SMS reminders for upcoming tours')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='notification_settings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('tour', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wishlisted_by', to='tours.tour')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wishlist_items', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-added_at'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='wishlist',
            unique_together={('user', 'tour')},
        ),
    ]
