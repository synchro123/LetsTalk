from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.generic.base import RedirectView
from django.views.generic import TemplateView
from django.views import View
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime

from .models import FriendshipRequest, Post, UserProfile, Chat, Message

from .forms import MessageForm

from django.db.models import Count


#0 - не друзья, 1 - первый подписан на 2го, 2 - второй подписан на 1го, 3 - друзья
def getFriendship(obj1, obj2):
	result = 0

	request1 = None
	request2 = None

	try:
		request1 = FriendshipRequest.objects.get(sender = obj1, recipient = obj2)
	except:
		pass

	try:
		request2 = FriendshipRequest.objects.get(sender = obj2, recipient = obj1)
	except:
		pass

	if request1 is not None and request2 is None:
		result = 1

	if request1 is None and request2 is not None:
		result = 2

	if request1 is not None and request2 is not None:
		result = 3

	return result

def getFriends(obj1):
	users = User.objects.all();
	result = []
	for u in users:
		if getFriendship(obj1, u) == 3:
			result.append(u)
	return result


def homepage(request):
	if request.user.is_authenticated:
		return HttpResponseRedirect('/id' + str(request.user.id))

	if request.method == "POST":
		username = request.POST['username']
		password = request.POST['pass']
		
		user = authenticate(username=username, password=password)
		if user is not None:
			login(request, user)
			try:
				prfile = UserProfile.objects.get(user=request.user)
			except:
				UserProfile.objects.create(user=request.user)

			return HttpResponseRedirect('/id' + str(request.user.id));


	return render(request, 'pages/home.html')

@login_required
def profile(request, id):
	user_model = User.objects.get(id=id)

	if request.method == "POST":
		pasta_text = request.POST['post_text']
		pasta = request.user.post_set.create(post_text = pasta_text)
		return HttpResponseRedirect(request.path);

	template = 'pages/account/profile.html'

	me = user_model == request.user

	pasti = None

	try:
		pasti = user_model.post_set.order_by('-id');
	except:
		pass
	posts = []

	for p in pasti:
		liked = request.user in p.likes.all()

		posts.append([p, liked])

	fr = getFriendship(request.user, user_model)

	fradd = ['Добавить в друзья','Заявка отправлена','Ответить на заявку','У вас в друзьях'][fr]

	friends = getFriends(user_model)

	context = {
		'me': me,
		'user': user_model,
		'posts': posts,
		'fradd': fradd,
		'friends': friends,
		'friendsshort': friends[:5],
		'friendscount': len(friends),
	}

	return render(request, template, context)

class FriendsView(View):
	def get(self, request, user_id):
		
		user = get_object_or_404(User, id=user_id)
		friends = []

		if user is not None:
			friends = getFriends(user)
 		
		return render(
			request,
			'pages/account/friends.html',
			{
				'user': user,
				'friends': friends,
				'friends_count': len(friends)
			}
		)

@login_required
def edit_profile(request):
	if request.method == 'POST':
		avatar = request.POST.get('avatar')
		if avatar:
			request.user.userprofile.avatar = avatar
		else:
			request.user.userprofile.avatar = 'https://vk.com/images/soviet_200.png'
		request.user.userprofile.save()

	template = 'pages/account/edit.html'
	context = {

	}

	return render(request, template, context)


class LogoutView(RedirectView):
	permanent = False
	query_string = True
	pattern_name = 'home'

	def get_redirect_url(self, *args, **kwargs):
		logout(self.request)
		return super().get_redirect_url(*args, **kwargs)
@login_required
def friendship_request(request, id):
	try:
		reci = User.objects.get(id=id)
	except:
		pass

	req = None

	try:
		req = request.user.i_sender.get(recipient=reci)		
	except:
		freq = request.user.i_sender.create(recipient=reci)

	if req is not None:
		req.delete()

	return HttpResponseRedirect(request.GET.get('n', '/'));

class DialogsView(View):
	def get(self, request):
		chats = Chat.objects.filter(members__in=[request.user.id])
		return render(request, 'pages/mail/mail.html', {'user_profile': request.user, 'chats': chats})

class MessagesView(View):
	def get(self, request, chat_id):
		try:
			chat = Chat.objects.get(id=chat_id)
			if request.user in chat.members.all():
				chat.message_set.filter(is_readed=False).exclude(author=request.user).update(is_readed=True)
			else:
				chat = None
		except Chat.DoesNotExist:
			chat = None
 		
		return render(
			request,
			'pages/mail/mail_view.html',
			{
				'user_profile': request.user,
				'chat': chat,
				'form': MessageForm()
			}
		)
 
	def post(self, request, chat_id):
		form = MessageForm(data=request.POST)
		if form.is_valid():
			message = form.save(commit=False)
			message.chat_id = chat_id
			message.author = request.user
			message.save()
		return HttpResponseRedirect(reverse('messages', kwargs={'chat_id': chat_id}))

class CreateDialogView(View):
	def get(self, request, user_id):
		chats = Chat.objects.filter(members__in=[request.user.id, user_id], type=Chat.DIALOG).annotate(c=Count('members')).filter(c=2)
		if chats.count() == 0:
			chat = Chat.objects.create()
			chat.members.add(request.user)
			chat.members.add(user_id)
		else:
			chat = chats.first()
		return HttpResponseRedirect(reverse('messages', kwargs={'chat_id': chat.id}))

class CreateChatView(View):
	def get(self, request, user_id):
		chats = Chat.objects.filter(members__in=[request.user.id, user_id], type=Chat.CHAT)
		if chats.count() == 0:
			chat = Chat.objects.create()
			chat.members.add(request.user)
			chat.members.add(user_id)
		else:
			chat = chats.first()
		return HttpResponseRedirect(reverse('messages', kwargs={'chat_id': chat.id}))

#===========================================================
#===========================================================
#
# ╔═══╗╔═══╗╔══╗
# ║╔═╗║║╔═╗║╚╣─╝
# ║║─║║║╚═╝║─║║─
# ║╚═╝║║╔══╝─║║─
# ║╔═╗║║║───╔╣─╗
# ╚╝─╚╝╚╝───╚══╝
#
#===========================================================
#===========================================================
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions

class PostAPIAdd(APIView):

	authentication_classes = [authentication.SessionAuthentication]
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request, format=None):
		post_text = self.request.query_params['text']

		user = self.request.user

		added = False
		postid = None

		if user.is_authenticated:
			if post_text: 
				created_post = user.post_set.create(post_text = post_text)

				added = True
				postid = created_post.id

		data = {
			'added': added,
			'postid': postid,
		}

		return Response(data)

class PostAPIRemove(APIView):

	authentication_classes = [authentication.SessionAuthentication]
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request, postid=None, format=None):
		obj = get_object_or_404(Post, pk=postid)
		user = self.request.user

		removed = False

		if user.is_authenticated:
			if obj and obj.author == user:
				obj.delete()
				removed = True

		data = {
			'removed': removed
		}

		return Response(data)

class PostAPIUpdate(APIView):

	authentication_classes = [authentication.SessionAuthentication]
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request, postid=None, post_text='', format=None):
		obj = get_object_or_404(Post, pk=postid)
		user = self.request.user

		updated = False

		if user.is_authenticated:
			if obj and obj.author == user and post_text:
				obj.post_text = post_text
				obj.save()
				updated = True

		data = {
			'updated': updated
		}

		return Response(data)

class PostAPIGet(APIView):

	authentication_classes = [authentication.SessionAuthentication]
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request, postid=None, format=None):
		obj = get_object_or_404(Post, pk=postid)

		data = {
			'text': obj.post_text,
			'author': self.request.user.id
		}

		return Response(data)

class PostLikeAPIToggle(APIView):

	authentication_classes = [authentication.SessionAuthentication]
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request, postid=None, format=None):
		obj = get_object_or_404(Post, pk=postid)
		user = self.request.user

		updated = False
		liked = False

		if user.is_authenticated:
			if user in obj.likes.all():
				obj.likes.remove(user)
				liked = False
			else:
				obj.likes.add(user)
				liked = True
			updated = True

		likes = obj.likes.count()

		data = {
			'updated': updated,
			'liked': liked,
			'likes': likes,
		}

		return Response(data)

class PostAPIAddComment(APIView):

	authentication_classes = [authentication.SessionAuthentication]
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request, postid=None, format=None):
		comm_text = self.request.query_params['text']

		user = self.request.user

		success = False

		pub_date = None;

		if user.is_authenticated:
			if postid and comm_text: 
				post = get_object_or_404(Post, id=postid)
				if post is not None:
					created_comment = user.postcomment_set.create(post=post, comment_text=comm_text)
					pub_date = created_comment.published_date
					success = True

		data = {
			'success': success,
			'comment_text': comm_text,
			'pub_date': pub_date,
			'author_name': user.first_name + ' ' + user.last_name,
			'author_id': user.id,
			'author_avatar': user.userprofile.avatar,
		}

		return Response(data)

class UserAPICreate(APIView):

	authentication_classes = []
	permission_classes = []

	def get(self, request, username='', email='', password='', first_name='', last_name='', format=None):

		success = False
		userid = 0

		if username and email and password and first_name and last_name:
			created_user = User.objects.create(username, email, password)
			created_user.first_name = first_name
			created_user.last_name = last_name
			created_user.save()

			userid = created_user.id
			success = True

		data = {
			'userid': userid,
			'success': success
		}

		return Response(data)

class UserAPIGet(APIView):
	authentication_classes = []
	permission_classes = []

	def get(self, username='', password='', format=None):

		success = False

		if username and password:
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				try:
					prfile = UserProfile.objects.get(user=request.user)
				except:
					UserProfile.objects.create(user=request.user)

		data = {
			'success': success,
		}

		return Response(data)

class UserAPIUpdate(APIView):

	authentication_classes = [authentication.SessionAuthentication]
	permission_classes = [permissions.IsAuthenticated]

	def get(self, format=None):

		first_name = self.request.query_params['first_name']
		last_name = self.request.query_params['last_name']
		birth_date = self.request.query_params['birth_date']

		success = False
		user = self.request.user

		if first_name:
			user.first_name = first_name

		if last_name:
			user.last_name = last_name

		if birth_date:
			user.userprofile.birth_date = birth_date


		user.save()
		user.userprofile.save()

		success = True

		data = {
			'success': success,
			'birth_date': birth_date,
		}

		return Response(data)

class UserAPIUpdateStatus(APIView):

	authentication_classes = [authentication.SessionAuthentication]
	permission_classes = [permissions.IsAuthenticated]

	def get(self, format=None):

		status = self.request.query_params['text']

		success = False
		user = self.request.user
		
		user.userprofile.status = status

		user.save()
		user.userprofile.save()

		success = True

		data = {
			'success': success,
		}

		return Response(data)

class UserAPIFriends(APIView):

	authentication_classes = [authentication.SessionAuthentication]
	permission_classes = [permissions.IsAuthenticated]

	def get(self, format=None):
		user_id = int(self.kwargs.get('user_id', 0))
		user = get_object_or_404(User, id=user_id)

		friends = []

		if user is not None:
			friends = getFriends(user)

		data = {
			'friends': user.id,
		}

		return Response(data)

class ChatAPICreateDialog(APIView):

	authentication_classes = [authentication.SessionAuthentication]
	permission_classes = [permissions.IsAuthenticated]

	def get(self, format=None):
		chat = Chat.objects.create()

		users_id = [int(x) for x in self.kwargs.get('users_id', 0).split('_')[:2]]
		[chat.add(User.objects.get(id=id)) for id in users_id if get_object_or_404(User, id = id) is not None]

		chat.dialog = True

		data = {
			'id': chat.id,
		}

		return Response(data)

class ChatAPIMessagesRead(APIView):

	authentication_classes = [authentication.SessionAuthentication]
	permission_classes = [permissions.IsAuthenticated]

	def get(self, format=None, chat_id=''):

		def set_read(user, message, chat):
			message.is_readed = True
			if not message in chat.message_set.all().filter(readers__in=[user]):
				message.readers.add(user)
			message.save()

		chat = get_object_or_404(Chat, pk=int(chat_id))
		messages = chat.message_set.all()

		[set_read(self.request.user, x, chat) for x in messages]

		data = {}

		return Response(data)

class ChatAPIMessagesUnreaded(APIView):

	authentication_classes = [authentication.SessionAuthentication]
	permission_classes = [permissions.IsAuthenticated]

	def get(self, format=None, chat_id=''):
		chat = get_object_or_404(Chat, pk=int(chat_id))
		messages = chat.message_set.all()
		count = messages.filter(readers__in=[self.request.user.id]).count()

		data = {
			'count': messages.count() - count,
		}

		return Response(data)

class ChatAPIMessagesSend(APIView):

	authentication_classes = [authentication.SessionAuthentication]
	permission_classes = [permissions.IsAuthenticated]

	def get(self, format=None):

		def set_read(user, message, chat):
			if not message in chat.message_set.all().filter(readers__in=[user]):
				message.readers.add(user)
			message.save()

		chat_id = int(self.request.query_params['chat_id'])
		txt = self.request.query_params['text']
		chat = get_object_or_404(Chat, pk=int(chat_id))

		messageid = 0
		success = False

		if chat is not None and txt:
			author = self.request.user
			message = chat.message_set.create(author=author, message=txt)
			messageid = message.id
			set_read(author, message, chat)
			success = True

		data = {
			'success': success,
			'msg_id': messageid,
			'curr_time': str(timezone.now().hour) + ":" + str(timezone.now().minute)
		}

		return Response(data)

class ChatAPIMessagesRemove(APIView):

	authentication_classes = [authentication.SessionAuthentication]
	permission_classes = [permissions.IsAuthenticated]

	def get(self, format=None, message_id=None):
		obj = get_object_or_404(Message, pk=message_id)
		user = self.request.user

		removed = False

		if user.is_authenticated:
			if obj and obj.author == user:
				obj.delete()
				removed = True

		data = {
			'removed': removed
		}

		return Response(data)

class ChatAPIMessagesGetUnreaded(APIView):

	authentication_classes = [authentication.SessionAuthentication]
	permission_classes = [permissions.IsAuthenticated]

	def get(self, format=None):
		chat_id = int(self.request.query_params['chat_id'])
		chat = get_object_or_404(Chat, pk=int(chat_id))

		message = None
		message_text = ''
		success = False
		messageid = 0
		
		user_firstname = ''
		user_lastname = ''
		user_avatar = ''
		user_id = 0

		if chat is not None:
			try:
				message = chat.message_set.filter(is_readed=False).exclude(author=self.request.user).all()[0]
				message_text = message.message
				messageid = message.id
				message.is_readed=True
				message.save()
				success = True

				user_firstname = message.author.first_name
				user_lastname = message.author.last_name
				user_avatar = message.author.userprofile.avatar
				user_id = message.author.id
			except Exception as e:
				pass

		data = {
			'success': success,
			'text': message_text,
			'msg_id': messageid,
			'curr_time': str(timezone.now().hour) + ":" + str(timezone.now().minute),
			'user_firstname': user_firstname,
			'user_lastname': user_lastname,
			'user_avatar': user_avatar,
			'user_id': user_id
		}

		return Response(data)