from django.db import migrations, models
import django.utils.timezone
import uuid

class Migration(migrations.Migration):

    dependencies = [
        ('merchants', '0001_initial'),
        ('wallets', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WalletCreationRequest',
            fields=[
                ('request_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=150)),
                ('last_name', models.CharField(max_length=150)),
                ('email', models.EmailField(max_length=254)),
                ('phone_number', models.CharField(max_length=20)),
                ('national_id', models.CharField(max_length=20)),
                ('date_of_birth', models.DateField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('processed_at', models.DateTimeField(blank=True, null=True)),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='merchants.merchant')),
            ],
        ),
    ]