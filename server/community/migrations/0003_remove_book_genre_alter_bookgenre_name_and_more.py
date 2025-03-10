# Generated by Django 5.1.4 on 2025-02-06 08:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0002_book_is_recommended_book_recommendation_comment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='genre',
        ),
        migrations.AlterField(
            model_name='bookgenre',
            name='name',
            field=models.CharField(choices=[('시', '시'), ('소설', '소설'), ('에세이', '에세이'), ('비문학', '비문학')], max_length=100, unique=True, verbose_name='장르'),
        ),
        migrations.AlterField(
            model_name='bookgenre',
            name='slug',
            field=models.SlugField(blank=True, max_length=100, unique=True, verbose_name='슬러그'),
        ),
        migrations.AddField(
            model_name='book',
            name='genre',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='community.bookgenre', verbose_name='장르'),
        ),
    ]
