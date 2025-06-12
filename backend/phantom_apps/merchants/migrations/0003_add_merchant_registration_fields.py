from django.db import migrations, models
import django.core.validators

class Migration(migrations.Migration):

    dependencies = [
        ('merchants', '0002_merchant_admin_email_merchant_admin_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='merchant',
            name='admin_email',
            field=models.EmailField(default='', max_length=254),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='merchant',
            name='admin_name',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='merchant',
            name='registration_number',
            field=models.CharField(default='', max_length=100, unique=True),
            preserve_default=False,
        ),
    ]