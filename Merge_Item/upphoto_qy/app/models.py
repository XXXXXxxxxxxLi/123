from django.contrib.postgres.fields import ArrayField
from django.db import models


class WhirEquipment(models.Model):
    id = models.CharField(primary_key=True, max_length=36)
    create_by = models.CharField(max_length=50, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    update_by = models.CharField(max_length=50, blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    sys_org_code = models.CharField(max_length=64, blank=True, null=True)
    equipment_id = models.CharField(max_length=32, blank=True, null=True)
    qy_id = models.CharField(max_length=32, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    people = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    details = models.CharField(max_length=255, blank=True, null=True)
    expiredate = models.DateTimeField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    jurisdiction = models.CharField(max_length=255, blank=True, null=True)
    alias = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "whir_equipment"


class WhirMedicine(models.Model):
    id = models.CharField(primary_key=True, max_length=36)
    create_by = models.CharField(max_length=50, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    update_by = models.CharField(max_length=50, blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    sys_org_code = models.CharField(max_length=64, blank=True, null=True)
    number = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    img = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    steps = models.CharField(max_length=1024, blank=True, null=True)
    reference = models.CharField(max_length=255, blank=True, null=True)
    compose = models.CharField(max_length=512, blank=True, null=True)
    effect = models.CharField(max_length=255, blank=True, null=True)
    indication = models.CharField(max_length=512, blank=True, null=True)
    taboo = models.TextField(blank=True, null=True)
    enterprise = models.CharField(max_length=255, blank=True, null=True)
    by_effect = models.TextField(blank=True, null=True)
    symptom = models.CharField(max_length=255, blank=True, null=True)
    sha256 = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "whir_medicine"


class WhirQyArchives(models.Model):
    id = models.CharField(primary_key=True, max_length=36)
    create_by = models.CharField(max_length=50, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    update_by = models.CharField(max_length=50, blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    sys_org_code = models.CharField(max_length=64, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    tax_number = models.CharField(max_length=255, blank=True, null=True)
    licence = models.CharField(max_length=255, blank=True, null=True)
    person = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=32, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    qy_explain = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    logo = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "whir_qy_archives"


class WhirQyMedicine(models.Model):
    id = models.CharField(primary_key=True, max_length=36)
    create_by = models.CharField(max_length=50, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    update_by = models.CharField(max_length=50, blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    sys_org_code = models.CharField(max_length=64, blank=True, null=True)
    qy_id = models.CharField(max_length=32, blank=True, null=True)
    medicine_id = models.CharField(max_length=32, blank=True, null=True)
    brand = models.CharField(max_length=255, blank=True, null=True)
    specifications = models.CharField(max_length=255, blank=True, null=True)
    model = models.CharField(max_length=255, blank=True, null=True)
    medicine_img = models.CharField(max_length=255, blank=True, null=True)
    img_date = models.DateTimeField(blank=True, null=True)
    checkstatus = models.IntegerField(blank=True, null=True)
    checkdate = models.DateTimeField(blank=True, null=True)
    checkexplain = models.CharField(max_length=255, blank=True, null=True)
    people = models.CharField(max_length=255, blank=True, null=True)
    equipment_id = models.CharField(max_length=2555, blank=True, null=True)
    symptom = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "whir_qy_medicine"


class Picture(models.Model):
    id = models.AutoField(primary_key=True)
    path = models.ImageField(upload_to="tongue/")

    class Meta:
        managed = False
        db_table = "picture"


class Physique(models.Model):
    SINGLE = "single"
    MIXED = "mixed"

    physique_type = models.CharField(
        max_length=10, choices=[(SINGLE, "Single"), (MIXED, "Mixed")], default=SINGLE
    )

    id = models.IntegerField(primary_key=True)
    physique = models.CharField(max_length=255)
    single_ids = ArrayField(models.IntegerField(), blank=True, default=list)
    single_names = ArrayField(
        models.CharField(max_length=255), blank=True, default=list
    )

    def __str__(self):
        return self.physique

    class Meta:
        managed = False
        db_table = "physique"


class TongueFeature(models.Model):
    FEATURE_TYPES = [
        ("TC", "舌色"),
        ("MC", "苔色"),
        ("MQ", "苔质"),
        ("TS", "舌形"),
        ("BF", "津液"),
        ("SC", "舌下络脉"),
    ]
    feature_type = models.CharField(
        max_length=2,
        choices=FEATURE_TYPES,
        default="TC",
    )
    specific_feature = models.CharField(max_length=100)

    def __str__(self):
        return self.specific_feature

    class Meta:
        managed = False
        db_table = "tonguefeature"


class Tagged_Data(models.Model):
    id = models.AutoField(primary_key=True)
    picture = models.ForeignKey(
        Picture,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tagged_data",
        verbose_name="图片",
    )
    tongue_color = models.ForeignKey(
        TongueFeature,
        related_name="tongue_color",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="舌色",
    )
    moss_color = models.ForeignKey(
        TongueFeature,
        related_name="moss_color",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="苔色",
    )
    moss_quality = models.ForeignKey(
        TongueFeature,
        related_name="moss_quality",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="苔质",
    )
    body_fluid = models.ForeignKey(
        TongueFeature,
        related_name="body_fluid",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="津液",
    )
    sublingual_collaterals = models.ForeignKey(
        TongueFeature,
        related_name="sublingual_collaterals",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="舌下络脉",
    )
    physique_type = models.CharField(max_length=255, verbose_name="体质类型")
    tongue_shape_ids = ArrayField(
        models.IntegerField(), blank=True, default=list, verbose_name="舌形"
    )
    single_physique_ids = ArrayField(models.IntegerField(), blank=True, default=list)
    physique_id = ArrayField(models.IntegerField(), blank=True, default=list)

    class Meta:
        managed = False
        db_table = "tagged_data"


class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
