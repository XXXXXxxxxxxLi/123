# Generated by Django 4.2.4 on 2023-09-01 09:06

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Physique",
            fields=[
                (
                    "physique_type",
                    models.CharField(
                        choices=[("single", "Single"), ("mixed", "Mixed")],
                        default="single",
                        max_length=10,
                    ),
                ),
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("physique", models.CharField(max_length=255)),
                (
                    "single_ids",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.IntegerField(),
                        blank=True,
                        default=list,
                        size=None,
                    ),
                ),
                (
                    "single_names",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=255),
                        blank=True,
                        default=list,
                        size=None,
                    ),
                ),
            ],
            options={
                "db_table": "physique",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="Picture",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("path", models.ImageField(upload_to="annotate_photo/")),
            ],
            options={
                "db_table": "picture",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="Tagged_Data",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "physique_type",
                    models.CharField(max_length=255, verbose_name="体质类型"),
                ),
                (
                    "tongue_shape_ids",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.IntegerField(),
                        blank=True,
                        default=list,
                        size=None,
                        verbose_name="舌形",
                    ),
                ),
                (
                    "single_physique_ids",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.IntegerField(),
                        blank=True,
                        default=list,
                        size=None,
                    ),
                ),
                (
                    "physique_id",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.IntegerField(),
                        blank=True,
                        default=list,
                        size=None,
                    ),
                ),
            ],
            options={
                "db_table": "tagged_data",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="TongueFeature",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "feature_type",
                    models.CharField(
                        choices=[
                            ("TC", "舌色"),
                            ("MC", "苔色"),
                            ("MQ", "苔质"),
                            ("TS", "舌形"),
                            ("BF", "津液"),
                            ("SC", "舌下络脉"),
                        ],
                        default="TC",
                        max_length=2,
                    ),
                ),
                ("specific_feature", models.CharField(max_length=100)),
            ],
            options={
                "db_table": "tonguefeature",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="WhirEquipment",
            fields=[
                (
                    "id",
                    models.CharField(max_length=36, primary_key=True, serialize=False),
                ),
                ("create_by", models.CharField(blank=True, max_length=50, null=True)),
                ("create_time", models.DateTimeField(blank=True, null=True)),
                ("update_by", models.CharField(blank=True, max_length=50, null=True)),
                ("update_time", models.DateTimeField(blank=True, null=True)),
                (
                    "sys_org_code",
                    models.CharField(blank=True, max_length=64, null=True),
                ),
                (
                    "equipment_id",
                    models.CharField(blank=True, max_length=32, null=True),
                ),
                ("qy_id", models.CharField(blank=True, max_length=32, null=True)),
                ("date", models.DateTimeField(blank=True, null=True)),
                ("people", models.CharField(blank=True, max_length=255, null=True)),
                ("status", models.IntegerField(blank=True, null=True)),
                ("details", models.CharField(blank=True, max_length=255, null=True)),
                ("expiredate", models.DateTimeField(blank=True, null=True)),
                ("address", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "jurisdiction",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("alias", models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                "db_table": "whir_equipment",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="WhirMedicine",
            fields=[
                (
                    "id",
                    models.CharField(max_length=36, primary_key=True, serialize=False),
                ),
                ("create_by", models.CharField(blank=True, max_length=50, null=True)),
                ("create_time", models.DateTimeField(blank=True, null=True)),
                ("update_by", models.CharField(blank=True, max_length=50, null=True)),
                ("update_time", models.DateTimeField(blank=True, null=True)),
                (
                    "sys_org_code",
                    models.CharField(blank=True, max_length=64, null=True),
                ),
                ("number", models.CharField(blank=True, max_length=255, null=True)),
                ("name", models.CharField(blank=True, max_length=255, null=True)),
                ("img", models.CharField(blank=True, max_length=255, null=True)),
                ("status", models.IntegerField(blank=True, null=True)),
                ("steps", models.CharField(blank=True, max_length=1024, null=True)),
                ("reference", models.CharField(blank=True, max_length=255, null=True)),
                ("compose", models.CharField(blank=True, max_length=512, null=True)),
                ("effect", models.CharField(blank=True, max_length=255, null=True)),
                ("indication", models.CharField(blank=True, max_length=512, null=True)),
                ("taboo", models.TextField(blank=True, null=True)),
                ("enterprise", models.CharField(blank=True, max_length=255, null=True)),
                ("by_effect", models.TextField(blank=True, null=True)),
                ("symptom", models.CharField(blank=True, max_length=255, null=True)),
                ("sha256", models.CharField(blank=True, max_length=500, null=True)),
            ],
            options={
                "db_table": "whir_medicine",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="WhirQyArchives",
            fields=[
                (
                    "id",
                    models.CharField(max_length=36, primary_key=True, serialize=False),
                ),
                ("create_by", models.CharField(blank=True, max_length=50, null=True)),
                ("create_time", models.DateTimeField(blank=True, null=True)),
                ("update_by", models.CharField(blank=True, max_length=50, null=True)),
                ("update_time", models.DateTimeField(blank=True, null=True)),
                (
                    "sys_org_code",
                    models.CharField(blank=True, max_length=64, null=True),
                ),
                ("name", models.CharField(blank=True, max_length=255, null=True)),
                ("tax_number", models.CharField(blank=True, max_length=255, null=True)),
                ("licence", models.CharField(blank=True, max_length=255, null=True)),
                ("person", models.CharField(blank=True, max_length=255, null=True)),
                ("address", models.CharField(blank=True, max_length=255, null=True)),
                ("phone", models.CharField(blank=True, max_length=32, null=True)),
                ("email", models.CharField(blank=True, max_length=255, null=True)),
                ("qy_explain", models.CharField(blank=True, max_length=255, null=True)),
                ("status", models.IntegerField(blank=True, null=True)),
                ("logo", models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                "db_table": "whir_qy_archives",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="WhirQyMedicine",
            fields=[
                (
                    "id",
                    models.CharField(max_length=36, primary_key=True, serialize=False),
                ),
                ("create_by", models.CharField(blank=True, max_length=50, null=True)),
                ("create_time", models.DateTimeField(blank=True, null=True)),
                ("update_by", models.CharField(blank=True, max_length=50, null=True)),
                ("update_time", models.DateTimeField(blank=True, null=True)),
                (
                    "sys_org_code",
                    models.CharField(blank=True, max_length=64, null=True),
                ),
                ("qy_id", models.CharField(blank=True, max_length=32, null=True)),
                ("medicine_id", models.CharField(blank=True, max_length=32, null=True)),
                ("brand", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "specifications",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("model", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "medicine_img",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("img_date", models.DateTimeField(blank=True, null=True)),
                ("checkstatus", models.IntegerField(blank=True, null=True)),
                ("checkdate", models.DateTimeField(blank=True, null=True)),
                (
                    "checkexplain",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("people", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "equipment_id",
                    models.CharField(blank=True, max_length=2555, null=True),
                ),
                ("symptom", models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                "db_table": "whir_qy_medicine",
                "managed": False,
            },
        ),
    ]