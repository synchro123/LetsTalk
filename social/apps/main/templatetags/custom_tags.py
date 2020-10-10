from django import template
from django.shortcuts import get_object_or_404

register = template.Library()


@register.simple_tag
def get_companion(user, chat):
	for u in chat.members.all():
		if u != user:
			return u
	return None

@register.simple_tag
def get_unreaded_messages_count(user, chat):
	messages = chat.message_set.all()
	count = messages.filter(readers__in=[user.id]).count()
	return messages.count() - count