from django.db import models
from django.contrib.postgres.fields import ArrayField

class Picture(models.Model):
    id = models.AutoField(primary_key=True)
    path = models.ImageField(upload_to="pictures/")


class Single_Physique(models.Model):
    id = models.IntegerField(primary_key=True)
    physique = models.CharField(max_length=255)

    def __str__(self):
        return self.physique


class Mixed_Physique(models.Model):
    id = models.IntegerField(primary_key=True)
    physique = models.CharField(max_length=255)
    single_ids = ArrayField(models.IntegerField(), blank=True, default=list)
    single_names = ArrayField(models.CharField(max_length=255), blank=True, default=list)


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


class Tagged_Data(models.Model):
    id = models.AutoField(primary_key=True)
    picture = models.ForeignKey(
        Picture,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="tagged_data",
        verbose_name="图片",
    )
    tongue_color = models.ForeignKey(
        TongueFeature,
        related_name="tongue_color",
        on_delete=models.CASCADE,
        verbose_name="舌色",
    )
    moss_color = models.ForeignKey(
        TongueFeature,
        related_name="moss_color",
        on_delete=models.CASCADE,
        verbose_name="苔色",
    )
    moss_quality = models.ForeignKey(
        TongueFeature,
        related_name="moss_quality",
        on_delete=models.CASCADE,
        verbose_name="苔质",
    )
    body_fluid = models.ForeignKey(
        TongueFeature,
        related_name="body_fluid",
        on_delete=models.CASCADE,
        verbose_name="津液",
    )
    sublingual_collaterals = models.ForeignKey(
        TongueFeature,
        related_name="sublingual_collaterals",
        on_delete=models.CASCADE,
        verbose_name="舌下络脉",
    )
    physique_type = models.CharField(max_length=255, verbose_name="体质类型")
    tongue_shape_ids = ArrayField(models.IntegerField(), blank=True, default=list, verbose_name="舌形")
    single_physique_ids = ArrayField(models.IntegerField(), blank=True, default=list)
    physique_id = ArrayField(models.IntegerField(), blank=True, default=list)
