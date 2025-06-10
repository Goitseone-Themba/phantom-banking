from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0002_add_wallet_creation_request'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='walletcreationrequest',
            name='status',
        ),
        migrations.RemoveField(
            model_name='walletcreationrequest',
            name='processed_at',
        ),
    ]