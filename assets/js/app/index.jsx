window.define('index', function(require, exports, module) {

var ConfirmEmail = require('auth').ConfirmEmail;
var ForgotPassForm = require('auth').ForgotPassForm;
var Home = require('app').Home;
var LoginForm = require('auth').LoginForm;
var RegisterForm = require('auth').RegisterForm;
var logout = require('utils').logout;
var loggedIn = require('utils').loggedIn;
var Watchers = require('watchers').Watchers;
var ResetPassForm = require('auth').ResetPassForm;
var Settings = require('app').Settings;

var browserHistory = ReactRouter.browserHistory;

var Alert = ReactBootstrap.Alert;
var Button = ReactBootstrap.Button;
var MenuItem = ReactBootstrap.MenuItem;
var Navbar = ReactBootstrap.Navbar;
var Nav = ReactBootstrap.Nav;
var NavItem = ReactBootstrap.NavItem;
var NavDropdown = ReactBootstrap.NavDropdown;

var destination = document.querySelector("#container");

// es6 automatically prefix these with ReactRouter;
var { Router,
      Route,
      IndexRoute,
      IndexLink,
      Link } = ReactRouter;

var SafeAnchor = React.createClass({
    render: function() {
        return (
          <li>
              <Link to={this.props.href}>{this.props.children}</Link>
          </li>
        );
    }
});

function requireAuth(nextState, replace) {
    if (!loggedIn()) {
        replace({ 
            pathname:'/login',
            state: {nextPathname: this.path}
        });
    }
}

var AlertDismissable = React.createClass({
  getInitialState() {
    return {
      alertVisible: true
    };
  },

  render() {
    if (this.state.alertVisible) {
      return (
        <Alert bsStyle="danger" onDismiss={this.handleAlertDismiss}>
          <h4>Oh snap! You got an error!</h4>
          <p>dumb dumb dumb</p>
          <p>
            <Button bsStyle="danger">Take this action</Button>
            <span> or </span>
            <Button onClick={this.handleAlertDismiss}>Hide Alert</Button>
          </p>
        </Alert>
      );
    }

    return (
      <Button onClick={this.handleAlertShow}>Show Alert</Button>
    );
  },

  handleAlertDismiss() {
    this.setState({alertVisible: false});
  },

  handleAlertShow() {
    this.setState({alertVisible: true});
  }
});

var AppNav = React.createClass({
    contextTypes: {
        router: React.PropTypes.object.isRequired
    },
    logoutHandler: function() {
        logout();
        this.context.router.replace('/login');
    },
    render: function() {
        var loginLink, logoutLink, registerLink, settingsLink, warningsLink;
        if (loggedIn()) {
            logoutLink = <NavItem onClick={this.logoutHandler} eventKey={3.1}>LOGOUT</NavItem>;
            settingsLink = <SafeAnchor href="/settings">SETTINGS</ SafeAnchor>;
            warningsLink = <SafeAnchor href="/watchers">WARNINGS</ SafeAnchor>;
        } else {
            loginLink = <SafeAnchor href="/login">LOGIN</ SafeAnchor>;
            registerLink = <SafeAnchor href="/register">SIGN UP</ SafeAnchor>;
        }
        return <div className="row">
            <Navbar>
                <Navbar.Header>
                    <Navbar.Brand>
                        <IndexLink to="/">SPORTS WARNING</IndexLink>
                    </Navbar.Brand>
                    <Navbar.Toggle />
                </Navbar.Header>
                <Navbar.Collapse>
                    <Nav pullRight>
                        {loginLink}
                        {registerLink}
                        {warningsLink}
                        {settingsLink}
                        {logoutLink}
                    </Nav>
                </Navbar.Collapse>
            </Navbar>
        </div>;
    }
});

var App = React.createClass({
  contextTypes: {
    router: React.PropTypes.object.isRequired
  },
  hideAlert: function() {
  },
  render: function() {
    contentClass = 'content all-red';
    if (loggedIn()) {
        contentClass = 'content';
    }
    return (
        <div>
            <AppNav />
            <div>
                <div className={contentClass}>
                    <div className="col-md-6 col-xs-10 col-centered">
                        <div id="spalerts">
                        </div>
                        {this.props.children}
                    </div>
                </div>
            </div>
        </div>
    );
  }
});

var Render404 = React.createClass({
    render: function() {
        return (
            <div className="form-top text-center">
                <h3>404 - NOT FOUND</h3>
            </div>
        );
    }
});

ReactDOM.render(
    <Router history={browserHistory}>              
        <Route path="/" component={App}>
            <IndexRoute component={Home} />
            <Route path="settings" component={Settings} onEnter={requireAuth} />
            <Route path="login" component={LoginForm} />
            <Route path="register" component={RegisterForm} />
            <Route path="reset-pass" component={ForgotPassForm} />
            <Route path="watchers" component={Watchers} onEnter={requireAuth} />
            <Route path="accounts">
                <Route path="reset/:uid/:token" component={ResetPassForm} />
                <Route path="confirm-email/:conf_key" component={ConfirmEmail} />
            </Route>
            <Route path="rest-auth">
                <Route path="registration">
                </Route>
            </Route>
            <Route path='*' component={Render404} />
 
        </Route>
    </Router>,
    destination
);
});
