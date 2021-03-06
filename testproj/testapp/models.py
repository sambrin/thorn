from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.db import models

from thorn import ModelEvent, webhook_model, model_reverser

# Create your models here.


class Foo(models.Model):
    username = models.CharField(max_length=128)

    def webhook_payload(self):
        return {'username': self.username}


class Bar(models.Model):
    foo = models.ForeignKey(Foo, related_name='bars')


class Tag(models.Model):
    name = models.CharField(max_length=128, unique=True)


@webhook_model(
    on_create=ModelEvent('article.created'),
    on_change=ModelEvent('article.changed'),
    on_delete=ModelEvent('article.removed'),
    on_tag=ModelEvent('article.tag_added').dispatches_on_m2m_add('tags'),
    on_tag_remove=ModelEvent(
        'article.tag_removed').dispatches_on_m2m_remove('tags'),
    on_tag_clear=ModelEvent(
        'article.tag_all_cleared').dispatches_on_m2m_clear('tags'),
    on_published=ModelEvent(
        'article.published', state__eq='PUBLISHED').dispatches_on_change(),
    sender_field='author',
    reverse=model_reverser('article:detail', id='pk'),
)
class Article(models.Model):
    title = models.CharField(max_length=128)
    state = models.CharField(max_length=64, default='PENDING')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='%(app_label)s_%(class)s',
    )
    tags = models.ManyToManyField(Tag)

    def webhook_payload(self):
        return {
            'title': self.title,
            'state': self.state,
            'author': ', '.join([
                self.author.last_name,
                self.author.first_name,
            ]),
        }


class SubscriberLog(models.Model):
    ref = models.CharField(max_length=128)
    event = models.CharField(max_length=128)
    data = models.TextField()
    hmac = models.TextField()
