from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):

    dependencies = [
        ('tracking', '0001_initial'),
    ]

    operations = [
        # Add seat fields to Bus
        migrations.AddField(
            model_name='bus',
            name='total_seats',
            field=models.PositiveIntegerField(default=40),
        ),
        migrations.AddField(
            model_name='bus',
            name='occupied_seats',
            field=models.PositiveIntegerField(default=0),
        ),
        # Create SOSAlert model
        migrations.CreateModel(
            name='SOSAlert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('message', models.TextField(blank=True, default='Emergency! Immediate assistance needed.')),
                ('status', models.CharField(choices=[('pending','Pending'),('acknowledged','Acknowledged'),('resolved','Resolved')], default='pending', max_length=15)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('resolved_at', models.DateTimeField(null=True, blank=True)),
                ('bus', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='tracking.bus')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sos_alerts', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
