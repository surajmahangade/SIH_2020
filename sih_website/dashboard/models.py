from django.db import models

# Create your models here.
class file_download(models.Model):
    #crawler_2 table 
    company_name = models.CharField(max_length=500)
    parent_link = models.CharField(max_length=500)
    url_of_file = models.CharField(max_length=500)
    sha_file = models.CharField(max_length=200,default=None)
    ca_checked = models.BooleanField(default=None)
    ca_type = models.CharField(max_length=100,default=None)

    class meta:
        db_table = "file_download"


class corp_action_data (models.Model):
    company_name = models.CharField(max_length=255)
    ca_type = models.CharField(max_length=255,null=True)
    div_type = models.CharField(max_length=255,null=True)
    div_percent = models.FloatField(null= True)
    date = models.DateTimeField(null=True)
    bonus_ratio = models.CharField(max_length=255,null=True)
    announcement_date = models.DateTimeField(null=True)
    record_date = models.DateTimeField(null=True)
    ex_date = models.CharField(max_length=255,null=True)
    old_fv = models.IntegerField(null=True)
    new_fv = models.IntegerField(null=True)
    split_date = models.DateTimeField(null=True)
    purpose = models.CharField(max_length=255,null=True)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
    agenda = models.CharField(max_length=255,null=True)
    premium = models.IntegerField(null=True)
    right_ratio = models.FloatField(null= True)
    fv = models.IntegerField(null=True)
    # data = models.CharField(max_length=5000)

    class meta:
        db_table = "corp_action_data"




