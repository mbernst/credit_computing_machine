from django.db import models
from credit_computing_machine.models import TimestampModel
from privateurl.models import PrivateUrl
from django.db.models.signals import pre_save
from django.dispatch import receiver
# Create your models here.

class CreditGroupManager(models.Manager):

    def get_credit_all_user(self, credit_group_id):
        return CreditUser.objects.filter(credit_group=credit_group_id)

    def get_credit_admin_user(self, credit_group_id):
        return CreditUser.objects.filter(credit_group=credit_group_id, is_admin=True)

    def get_credit_non_admin_user(self, credit_group_id):
        return CreditUser.objects.filter(credit_group=credit_group_id, is_admin=False)


class CreditGroup(TimestampModel):
    name = models.CharField(max_length=200)
    is_deleted = models.BooleanField(default=False)
    privateurl = models.ForeignKey(PrivateUrl,null=True)
    objects = CreditGroupManager()


@receiver(pre_save, sender=CreditGroup, dispatch_uid="add_group_purl")
def add_group_purl(sender, instance, **kwargs):
     purl = PrivateUrl.create('manage_credit_score')
     instance.privateurl= purl

class CreditUser(TimestampModel):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    credit_group = models.ForeignKey(CreditGroup, null=True, blank=True, related_name='credit_users')
    is_admin = models.BooleanField(default=False)
    privateurl = models.ForeignKey(PrivateUrl, null=True)

@receiver(pre_save, sender=CreditUser, dispatch_uid="add_user_purl")
def add_user_purl(sender, instance, **kwargs):
     purl = PrivateUrl.create('user_credit')
     instance.privateurl= purl


class CreditScore(TimestampModel):
    score = models.FloatField()
    from_credit_user = models.ForeignKey(
        CreditUser, related_name='from_credit_user')
    to_credit_user = models.ForeignKey(
        CreditUser, related_name='to_credit_user')
    credit_group = models.ForeignKey(CreditGroup)
