from django.db import models
import uuid
# Create your models here.


class PinCode(models.Model):
	pin=models.CharField(max_length=100)

	def __str__(self):
		return self.pin
