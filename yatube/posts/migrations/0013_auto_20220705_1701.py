# Generated by Django 2.2.16 on 2022-07-05 14:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0012_auto_20220705_1611'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'verbose_name': ('Комментарий',), 'verbose_name_plural': 'Комментарии'},
        ),
    ]