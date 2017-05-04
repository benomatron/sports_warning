# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-22 22:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import sportswar.users.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('phone_number', models.CharField(blank=True, max_length=20)),
                ('country_code', models.CharField(blank=True, default='1', max_length=3)),
                ('authy_user_id', models.CharField(blank=True, max_length=254)),
                ('has_validated_phone', models.BooleanField(default=False)),
                ('display_name', models.CharField(blank=True, max_length=100)),
                ('time_zone', models.CharField(choices=[('US/Eastern', 'US/Eastern'), ('US/Central', 'US/Central'), ('US/Pacific', 'US/Pacific'), ('US/Mountain', 'US/Mountian'), ('US/Arizona', 'US/Arizona'), ('US/Michigan', 'US/Michigan'), ('US/Hawaii', 'US/Hawaii'), ('US/East-Indiana', 'US/East-Indiana'), ('US/Indiana-Starke', 'US/Indiana-Starke')], default='US/Eastern', max_length=100)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', sportswar.users.models.UserManager()),
            ],
        ),
    ]
