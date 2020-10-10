from django.forms import ModelForm
from .models import FriendshipRequest, Post, UserProfile, Chat, Message

class MessageForm(ModelForm):
	class Meta:
		model = Message
		fields = ['message']
		labels = {'message': ""}
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for fld in self.fields:
			self.fields[fld].widget.attrs['class'] = 'form-control'
			self.fields[fld].widget.attrs['style'] = 'min-height: 38px'
			self.fields[fld].widget.attrs['rows'] = '1'
			self.fields[fld].widget.attrs['cols'] = ''