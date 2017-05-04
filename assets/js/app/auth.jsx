window.define('auth', function(require, exports, module) {

var deepCopy = require('../deepcopy');

var utils = require('utils');

var Button = ReactBootstrap.Button;
var Col = ReactBootstrap.Col;
var ControlLabel = ReactBootstrap.ControlLabel;
var Form = ReactBootstrap.Form;
var FormControl = ReactBootstrap.FormControl;
var FormGroup = ReactBootstrap.FormGroup;
var HelpBlock = ReactBootstrap.HelpBlock;


var ResetPassForm = exports.ResetPassForm = React.createClass({
    contextTypes: {
        router: React.PropTypes.object.isRequired
    },
    getInitialState: function() {
        return {
            uid: this.props.params.uid,
            token: this.props.params.token,
            new_password1: null,
            new_password2: null,
            msg: null
        };
    },
    handleSubmit: function(e) {
        e.preventDefault();
        var msg;
        if (!this.state.new_password1 || !this.state.new_password2) {
            msg = 'Please complete all required fields';
            this.setState({msg: {txt: msg, level: 'warning'}});
            return;
        }
        if (!this.state.uid || !this.state.token) {
            msg = 'Reset token has expired, please try again.';
            this.setState({msg: {txt: msg, level: 'warning'}});
            return;
        }
        $.when(utils.resetPassword(this.state.uid, this.state.token, this.state.new_password1, this.state.new_password2))
            .done(function (data) { 
                utils.clearAlerts();
                utils.renderAlert('Password has been reset.', 'success');
                this.context.router.replace('/login');
            }.bind(this))
            .fail(function (xhr) {
                var msg = utils.parseMessage(xhr.responseText);
                this.setState({msg: {txt: msg, level: 'warning'}});
            }.bind(this));
    },
    handleChangePass1: function(e) {
        this.setState({new_password1: e.target.value});
    },
    handleChangePass2: function(e) {
        this.setState({new_password2: e.target.value});
    },
    render: function() {
        var help, helpLevel;
        if (this.state.msg && this.state.msg.txt) {
            help = this.state.msg.txt;
            helpLevel = 'message-' + this.state.msg.level;
        }
        return (
            <div className="form-top">
                <Form horizontal onSubmit={this.handleSubmit}>
                    <FormGroup>
                        <Col xs={10} xsOffset={1}>
                            <h4>RESET PASSWORD</h4>
                            <hr />
                        </Col>
                        <Col xs={10} xsOffset={1}>
                            <HelpBlock>New password</HelpBlock>
                            <FormControl
                              type="password"
                              onChange={this.handleChangePass1}
                            />
                        </Col>
                    </FormGroup>
                    <FormGroup>
                        <Col xs={10} xsOffset={1}>
                            <HelpBlock>Confirm new password</HelpBlock>
                            <FormControl
                              type="password"
                              onChange={this.handleChangePass2}
                            />
                        </Col>
                    </FormGroup>
                    <FormGroup>
                        <Col xs={10} xsOffset={1}>
                            <HelpBlock className={helpLevel}>{help}</HelpBlock>
                        </Col>
                    </FormGroup>
                    <FormGroup>
                        <Col xs={10} xsOffset={1}>
                            <Button type="submit" bsStyle="success" bsSize="small" className="pull-right">
                                RESET PASSWORD 
                            </Button>
                        </Col>
                    </FormGroup>
                </Form>
            </div>
        );
      }
});

var ChangePasswordForm = exports.ChangePasswordForm = React.createClass({
    getInitialState: function() {
      return {old_password: null, new_password1: null, new_password2: null};
    },
    handleSubmit: function(e) {
      e.preventDefault();
      if (!this.state.old_password || !this.state.new_password1 || !this.state.new_password2) {
          this.props.updateMessage('Please complete all required fields', 'warning');
          return;
      }
      $.when(utils.changePassword(localStorage.token, this.state.old_password, this.state.new_password1, this.state.new_password2))
          .done(function (data) {
              this.props.toggleChangePass();
              this.props.updateMessage('Successfully changed password', 'success');
          }.bind(this))
          .fail(function (xhr, status, err) {
              var msg = utils.parseMessage(xhr.responseText);
              this.props.updateMessage(msg, 'warning');
          }.bind(this));
    },
    handleChangeOld: function(e) {
      this.setState({old_password: e.target.value});
    },
    handleChangePass1: function(e) {
      this.setState({new_password1: e.target.value});
    },
    handleChangePass2: function(e) {
      this.setState({new_password2: e.target.value});
    },
    render: function() {
        return (
            <div>
                <Form horizontal className="change-pass-form" onSubmit={this.handleSubmit}>
                    <FormGroup>
                        <Col xs={8} xsOffset={1}>
                            <HelpBlock>Old password</HelpBlock>
                            <FormControl
                              type="password"
                              onChange={this.handleChangeOld}
                            />
                        </Col>
                    </FormGroup>
                    <FormGroup>
                        <Col xs={8} xsOffset={1}>
                            <HelpBlock>New password</HelpBlock>
                            <FormControl
                              type="password"
                              onChange={this.handleChangePass1}
                            />
                        </Col>
                    </FormGroup>
                    <FormGroup>
                        <Col xs={8} xsOffset={1}>
                            <HelpBlock>Again</HelpBlock>
                            <FormControl
                              type="password"
                              onChange={this.handleChangePass2}
                            />
                        </Col>
                    </FormGroup>
                    <FormGroup>
                        <Col xs={7} xsOffset={2} className="text-right">
                            <Button type="button" bsSize="small" bsStyle="link" onClick={this.props.toggleChangePass}>
                                CANCEL
                            </Button>
                            <Button type="submit" bsSize="small" bsStyle="primary">
                                SUBMIT 
                            </Button>
                        </Col>
                    </FormGroup>
                </Form>
            </div>
        );
    }
});

var RegisterForm = exports.RegisterForm = React.createClass({
    contextTypes: {
        router: React.PropTypes.object.isRequired
    },
    getInitialState: function() {
        return {
            email: null,
            password1: null,
            password2: null,
            timezone: null,
            phone_number: '',
            msg: null
        };
    },
    handleSubmit: function(e) {
        e.preventDefault();
        if (!this.state.email || !this.state.password1 || !this.state.password2 || !this.state.timezone) {
            this.setState({msg: {txt: 'Please complete all required fields', level: 'error'}});
            return;
        }
        // TODO: some phone validation here
        if (this.state.phone_number.length > 0 && this.state.phone_number < 10) {
            this.setState({msg: {txt: 'Please enter a valid 10 digit phone number', level: 'error'}});
            return;
        }
        // probably want to have defaults for this
        $.when(utils.registerUser(this.state.email, this.state.password1, this.state.password2, this.state.timezone, this.state.phone_number))
            .done(function (data) {
                this.context.router.replace('/login');
                this.setState({msg: {}});
                utils.renderAlert('Thank you! Please check your email to complete the registration process, look in the spam folder if you don\'t see it.', 'success');
            }.bind(this))
            .fail(function (xhr) {
                var msg = utils.parseMessage(xhr.responseText);
                this.setState({msg: {txt: msg, level: 'error'}});
            }.bind(this));
    },
    handleChangePass: function(e) {
        this.setState({password1: e.target.value});
    },
    handleChangePass2: function(e) {
        this.setState({password2: e.target.value});
    },
    handleChangeEmail: function(e) {
        this.setState({email: e.target.value});
    },
    // TODO: dry the phone and timezone forms
    handleChangeNumber: function(e) {
        var val = e.target.value.replace(/[^\d]/g,'');
        val = val.slice(0, 10);
        this.setState({phone_number: val});
    },
    handleChangeTZ: function(e) {
        this.setState({timezone: e.target.value});
    },
    render: function() {
        var help, helpLevel, timezoneOptions;
        timezoneOptions = [
            <option key={0} value="">Please select your time zone</option>,
            <option key={1} value="US/Eastern">US/Eastern</option>,
            <option key={2} value="US/Central">US/Central</option>,
            <option key={3} value="US/Pacific">US/Pacific</option>,
            <option key={4} value="US/Mountain">US/Mountain</option>,
            <option key={5} value="US/Arizona">US/Arizona</option>,
            <option key={6} value="US/Michigan">US/Michigan</option>,
            <option key={7} value="US/Hawaii">US/Hawaii</option>,
            <option key={8} value="US/East-Indiana">US/East-Indiana</option>,
            <option key={9} value="US/Indiana-Starke">US/Indiana-Starke</option>
        ];
        if (this.state.msg && this.state.msg.txt) {
            help = this.state.msg.txt;
            helpLevel = 'message-' + this.state.msg.level;
        }
        return (
            <div className='form-top'>
                <Form horizontal onSubmit={this.handleSubmit}>
                    <FormGroup>
                        <Col xs={10} xsOffset={1}>
                            <h4>SIGN UP</h4>
                            <hr />
                        </Col>
                        <Col xs={10} xsOffset={1}>
                            <HelpBlock>Email</HelpBlock>
                            <FormControl
                              type="email"
                              placeholder="chaz@example.com"
                              onChange={this.handleChangeEmail}
                            />
                        </Col>
                    </FormGroup>
                    <FormGroup>
                        <Col xs={10} xsOffset={1}>
                            <HelpBlock>Password</HelpBlock>
                            <FormControl
                              type="password"
                              placeholder="password"
                              onChange={this.handleChangePass}
                            />
                        </Col>
                    </FormGroup>
                    <FormGroup>
                        <Col xs={10} xsOffset={1}>
                            <HelpBlock>Confirm password</HelpBlock>
                            <FormControl
                              type="password"
                              placeholder="confirm password"
                              onChange={this.handleChangePass2}
                            />
                        </Col>
                    </FormGroup>
                    <FormGroup>
                        <Col xs={10} xsOffset={1}>
                            <HelpBlock>Your time zone</HelpBlock>
                            <FormControl
                                componentClass="select"
                                placeholder="Select your time zone"
                                value={this.state.timezone || ''}
                                onChange={this.handleChangeTZ}>
                                {timezoneOptions}
                            </FormControl>
                        </Col>
                    </FormGroup>
                    <FormGroup>
                        <Col xs={10} xsOffset={1}>
                            <HelpBlock>Phone Number (if you want SMS alerts)</HelpBlock>
                            <FormControl
                              type="text"
                              value={this.state.phone_number || ''}
                              placeholder="5551234567"
                              onChange={this.handleChangeNumber}
                            />
                        </Col>
                    </FormGroup>
                    <FormGroup>
                        <Col xs={10} xsOffset={1}>
                            <HelpBlock className={helpLevel}>{help}</HelpBlock>
                        </Col>
                    </FormGroup>
                    <FormGroup>
                        <Col xs={10} xsOffset={1}>
                            <Button type="submit" bsStyle="success" bsSize="small" className="pull-right">
                                SIGN UP
                            </Button>
                        </Col>
                    </FormGroup>
                </Form>
            </div>
        );
    }
});

var LoginForm = exports.LoginForm = React.createClass({
    contextTypes: {
        router: React.PropTypes.object.isRequired
    },
    getInitialState: function() {
        var nextUrl = '/watchers/';
        if (this.props.location && this.props.location.state) {
            nextUrl = this.props.location.state.nextPathname || nextUrl;
        }
        return {email: null, password: null, nextUrl: nextUrl, msg: null};
    },
    handleSubmit: function(e) {
        e.preventDefault();
        if (!this.state.email || !this.state.password) {
            this.setState({msg: {txt: 'Please complete all required fields', level: 'error'}});
            return;
        }
        $.when(utils.loginUser(this.state.email, this.state.password))
            .done(function (res) {
                if (res.key) {
                    utils.clearAlerts();
                    localStorage.token = res.key;
                    this.context.router.replace(this.state.nextUrl);
                } else {
                    this.setState({msg: {txt: 'Incorrect email or password', level: 'error'}});
                }
            }.bind(this))
            .fail(function(xhr, status, err) {
                var msg = utils.parseMessage(xhr.responseText);
                this.setState({msg: {txt: msg, level: 'error'}});
            }.bind(this));
    },
    handleChangeName: function(e) {
        this.setState({email: e.target.value});
    },
    handleChangePass: function(e) {
        this.setState({password: e.target.value});
    },
    redirectPass: function(e) {
        this.context.router.replace('/reset-pass');
    },
    render: function() {
        var help, helpLevel;
        if (this.state.msg && this.state.msg.txt) {
            help = this.state.msg.txt;
            helpLevel = 'message-' + this.state.msg.level;
        }
        return (
            <div className='form-top'>
                <Form horizontal onSubmit={this.handleSubmit}>
                    <FormGroup>
                        <Col xs={10} xsOffset={1}>
                            <h4>LOGIN</h4>
                            <hr />
                        </Col>
                        <Col xs={10} xsOffset={1}>
                            <HelpBlock>Email</HelpBlock>
                            <FormControl
                              type="text"
                              placeholder="chaz@bedazzler.com"
                              onChange={this.handleChangeName}
                            />
                        </Col>
                    </FormGroup>
                    <FormGroup>
                        <Col xs={10} xsOffset={1}>
                            <HelpBlock>Password</HelpBlock>
                            <FormControl
                              type="password"
                              placeholder="secret sauce"
                              onChange={this.handleChangePass}
                            />
                        </Col>
                    </FormGroup>
                    <FormGroup>
                        <Col xs={10} xsOffset={1}>
                            <HelpBlock className={helpLevel}>{help}</HelpBlock>
                        </Col>
                    </FormGroup>
                    <FormGroup>
                        <Col xs={5} xsOffset={1}>
                            <div className='secondary-text show-pointer' onClick={this.redirectPass}>Forgot password?</div>
                        </Col>
                        <Col xs={5}>
                            <Button type="submit" bsStyle="success" bsSize="small" className="pull-right">
                               LOGIN 
                            </Button>
                        </Col>
                    </FormGroup>
                </Form>
            </div>
        );
    }
});

var ConfirmEmail = exports.ConfirmEmail = React.createClass({
    contextTypes: {
        router: React.PropTypes.object.isRequired
    },
    getInitialState: function() {
        return {confirm_key: this.props.params.conf_key, confirmed: false};
    },
    componentWillReceiveProps: function(nextProps) {
        if (this.state.confirm_key !== nextProps.params.conf_key) {
            this.setState({confirm_key: nextProps.params.conf_key});
        }
    },
    componentDidMount: function() {
        if (this.state.confirm_key && !this.state.confirmed) {
            $.when(utils.confirmEmail(this.state.confirm_key))
                .done(function (data) {
                    utils.renderAlert('Successfully confirmed email! ', 'success');
                    this.setState({confirmed: true});
                    this.context.router.replace('/login');
                }.bind(this))
                .fail(function (xhr) {
                    var msg = utils.parseMessage(xhr.responseText);
                    utils.renderAlert(msg, 'error');
                }.bind(this));
        }
    },
    render: function() {
        var loginLink = <div>Confirming email...</div>;
        if (this.state.confirmed) {
            loginLink = <div>
                <div>Email confirmed!<a href='/login'> Login here.</a></div>
            </div>;
        }
        return (
          <div>
              {loginLink}
          </div>
        );
    }
});

var ForgotPassForm = exports.ForgotPassForm = React.createClass({
    contextTypes: {
        router: React.PropTypes.object.isRequired
    },
    getInitialState: function() {
        return {email: null, msg: null, sent: false};
    },
    handleSubmit: function(e) {
        e.preventDefault();
        if (!this.state.email) {
            this.setState({msg: {txt: 'Please enter a valid email', level: 'error'}});
            return;
        }
        $.when(utils.emailReset(this.state.email))
            .done(function (data) {
                this.setState({msg: {txt: 'A reset link has been sent to your email.', level: 'success'}, sent: true});
            }.bind(this))
            .fail(function (xhr) {
                var msg = utils.parseMessage(xhr.responseText);
                this.setState({msg: {txt: msg, level: 'success'}});
            }.bind(this));
    },
    handleChangeEmail: function(e) {
        this.setState({email: e.target.value});
    },
    goLogin: function(e) {
        this.context.router.replace('/login');
    },
    render: function() {
        var help, helpLevel;
        if (this.state.msg && this.state.msg.txt) {
          help = this.state.msg.txt;
          helpLevel = 'message-' + this.state.msg.level;
        }
        var resetButton = <Button type="submit" bsStyle="success" bsSize="small" className="pull-right">RESET PASSWORD</Button>;
        if (this.state.sent) {
            resetButton = <Button bsStyle="success" bsSize="small" className="pull-right" onClick={this.goLogin}>RETURN TO LOGIN</Button>;
        }
        return (
            <div className='form-top'>
                <Form horizontal onSubmit={this.handleSubmit}>
                    <FormGroup>
                        <Col xs={10} xsOffset={1}>
                            <HelpBlock>To reset your password please provide the email address that you used when you signed up for your account.</HelpBlock>
                            <FormControl
                                type="email address"
                                placeholder="willy@example.com"
                                onChange={this.handleChangeEmail}
                            />
                        </Col>
                    </FormGroup>
                    <FormGroup>
                        <Col xs={10} xsOffset={1}>
                            <HelpBlock className={helpLevel}>{help}</HelpBlock>
                        </Col>
                    </FormGroup>
                    <FormGroup>
                        <Col xs={10} xsOffset={1}>
                            {resetButton}
                        </Col>
                    </FormGroup>
                </Form>
            </div>
        );
    }
});

var ValidatePhoneForm = exports.ValidatePhoneForm = React.createClass({
    getInitialState: function() {
        return {validation_code: ''};
    },
    phoneValidationCheck: function() {
        $.when(utils.validatePhoneCheck(this.state.validation_code, localStorage.token))
            .done(function (data) {
                this.props.updateMessage('Your number has been validated.', 'success');
                this.props.cancelValidate();
            }.bind(this))
            .fail(function(xhr, status, err) {
                var msg;
                if (status === 500) {
                    msg = 'Error validating phone number';
                } else {
                    msg = utils.parseMessage(xhr.responseText);
                }
                this.props.updateMessage(msg, 'warning');
            }.bind(this));
    },
    phoneValidationInit: function() {
        $.when(utils.validatePhoneInit(localStorage.token))
            .done(function (data) {
                this.props.updateMessage('A validation code is being sent to your phone.', 'success');
            }.bind(this))
            .fail(function(xhr, status, err) {
                var msg;
                if (status === 500) {
                    msg = 'Error sending phone validation';
                } else {
                    msg = utils.parseMessage(xhr.responseText);
                }
                this.props.updateMessage(msg, 'warning');
            }.bind(this));
    },
    handleChangeCode: function(e) {
        this.setState({validation_code: e.target.value});
    },
    componentDidMount: function() {
        this.phoneValidationInit();
    },
    render: function() {
        return (
            <div>
                <div className="col-xs-12"><hr /></div>
                <Form horizontal onSubmit={this.handleSubmit}>
                    <FormGroup>
                        <Col xs={10} xsOffset={1}>
                            <HelpBlock>We have sent a code to your phone.  Enter it here to allow alerts via SMS.</HelpBlock>
                        </Col>
                    </FormGroup>
                    <FormGroup>
                        <Col xs={5} xsOffset={1}>
                            <FormControl
                              type="text"
                              placeholder="Code"
                              onChange={this.handleChangeCode}
                            />
                        </Col>
                        <Col xs={5} xsOffset={1}>
                            <Button type="button" bsSize="small" bsStyle="default" className="m-five-right" onClick={this.props.cancelValidate}>
                                CANCEL 
                            </Button>
                            <Button type="button" bsSize="small" bsStyle="primary" onClick={this.phoneValidationCheck}>
                                VALIDATE 
                            </Button>
                            <Button type="button" bsSize="small" bsStyle="link" onClick={this.phoneValidationInit}>
                                RESEND
                            </Button>
                        </Col>
                    </FormGroup>
                </Form>
            </div>
        );
    }
});
});
