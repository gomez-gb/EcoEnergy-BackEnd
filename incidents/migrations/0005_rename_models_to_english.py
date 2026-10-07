from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incidents', '0004_alter_incidencia_description_and_more'),
    ]

    operations = [
        migrations.RenameModel(old_name='Incidencia', new_name='Incident'),
        migrations.RenameModel(old_name='IncidenciaSeguimiento', new_name='IncidentFollowUp'),
        migrations.RenameField(
            model_name='incidentfollowup',
            old_name='incidencia',
            new_name='incident',
        ),
    ]
