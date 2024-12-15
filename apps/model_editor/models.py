from django.db import models
from django.contrib.auth.models import User

class NeuralNetwork(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Layer(models.Model):
    network = models.ForeignKey(NeuralNetwork, related_name='layers', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    layer_type = models.CharField(max_length=50)
    config = models.JSONField(default=dict)
    order = models.IntegerField()

    class Meta:
        ordering = ['order']

class LayerConnection(models.Model):
    network = models.ForeignKey(NeuralNetwork, related_name='connections', on_delete=models.CASCADE)
    from_layer = models.ForeignKey(Layer, related_name='outgoing_connections', on_delete=models.CASCADE)
    to_layer = models.ForeignKey(Layer, related_name='incoming_connections', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('network', 'from_layer', 'to_layer')