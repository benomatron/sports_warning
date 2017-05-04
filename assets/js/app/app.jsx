window.define('app', function(require, exports, module) {

var deepCopy = require('../deepcopy');

var utils = require('utils');

var ChangePasswordForm = require('auth').ChangePasswordForm;
var LoginForm = require('auth').LoginForm;
var RegisterForm = require('auth').RegisterForm;
var ValidatePhoneForm = require('auth').ValidatePhoneForm;

var Button = ReactBootstrap.Button;
var Col = ReactBootstrap.Col;
var ControlLabel = ReactBootstrap.ControlLabel;
var Form = ReactBootstrap.Form;
var FormControl = ReactBootstrap.FormControl;
var FormGroup = ReactBootstrap.FormGroup;
var HelpBlock = ReactBootstrap.HelpBlock;
var Typeahead = ReactBootstrapTypeahead.default;


var Settings = exports.Settings = React.createClass({
    getUser: function () {
        $.when(utils.getUser(localStorage.token))
            .done(function (data) {
                this.setState({user: data});
            }.bind(this))
            .fail(function (xhr) {
                var msg = utils.parseMessage(xhr.responseText);
                this.setState({msg: {txt: msg, level: 'error'}});
            }.bind(this));
    },
    submitUser: function() {
        $.when(utils.submitUser(this.state.user, localStorage.token))
            .done(function (data) {
                this.setState({user: data, msg: {txt: 'User updated successfully.', level: 'success'}});
            }.bind(this))
            .fail(function(xhr) {
                var msg = utils.parseMessage(xhr.responseText);
                this.setState({msg: {txt: msg, level: 'error'}});
            }.bind(this));
    },
    getInitialState: function() {
        var defaultMsg = {txt: '', level: 'info'};
        return {
            user: [],
            msg: defaultMsg,
            defaultMsg: defaultMsg,
            isEditing: false,
            changingPass: false,
            validatingPhone: false
        };
    },
    componentDidMount: function() {
        this.getUser();
    },
    resetForm: function(e) {
        this.setState({isEditing: false, changingPass: false, validatingPhone: false, msg: {txt: '', level: 'info'}});
        this.getUser();
    },
    handleSubmit: function(e) {
        e.preventDefault();
        if (!this.state.user || !this.state.user.id || !this.state.user.email) {
            this.setState({msg: {txt: 'Empty values in form', level: 'warning'}});
            return;
        }
        if (this.state.user.phone_number && this.state.user.phone_number.length !== 10) {
            this.setState({msg: {txt: 'Please enter a valid 10 digit phone number', level: 'warning'}});
            return;
        }
        this.submitUser();
        this.setState({isEditing: false, changingPass: false, validatingPhone: false});
    },
    handleChangeName: function(e) {
        var user = deepCopy(this.state.user);
        user.display_name = e.target.value;
        this.setState({user: user, isEditing: true});
    },
    handleChangeNumber: function(e) {
        var val = e.target.value.replace(/[^\d]/g,'');
        var user = deepCopy(this.state.user);
        user.phone_number = val.slice(0, 10);
        this.setState({user: user, isEditing: true});
    },
    updateMessage: function(msgTxt, msgLevel) {
        this.setState({msg: {txt: msgTxt, level: msgLevel}});
    },
    toggleValidatePhone: function() {
        this.setState({validatingPhone: !this.state.validatingPhone});
        this.getUser();
    },
    toggleChangePass: function() {
        this.setState({changingPass: !this.state.changingPass, msg: this.state.defaultMsg});
    },
    handleChangeTZ: function(e) {
        var user = deepCopy(this.state.user);
        user.time_zone = e.target.value;
        this.setState({user: user, isEditing: true});
    },
    render: function() {
        var passForm, changePassButton, phoneForm, validPhoneButton, submitButtons, formDisabled, help, timezoneOptions;
        var helpLevel = 'message-info';

        // TODO: DRY
        timezoneOptions = [
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
        helpLevel = 'col-xs-10 col-xs-offset-1 settings-help ' + helpLevel;
        if (this.state.changingPass) {
            passForm = <ChangePasswordForm updateMessage={this.updateMessage} toggleChangePass={this.toggleChangePass} />;
        } else {
            changePassButton = <Button type="button" bsStyle="link" bsSize="small" disabled={this.state.validatingPhone || this.state.isEditing} onClick={this.toggleChangePass}>Change</Button>;
        }

        if (this.state.user.phone_number) {
            if (this.state.validatingPhone) {
                phoneForm = <ValidatePhoneForm updateMessage={this.updateMessage} cancelValidate={this.toggleValidatePhone} />;
            } else if (!this.state.user.has_validated_phone) {
                validPhoneButton = (
                    <Button type="button"
                            bsStyle="warning"
                            bsSize="small"
                            disabled={this.state.changingPass || this.state.isEditing}
                            onClick={this.toggleValidatePhone}>
                        Validate
                    </Button>
                );
            } else {
                validPhoneButton = <span className='validated-phone'><span className='glyphicon glyphicon-ok' aria-hidden="true"></span></span>;
            }
        }

        if (this.state.isEditing) {
            submitButtons = (
                <FormGroup>
                    <Col xsOffset={2} xs={7} className="text-right">
                        <Button type="button" bsSize="small" bsStyle="link" onClick={this.resetForm}>
                            CANCEL
                        </Button>
                        <Button type="submit" bsSize="small" bsStyle="primary" onSubmit={this.handleSubmit}>
                            SUBMIT 
                        </Button>
                    </Col>
                </FormGroup>
            );
        } else if (this.state.changingPass || this.state.validatingPhone) {
            formDisabled = true;
        }

        return (
            <div className="form-top">
                <div className="active-header">SETTINGS</div>
                <hr />
                <Form horizontal onSubmit={this.handleSubmit}>
                    <FormGroup>
                        <Col xs={8} xsOffset={1}>
                            <HelpBlock>Name</HelpBlock>
                            <FormControl
                              type="text"
                              value={this.state.user.display_name || ''}
                              disabled={formDisabled}
                              placeholder="Full Name"
                              onChange={this.handleChangeName}
                            />
                        </Col>
                    </FormGroup>
                    <FormGroup>
                        <Col xs={8} xsOffset={1}>
                            <HelpBlock>Email</HelpBlock>
                            <FormControl
                              type="text"
                              value={this.state.user.email || ''}
                              disabled={true}
                              placeholder="Email"
                            />
                        </Col>
                    </FormGroup>
                    <FormGroup>
                        <Col xs={8} xsOffset={1}>
                            <HelpBlock>Phone Number</HelpBlock>
                            <FormControl
                              type="text"
                              value={this.state.user.phone_number || ''}
                              disabled={formDisabled}
                              placeholder="Phone Number"
                              onChange={this.handleChangeNumber}
                            />
                        </Col>
                        <Col xs={3} className='top-offset-btn'>
                            {validPhoneButton}
                        </Col>
                    </FormGroup>
                    <FormGroup>
                        <Col xs={8} xsOffset={1}>
                            <HelpBlock>Time Zone</HelpBlock>
                            <FormControl
                                componentClass="select"
                                placeholder="Select your time zone"
                                value={this.state.user.time_zone || ''}
                                onChange={this.handleChangeTZ}>
                                {timezoneOptions}
                            </FormControl>
                        </Col>
                    </FormGroup>
                    <FormGroup>
                        <Col xs={8} xsOffset={1}>
                            <HelpBlock>Password</HelpBlock>
                            <FormControl
                              type="password"
                              value="blahblahblah"
                              placeholder="password"
                              disabled={true}
                            />
                        </Col>
                        <Col xs={3} className='top-offset-btn'>
                            {changePassButton}
                        </Col>
                    </FormGroup>
                    <div className={helpLevel}>{help}</div>
                    {submitButtons}
                </Form>
                {phoneForm}
                {passForm}
                <div className="col-xs-12"><hr /></div>
            </div>
        );
    }
});

var Home = exports.Home = React.createClass({
    contextTypes: {
        router: React.PropTypes.object.isRequired
    },
    getInitialState: function() {
      return {teams: []};
    },
    componentDidMount: function() {
        $.when(utils.loadTeams())
            .done(function(teams) {
              this.setState({teams: teams});
          }.bind(this))
          .fail(function(xhr) {
          }.bind(this));
    },
    handleChangeTeam: function(e) {
      this.setState({team: e[0]});
    },
    handleClickLogin: function() {
        this.context.router.replace('/login');
    },
    handleClickSignup: function() {
        this.context.router.replace('/register');
    },
    render: function() {
        if (utils.loggedIn()) {
            return (
                <div className='text-center form-top'>
                    <div className='home-header form-top'>
                        <h3>THANKS FOR GETTING WARNED WITH US!</h3>
                        <h5>YOU CAN CONTACT US AT PERSONS@SPORTSWARNING.COM</h5>
                    </div>
                </div>
            );
        } else {
            return (
                <div className='text-center'>
                    <div className='home-header'>
                        <h3>SPORTS ARE FUN. TRAFFIC JAMS ARE NOT.</h3>
                        <h5>Sign up to receive alerts when a sporting event may slow your roll.</h5>
                    </div>
                    <div className='landing-form'>
                        <Form>
                            <FormGroup>
                                <Typeahead
                                    onChange={this.handleChangeTeam}
                                    options={this.state.teams}
                                    labelKey="name"
                                    placeholder="Which team ruins your commute?"
                                />
                            </FormGroup>
                        </Form>
                    </div>
                    <div className='home-footer'>
                        <h4 className='show-pointer' onClick={this.handleClickSignup}>SIGN UP</h4>
                        <h6>or</h6>
                        <h5 className='show-pointer' onClick={this.handleClickLogin}>LOGIN</h5>
                        <h6 className='bottom-text'>Totally free. No spam. We promise.</h6>
                    </div>
                </div>
            );
        }
    }
});
});
