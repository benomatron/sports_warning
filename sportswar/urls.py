from django.conf.urls import include, url
from django.contrib import admin

import sportswar.users.api as users_api
import sportswar.events.api as events_api
import sportswar.teams.api as teams_api

from sportswar.events.views import IndexView

urlpatterns = [
    # Overrides account_confirm_email from allauth
    url(r"^accounts/confirm-email/(?P<key>[-:\w]+)/$", IndexView.as_view(), name="account_confirm_email"),
    url(r'^accounts/confirm-email/$', IndexView.as_view(), name='account_email_verification_sent'),
    # Used by reset email template
    url(r'^accounts/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        IndexView.as_view(), name='password_reset_confirm'),
    url(r'^accounts/phone_validate/$', users_api.VerifyPhoneView.as_view(), name='verify-phone'),

    # rest-auth
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),

    # allauth
    url(r'^accounts/', include('allauth.urls')),

    # rest_framework
    url(r'^api/watchers/$', events_api.WatcherListView.as_view(), name='watch-list'),
    url(r'^api/watchers/create/$', events_api.WatcherCreateView.as_view(), name='watch-create'),
    url(r'^api/watchers/(?P<pk>[0-9]+)/$', events_api.WatcherDetailView.as_view(), name='watch-detail'),
    url(r'^api/teams/$', teams_api.TeamListView.as_view(), name='team-list'),
    url(r'^api/teams/(?P<pk>[0-9]+)/$', teams_api.TeamDetailView.as_view(), name='team-detail'),
    url(r'^api/users/$', users_api.UserListView.as_view(), name='user-list'),
    url(r'^api/users/current', users_api.CurrentUser.as_view(), name='user-current'),
    url(r'^api/users/(?P<pk>[0-9]+)/$', users_api.UserDetailView.as_view(), name='user-detail'),

    # app
    url(r'^admin/', admin.site.urls),
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^.*$', IndexView.as_view(), name='app'),

]
