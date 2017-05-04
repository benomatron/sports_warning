window.define('watchers', function(require, exports, module) {

var deepCopy = require('../deepcopy');

var utils = require('utils');

var Button = ReactBootstrap.Button;
var Col = ReactBootstrap.Col;
var ControlLabel = ReactBootstrap.ControlLabel;
var Form = ReactBootstrap.Form;
var FormControl = ReactBootstrap.FormControl;
var FormGroup = ReactBootstrap.FormGroup;
var HelpBlock = ReactBootstrap.HelpBlock;
var Typeahead = ReactBootstrapTypeahead.default;

var WatcherList = React.createClass({
    getInitialState: function() {
        return {watcherNodes: [], watchers: [], teams: []};
    },
    buildWatcherNodes: function(watchers, user) {
        var watcherNodes;
        if (watchers.length) {
            var that = this;
            watcherNodes = watchers.map(function(watcher) {
                return <WatcherForm
                    key={watcher.id}
                    user={user}
                    onWatcherUpdate={that.props.onWatcherUpdate}
                    onWatcherDelete={that.props.onWatcherDelete}
                    watcher={watcher}
                    teams={that.props.teams}
                />;
            });
        }
        this.setState({watcherNodes: watcherNodes});
    },
    componentWillReceiveProps: function(nextProps) {
        if ((nextProps.watchers && this.state.watchers !== nextProps.watchers) ||
                nextProps.user !== this.props.user) {
            this.buildWatcherNodes(nextProps.watchers, nextProps.user);
        }
    },
    render: function() {
        return (
            <div className="watcher-list">
                {this.state.watcherNodes}
            </div>
        );
    }
});

var WatcherForm = React.createClass({
    getInitialState: function() {
        var isNew = this.props.watcher && this.props.watcher.id ? false : true;
        var validPhone = this.props.user && this.props.user.has_validated_phone;
        var teamId = this.props.watcher.team_id;
        var team;
        if (this.props.teams && this.props.teams.length) {
            this.props.teams.forEach(function (t) {
                if (t.id == teamId) {
                    team = t;        
                }
            });
        }
        return {
            watcher: this.props.watcher || {},
            team: team,
            teams: this.props.teams || [],
            isNew: isNew,
            isDeleting: false,
            isEditing: isNew,
            msg: null
        };
    },
    componentWillReceiveProps: function(nextProps) {
        if (this.state.watcher !== nextProps.watcher) {
            this.setState({watcher: nextProps.watcher});
        }
        if (this.state.teams !== nextProps.teams) {
            var team;
            if (nextProps.teams && nextProps.teams.length) {
                this.props.teams.forEach(function (t) {
                    if (t.id == nextProps.watcher.team_id) {
                        team = t;        
                    }
                });
            }
            this.setState({teams: nextProps.teams, team: team});
        }
        if (this.state.user != nextProps.user) {
            this.setState({user: nextProps.user});
        }
        if (nextProps.watcher && nextProps.watcher.id && this.state.isEditing) {
            this.setState({isEditing: false});
        }
    },
    handleChangeTeam: function(e) {
        var team = e[0];
        if (team) {
            var watcher = deepCopy(this.state.watcher);
            watcher.team_id = team.id; 
            this.setState({team: team, watcher: watcher});
        }
    },
    handleChangeNotifType: function(e) {
        var watcher = deepCopy(this.state.watcher);
        watcher.notification_method = e.target.value;
        this.setState({watcher: watcher});
    },
    handleChangeScheduleTime: function(e) {
        var watcher = deepCopy(this.state.watcher);
        watcher.hours_before = e.target.value;
        this.setState({watcher: watcher});
    },
    handleChangeAwayNotif: function(e) {
        var watcher = deepCopy(this.state.watcher);
        watcher.notify_away_games = e.target.value;
        this.setState({watcher: watcher});
    },
    handleDelete: function(e) {
        e.preventDefault();
        var id = this.state.watcher.id;
        this.props.onWatcherDelete({
            id: id
        });
    },
    toggleDelete: function() {
        this.setState({isDeleting: !this.state.isDeleting});
    },
    handleSubmit: function(e) {
        e.preventDefault();
        if (!this.state.team) {
            this.setState({msg: {txt: 'Please pick a valid team', level: 'error'}});
            return;
        }
        var watcher = this.state.watcher;
        if (watcher.team_id == null || watcher.notification_method == null || watcher.hours_before == null) {
            this.setState({msg: {txt: 'Please complete all fields', level: 'error'}});
            return;
        }
        if (watcher.user_id) {
            this.props.onWatcherUpdate(watcher);
            this.setState({msg: null});
        } else {
            this.props.onWatcherSubmit(watcher);
            this.setState({msg: null});
            this.refs.typeahead.getInstance().clear();
            this.props.cancelCreate();
        }
    },
    cancelEdit: function(e) {
        this.setState({watcher: this.props.watcher, isEditing: false});
    },
    toggleEdit: function() {
        this.setState({isEditing: !this.state.isEditing});
    },
    render: function() {
        var selectedTeam, submitButton, cancelButton, deleteButton, deleteCancelButton, editButton, noPhoneHelp, notifOptions;
        var help, helpLevel;
        if (this.state.teams && this.state.watcher && this.state.watcher.team_id) {
            var that = this;
            this.state.teams.forEach(function (t) {
                if (t.id == that.state.watcher.team_id) {
                    selectedTeam = t;
                }
            });
        }
        if (this.state.msg && this.state.msg.txt) {
            help = this.state.msg.txt;
            helpLevel = 'form-message message-' + this.state.msg.level;
        }
        if (this.state.watcher && this.state.watcher.user_id) {
            if (this.state.isDeleting) {
                deleteCancelButton = <Button type="button" bsSize="small" bsStyle="link" onClick={this.toggleDelete}>CANCEL</Button>;
                deleteButton = <Button type="button" bsSize="small" bsStyle="danger" onClick={this.handleDelete}>DELETE</Button>;
            } else {
                deleteButton = <Button type="button" bsSize="small" bsStyle="danger" onClick={this.toggleDelete}>DELETE</Button>;
            }
            if (this.state.isEditing) {
                submitButton = <Button type="submit" bsSize="small" bsStyle="primary" className="pull-right">UPDATE</Button>;
                cancelButton = <Button type="button" bsSize="small" bsStyle="link" className="pull-right m-five-right" onClick={this.cancelEdit}>CANCEL</Button>;
                editButton = ''; 
            } else {
                editButton = <Button type="button" bsSize="small" bsStyle="default" className="pull-right" onClick={this.toggleEdit}>EDIT</Button>;
            }
        } else {
            submitButton = <Button type="submit" bsSize="small" bsStyle="primary" className="pull-right">CREATE</Button>;
            cancelButton = <Button type="button" bsSize="small" bsStyle="link" className="pull-right m-five-right" onClick={this.props.cancelCreate}>CANCEL</Button>;
        }

        if (this.props.user && this.props.user.has_validated_phone) {
            notifOptions = [
                <option key={1} value="email">Email</option>,
                <option key={2} value="sms">Sms</option>,
                <option key={3} value="both">Both</option>
            ];
        } else {
            notifOptions = [
                <option key={1} value="email">Email</option>,
                <option key={2} value="sms" disabled={true}>Sms (phone validation required)</option>,
            ];
        }

        var scheduleOptions = [
            <option key={1} value="0">At time of event</option>,
            <option key={2} value="1">One hour before</option>,
            <option key={3} value="2">Two hours before</option>,
            <option key={4} value="4">Four hours before</option>,
            <option key={5} value="8">Eight hours before</option>,
            <option key={6} value="12">Twelve hours before</option>,
            <option key={7} value="24">One day before</option>
        ];
        var awayOptions = [
            <option key={1} value="false">Home games only</option>,
            <option key={2} value="true">Home and away</option>,
        ];

        return (
            <Form horizontal className="watcher-form" onSubmit={this.handleSubmit}>
                <hr />
                <FormGroup>
                    <Col componentClass={ControlLabel} xs={12}>
                        <Typeahead
                            ref="typeahead"
                            disabled={!this.state.isEditing}
                            onChange={this.handleChangeTeam}
                            options={this.state.teams}
                            selected={[selectedTeam]}
                            labelKey="name"
                            placeholder="Search for a sports team"
                        />
                    </Col>
                    <Col componentClass={ControlLabel} xs={4}>
                        <FormControl
                            disabled={!this.state.isEditing}
                            componentClass="select"
                            placeholder="select"
                            value={this.state.watcher.notification_method}
                            onChange={this.handleChangeNotifType}>
                            {notifOptions}
                        </FormControl>
                    </Col>
                    <Col componentClass={ControlLabel} xs={4}>
                        <FormControl
                            disabled={!this.state.isEditing}
                            componentClass="select"
                            placeholder="When to be notified"
                            value={this.state.watcher.hours_before}
                            onChange={this.handleChangeScheduleTime}>
                            {scheduleOptions}
                        </FormControl>
                    </Col>
                    <Col componentClass={ControlLabel} xs={4}>
                        <FormControl
                            disabled={!this.state.isEditing}
                            componentClass="select"
                            placeholder=""
                            value={this.state.watcher.notify_away_games}
                            onChange={this.handleChangeAwayNotif}>
                            {awayOptions}
                        </FormControl>
                    </Col>
                    <Col xs={12}>
                        <HelpBlock className={helpLevel}>{help}</HelpBlock>
                    </Col>
                    <Col xs={4} className='watcher-btn'>
                        {deleteCancelButton}
                        {deleteButton}
                    </Col>
                    <Col xsOffset={4} xs={4} className='watcher-btn'>
                        {submitButton}
                        {cancelButton}
                        {editButton}
                    </Col>
                </FormGroup>
            </Form>
        );
    }
});

var Watchers = exports.Watchers = React.createClass({
    // TODO: dry this more
    loadWatchers: function() {
        $.when(utils.watcherAPI('GET', '', localStorage.token))
            .done(function (watchers) {
                this.setState({watchers: watchers, isAdding: !watchers.length || this.state.isAdding});
            }.bind(this))
            .fail(function (xhr) {
                // TODO: DRY these once render alert is better
                var msg = utils.parseMessage(xhr.responseText);
                utils.renderAlert(msg, 'danger');
            }.bind(this));
    },
    getUser: function() {
        $.when(utils.getUser(localStorage.token))
            .done(function (user) {
                this.setState({user: user});
            }.bind(this))
            .fail(function (xhr) {
                var msg = utils.parseMessage(xhr.responseText);
                utils.renderAlert(msg, 'danger');
            }.bind(this));
    },
    handleWatcherSubmit: function(watcher) {
        $.when(utils.watcherAPI('POST', watcher, localStorage.token))
            .done(function (data) {
                this.loadWatchers();
            }.bind(this))
            .fail(function (xhr) {
                var msg = utils.parseMessage(xhr.responseText);
                utils.renderAlert(msg, 'danger');
            }.bind(this));
    },
    handleWatcherUpdate: function(watcher) {
        $.when(utils.watcherAPI('PUT', watcher, localStorage.token))
            .done(function (data) {
                utils.renderAlert('Your sports warning has been updated', 'info');
                this.loadWatchers();
            }.bind(this))
            .fail(function (xhr) {
                var msg = utils.parseMessage(xhr.responseText);
                utils.renderAlert(msg, 'danger');
            }.bind(this));
    },
    handleWatcherDelete: function(watcher) {
        $.when(utils.watcherAPI('DELETE', watcher, localStorage.token))
            .done(function (data) {
                this.loadWatchers();
            }.bind(this))
            .fail(function (xhr) {
                var msg = utils.parseMessage(xhr.responseText);
                utils.renderAlert(msg, 'danger');
            }.bind(this));
    },
    getInitialState: function() {
        return {teams: [], watchers: [], isAdding: false};
    },
    componentDidMount: function() {
        $.when(utils.loadTeams())
            .done(function(teams) {
              this.setState({teams: teams});
          }.bind(this))
          .fail(function(xhr, status, err) {
              var msg = utils.parseMessage(xhr.responseText);
              utils.renderAlert(msg, 'danger');
          }.bind(this));
        this.loadWatchers();
        this.getUser();
    },
    toggleNewForm: function() {
        this.setState({isAdding: !this.state.isAdding});
    },
    render: function() {
        var newWatcherForm, newWatcherButton;
        if (this.state.isAdding) {
            newWatcherForm = <div>
                <WatcherForm
                user={this.state.user}
                onWatcherSubmit={this.handleWatcherSubmit}
                teams={this.state.teams}
                cancelCreate={this.toggleNewForm}
                watcher={{notification_method: 'email', hours_before: '0', notify_away_games: false}}/>
            </div>;
        }
        return (
            <div className="form-top">
                    <span className='active-header'>
                        ACTIVE WARNINGS 
                    </span>
                    <Button type="button"
                            bsSize="small"
                            bsStyle="primary"
                            className='pull-right'
                            disabled={this.state.isAdding}
                            onClick={this.toggleNewForm}>
                        NEW WARNING
                    </Button>
                {newWatcherForm}
                <WatcherList
                    user={this.state.user}
                    teams={this.state.teams}
                    watchers={this.state.watchers}
                    onWatcherUpdate={this.handleWatcherUpdate}
                    onWatcherDelete={this.handleWatcherDelete}
                />
                <hr />
            </div>
        );
    }
});
});
