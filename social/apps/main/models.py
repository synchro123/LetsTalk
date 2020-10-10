from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

# Create your models here.
class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
	birth_date = models.DateField('дата рождения', null=True, blank=True)
	verified = models.BooleanField('подтвержденная страница', default=False)
	status = models.TextField('Статус')

	avatar = models.TextField('Аватарка')

class Post(models.Model):
	author = models.ForeignKey(User, on_delete=models.CASCADE)

	post_text = models.TextField('текст поста')

	published_date = models.DateTimeField('время публикации', auto_now=True)

	likes = models.ManyToManyField(User, blank=True, related_name='i_liked')

	class Meta:
		ordering = ['-published_date',]


class PostComment(models.Model):
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	post = models.ForeignKey(Post, on_delete=models.CASCADE)

	comment_text = models.TextField('текст комментария')

	published_date = models.DateTimeField('время оставления', auto_now=True)

	class Meta:
		ordering = ['-published_date',]

#запрос дружбы
class FriendshipRequest(models.Model):
	sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='i_sender')
	recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='i_recipient')

	request_date = models.DateTimeField('время запроса', auto_now=True)

class Chat(models.Model):
	DIALOG = 'D'
	CHAT = 'C'
	CHAT_TYPE_CHOICES = (
		(DIALOG, _('Dialog')),
		(CHAT, _('Chat'))
	)
 
	type = models.CharField(
		_('Тип'),
		max_length=1,
		choices=CHAT_TYPE_CHOICES,
		default=DIALOG
	)
	members = models.ManyToManyField(User, verbose_name=_("Участник"))
	
	def get_absolute_url(self):
		return reverse('messages', kwargs={'chat_id': self.pk})
 
 
class Message(models.Model):
	chat = models.ForeignKey(Chat, verbose_name=_("Чат"), on_delete=models.CASCADE)
	author = models.ForeignKey(User, verbose_name=_("Пользователь"), on_delete=models.CASCADE, related_name='i_messages')
	message = models.TextField(_("Сообщение"))
	pub_date = models.DateTimeField(_('Дата сообщения'), default=timezone.now)
	is_readed = models.BooleanField(_('Прочитано'), default=False)

	readers = models.ManyToManyField(User, verbose_name=_("Прочитавшие"))
	 
	class Meta:
		ordering=['pub_date']
	 
	def __str__(self):
		return self.message