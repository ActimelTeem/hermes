from django.db import models
from django.utils import timezone

class OrderStatus(models.Model):
    status = models.CharField(max_length=200)

    def __str__(self):
        return self.status

class PaymentStatus(models.Model):
    status = models.CharField(max_length=200)

    def __str__(self):
        return self.status

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    content = models.TextField()
    order_location = models.CharField(max_length=200)
    order_status = models.ForeignKey('crm.OrderStatus')
    order_courier_comment = models.TextField()
    order_client_comment = models.TextField()
    order_client = models.TextField()
    payment_status = models.ForeignKey('crm.PaymentStatus')
    order_date = models.DateTimeField(blank=True, null=True)
    order_cost = models.FloatField()
    order_manager = models.ForeignKey('auth.User')
    order_courier = models.TextField()
    order_dest_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        self.order_date = timezone.now()
        self.save()

    def __str__(self):
        return str(self.order_id)

# Create your models here.
