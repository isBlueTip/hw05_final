# Generated by Django 2.2.16 on 2022-02-05 08:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0011_auto_20220203_1129'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-pub_date'], 'verbose_name': 'пост', 'verbose_name_plural': 'посты'},
        ),
    ]
