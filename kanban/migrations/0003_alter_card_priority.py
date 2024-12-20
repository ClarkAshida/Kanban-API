# Generated by Django 5.1 on 2024-11-21 23:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kanban', '0002_board_column_fk_board'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='priority',
            field=models.CharField(blank=True, choices=[('U', 'Urgente'), ('I', 'Importante'), ('M', 'Média'), ('B', 'Baixa')], default='M', max_length=1, null=True),
        ),
    ]
