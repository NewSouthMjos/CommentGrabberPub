# Generated by Django 3.0 on 2021-08-23 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Result_row',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Result_date', models.DateTimeField(verbose_name='Дата')),
                ('Result_author', models.CharField(max_length=100, verbose_name='Автор')),
                ('Result_comment', models.TextField(verbose_name='Комментарий')),
                ('Result_parentnote', models.TextField(verbose_name='К записи')),
                ('Result_likescount', models.PositiveIntegerField(verbose_name='Количество лайков')),
            ],
        ),
    ]