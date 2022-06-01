# Generated by Django 4.0 on 2022-07-31 13:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HashTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ig_id', models.CharField(blank=True, max_length=100)),
                ('name', models.CharField(blank=True, max_length=150)),
                ('media_count', models.PositiveIntegerField(blank=True, default=0)),
            ],
        ),
        migrations.CreateModel(
            name='IGUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ig_pk', models.CharField(blank=True, max_length=100)),
                ('username', models.CharField(blank=True, max_length=150)),
                ('full_name', models.CharField(blank=True, max_length=200)),
                ('is_private', models.BooleanField(blank=True, default=False)),
                ('profile_pic_url', models.URLField(blank=True, null=True)),
                ('profile_pic_url_hd', models.URLField(blank=True, null=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('media_count', models.PositiveIntegerField(blank=True, default=0)),
                ('follower_count', models.PositiveIntegerField(blank=True, default=0)),
                ('following_count', models.PositiveIntegerField(blank=True, default=0)),
                ('biography', models.TextField(blank=True)),
                ('external_url', models.URLField(blank=True, null=True)),
                ('is_business', models.BooleanField(blank=True, default=False)),
                ('business_category_name', models.CharField(blank=True, max_length=150)),
                ('category_name', models.CharField(blank=True, max_length=150)),
                ('category', models.CharField(blank=True, max_length=150)),
                ('public_email', models.EmailField(blank=True, max_length=254)),
                ('contact_phone_number', models.CharField(blank=True, max_length=30)),
                ('public_phone_country_code', models.CharField(blank=True, max_length=5)),
                ('public_phone_number', models.CharField(blank=True, max_length=30)),
                ('business_contact_method', models.CharField(blank=True, max_length=50)),
                ('city_id', models.CharField(blank=True, max_length=100)),
                ('city_name', models.CharField(blank=True, max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ig_pk', models.PositiveIntegerField(blank=True, null=True)),
                ('category', models.CharField(blank=True, max_length=100)),
                ('name', models.CharField(blank=True, max_length=100)),
                ('lng', models.DecimalField(blank=True, decimal_places=4, max_digits=6, null=True)),
                ('lat', models.DecimalField(blank=True, decimal_places=4, max_digits=6, null=True)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Media',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ig_pk', models.PositiveIntegerField(blank=True, null=True)),
                ('ig_id', models.CharField(blank=True, max_length=100)),
                ('code', models.SlugField(blank=True)),
                ('title', models.CharField(blank=True, max_length=200)),
                ('caption_text', models.TextField(blank=True)),
                ('url', models.URLField(blank=True, null=True)),
                ('video_url', models.URLField(blank=True, null=True)),
                ('media_type', models.CharField(blank=True, choices=[('Photo', 'Photo'), ('Video', 'Video'), ('IGTV', 'IGTV'), ('Reel', 'Reel'), ('Album', 'Album')], max_length=7)),
                ('taken_at', models.DateTimeField(blank=True, null=True)),
                ('comment_count', models.PositiveIntegerField(blank=True, default=0)),
                ('like_count', models.PositiveIntegerField(blank=True, default=0)),
                ('view_count', models.PositiveIntegerField(blank=True, default=0)),
                ('video_duration', models.FloatField(default=0)),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='observations.location')),
                ('tags', models.ManyToManyField(to='observations.HashTag')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medias', to='observations.iguser')),
                ('usertags', models.ManyToManyField(to='observations.IGUser')),
            ],
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ig_pk', models.PositiveIntegerField(blank=True, null=True)),
                ('video_url', models.URLField(blank=True, null=True)),
                ('thumbnail_url', models.URLField(blank=True, null=True)),
                ('media_type', models.CharField(blank=True, choices=[('Photo', 'Photo'), ('Video', 'Video')], max_length=7)),
                ('media', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resources', to='observations.media')),
            ],
        ),
        migrations.AddField(
            model_name='iguser',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='observations.location'),
        ),
    ]