# Generated by Django 4.1.7 on 2023-05-10 07:21

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_rename_price_invoice_totalamount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='password',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='user_id_number',
            field=models.CharField(max_length=200, validators=[django.core.validators.RegexValidator(message='Please input right identification number', regex='^[1-9]\\d{5}(19|20)\\d{2}(0[1-9]|1[012])(0[1-9]|[12][0-9]|3[01])\\d{3}[0-9xX]$')]),
        ),
    ]