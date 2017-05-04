window.define('utils', function(require, exports, module) {

    exports.getUser = function (token) {
        return $.ajax({
            url: "/api/users/current",
            dataType: 'json',
            cache: false,
            headers: {
                'Authorization': 'Token ' + token,
            }
        });
    };

    exports.submitUser = function(user, token) {
        return $.ajax({
            url: "/api/users/" + user.id + '/',
            dataType: 'json',
            type: 'PUT',
            data: JSON.stringify(user),
            contentType: 'application/json',
            headers: {
                'Authorization': 'Token ' + token
            },
        });
    };

    exports.loadTeams = function() {
        return $.ajax({
            url: "/api/teams/",
            dataType: 'json',
            cache: false,
        });
    };

    exports.loadEvents = function(token) {
        // TODO: events page
        return $.ajax({
            url: "/api/events/",
            dataType: 'json',
            cache: false,
            headers: {
                'Authorization': 'Token ' + token
            },
        });
    };

    exports.validatePhoneInit = function (token) {
        return $.ajax({
            url: "/accounts/phone_validate/",
            dataType: 'json',
            cache: false,
            headers: {
                'Authorization': 'Token ' + token
            },
        });
    };

    exports.validatePhoneCheck = function(code, token) {
        return $.ajax({
            url: "/accounts/phone_validate/",
            dataType: 'json',
            type: 'POST',
            data: JSON.stringify({
                'code': code
            }),
            contentType: 'application/json',
            headers: {
                'Authorization': 'Token ' + token
            },
        });
    };

    exports.loginUser = function (email, pass) {
        return $.ajax({
            url: "/rest-auth/login/",
            dataType: 'json',
            type: 'POST',
            data: JSON.stringify({
                'email': email,
                'password': pass
            }),
            contentType: 'application/json',
        });
    };

    var logout = exports.logout = function() {
        delete localStorage.token;
        renderAlert('Successfully logged out', 'success');
    };
    
    var loggedIn = exports.loggedIn = function() {
        return !!localStorage.token;
    };
    
    exports.resetPassword = function (uid, token, new_password1, new_password2) {
        return $.ajax({
            url: "/rest-auth/password/reset/confirm/",
            type: 'POST',
            data: {
                uid: uid,
                token: token,
                new_password1: new_password1,
                new_password2: new_password2,
            },
        });
    };

    exports.changePassword = function (token, old_password, new_password1, new_password2) {
        return $.ajax({
            url: "/rest-auth/password/change/",
            type: 'POST',
            data: {
                new_password1: new_password1,
                new_password2: new_password2,
                old_password: old_password
            },
            headers: {
                'Authorization': 'Token ' + token
            },
        });
    };

    exports.registerUser = function(email, password1, password2, timezone, phone_number) {
        return $.ajax({
            url: "/rest-auth/registration/",
            dataType: 'json',
            type: 'POST',
            data: JSON.stringify({
                'email': email,
                'password1': password1,
                'password2': password2,
                'time_zone': timezone,
                'phone_number': phone_number
            }),
            contentType: 'application/json',
        });
    };

    exports.emailReset = function (email) {
        return $.ajax({
            url: "/rest-auth/password/reset/",
            dataType: 'json',
            type: 'POST',
            data: JSON.stringify({
                email: email
            }),
            contentType: 'application/json',
        });
    };

    exports.confirmEmail = function (confirm_key) {
        $.ajax({
            url: "/rest-auth/registration/verify-email/",
            dataType: 'json',
            type: 'POST',
            data: JSON.stringify({
                key: confirm_key
            }),
            contentType: 'application/json',
        });
    };

    exports.watcherAPI = function (method, watcher, token) {
        var url = '/api/watchers/';

        if (method == 'POST') {
            url = url + 'create/';
        } else if (method == 'PUT' || method == 'DELETE') {
            url = url + watcher.id + '/';
        } else if (method == 'GET') {
            return $.ajax({
                url: url,
                dataType: 'json',
                cache: false,
                headers: {
                    'Authorization': 'Token ' + token
                },
            });
        } else {
            console.log('method type ' + method + ' is not supported');
            return;
        }
        return $.ajax({
            url: url,
            dataType: 'json',
            type: method,
            data: JSON.stringify(watcher),
            contentType: 'application/json',
            headers: {
                'Authorization': 'Token ' + token
            },
        });
    };

    // TODO: redo using redux
    var renderAlert = exports.renderAlert = function (msg, level) {
        var spalerts = document.querySelector('#spalerts');
        if (spalerts) {
            var alertDiv = document.createElement("div");
            alertDiv.className = 'alert alert-' + level + ' alert-dismissable fade in';

            var newButton = document.createElement('button');
            newButton.className = 'close';
            newButton.type= 'button';
            newButton.setAttribute("data-dismiss", "alert");
            newButton.setAttribute("aria-hidden", "true");
            newButton.textContent = 'x';

            var newText = document.createElement('span');
            newText.textContent = msg;

            alertDiv.appendChild(newButton);
            alertDiv.appendChild(newText);
            spalerts.appendChild(alertDiv);
        }
    };

    // TODO: redux and send callback when alerts are cleared
    exports.clearAlerts = function () {
        var spalerts = document.querySelector('#spalerts');
        for (var i = 0; i < spalerts.childNodes.length; i++) {
            spalerts.removeChild(spalerts.firstChild);
        }
    };

    exports.parseMessage = function (json) {
        var msg = 'An error occurred while processing your request';
        try {
            msg = Object.values(JSON.parse(json));
        }
        catch (e) {}
        return msg;
    };

    exports.getUrlParameter = function (sParam) {
        var sPageURL = decodeURIComponent(window.location.search.substring(1)),
            sURLVariables = sPageURL.split('&'),
            sParameterName,
            i;

        for (i = 0; i < sURLVariables.length; i++) {
            sParameterName = sURLVariables[i].split('=');

            if (sParameterName[0] === sParam) {
                return sParameterName[1] === undefined ? true : sParameterName[1];
            }
        }
    };
});
