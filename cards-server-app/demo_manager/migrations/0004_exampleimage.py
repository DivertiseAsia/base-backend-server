# Generated by Django 4.1.2 on 2023-04-03 09:50

import demo_manager.models.resize_image
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demo_manager', '0003_userbookstorage'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExampleImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('picture_width', models.PositiveIntegerField(blank=True, null=True)),
                ('picture_height', models.PositiveIntegerField(blank=True, null=True)),
                ('picture', demo_manager.models.resize_image.CustomImageField(aspect_ratios=[None], blank=True, breakpoints={'l': 1200, 'm': 992, 's': 768, 'xl': 1400, 'xs': 576}, container_width=1200, file_types=['WEBP'], grid_columns=1, height_field='picture_height', keep_original=False, max_file_size=None, null=True, pixel_densities=[1], quality=20, upload_to='pictures', width_field='picture_width')),
            ],
        ),
    ]
