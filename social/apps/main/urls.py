from django.urls import path

from . import views

urlpatterns = [
	path('', views.homepage, name='home'),
	path('id<int:id>', views.profile, name='profile'),
	path('friends<int:user_id>', views.FriendsView.as_view(), name='friends'),
	path('edit', views.edit_profile, name='edit_profile'),
	path('friendship_request/<int:id>', views.friendship_request, name='friendship_request'),

	path('telegraph', views.DialogsView.as_view(), name='dialogs'),
	path('telegraph/dialogue/start/<user_id>', views.CreateDialogView.as_view(), name='start_dialog'),
	path('telegraph/dialogue/<chat_id>', views.MessagesView.as_view(), name='messages'),

	path('logout/', views.LogoutView.as_view(), name='logout'),
	
	# api
	# user posts
	path('api/add_post', views.PostAPIAdd.as_view(), name='post_create'),
	path('post_<int:postid>/update/<post_text>', views.PostAPIUpdate.as_view(), name='post_update'),
	path('post_<int:postid>/remove', views.PostAPIRemove.as_view(), name='post_remove'),
	path('post_<int:postid>/like', views.PostLikeAPIToggle.as_view(), name='post_like'),

	path('post_<int:postid>/comment', views.PostAPIAddComment.as_view(), name='post_comment'),

	# user
	path('user_create/<username>_<email>_<password>_<first_name>_<last_name>', views.UserAPICreate.as_view(), name='create_user'),
	path('user_update', views.UserAPIUpdate.as_view(), name='update_user'),
	path('user_update_status', views.UserAPIUpdateStatus.as_view(), name='update_status_user'),
	path('user_friendlist', views.UserAPIFriends.as_view(), name='friends_user'),

	# chat
	path('api/read/<chat_id>', views.ChatAPIMessagesRead.as_view(), name='api_read_messages'),
	path('api/get_unreaded/<chat_id>', views.ChatAPIMessagesUnreaded.as_view(), name='api_unreaded_messages'),
	path('api/send_message', views.ChatAPIMessagesSend.as_view(), name='api_send_message'),
	path('api/remove_message/<message_id>', views.ChatAPIMessagesRemove.as_view(), name='api_remove_message'),
	path('api/get_last_unreaded_message', views.ChatAPIMessagesGetUnreaded.as_view(), name='api_getlast_message'),

	#path('get_mark_status/<int:id>', views.get_mark_status),
	#path('get_marks_count/<int:id>', views.get_marks_count),
	#path('/mail<int:id>', views.profile, name='mail'),
]