from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registration_enabled', models.BooleanField(default=True, verbose_name='允许注册')),
            ],
            options={
                'verbose_name': '站点设置',
                'verbose_name_plural': '站点设置',
                'db_table': 'site_setting',
            },
        ),
        migrations.RunPython(
            code=lambda apps, schema_editor: apps.get_model('users', 'SiteSetting').objects.get_or_create(pk=1),
            reverse_code=migrations.RunPython.noop,
        ),
    ]
