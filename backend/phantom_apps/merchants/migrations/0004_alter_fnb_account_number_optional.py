from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('merchants', '0003_add_merchant_registration_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='merchant',
            name='fnb_account_number',
            field=models.CharField(blank=True, max_length=20, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='merchant',
            name='business_registration',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
    ]