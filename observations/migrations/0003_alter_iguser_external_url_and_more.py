# Generated by Django 4.0 on 2022-08-02 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('observations', '0002_alter_hashtag_ig_id_alter_iguser_ig_pk_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='iguser',
            name='external_url',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='iguser',
            name='profile_pic_url',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='iguser',
            name='profile_pic_url_hd',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='media',
            name='url',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='media',
            name='video_url',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='resource',
            name='thumbnail_url',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='resource',
            name='video_url',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
    ]
