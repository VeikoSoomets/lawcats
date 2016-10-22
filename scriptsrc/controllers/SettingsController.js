/**
 * Main controller for app/settings
 */

class SettingsController {
  constructor(MessagingService, $http) {
    this.MessagingService = MessagingService;
    this.$http = $http;
    this.packets = {
      prices: [25, 99],
      packet: 1,
      range: 1
    };

    this.emailAlerts = {
      email: '',
      range: 1
    };

    this.userGroup = {
      name: '',
      currentName: '',
      'new': ''
    };

    this.newSource = {
      link: '',
      description: ''
    };

    this.passwordChange = {
      oldPassword: '',
      newPassword: '',
      newPasswordAgain: ''
    };

    this.groupMembers = [];
    this.userEmail = '';
    this.groupMaster = '';
    this.pullGroupData();

    this.sources = [];
    this.categoriesUrl = '/app/custom_cats';
    this.getSources();
  }

  /**
   * Get sources to settings page source management.
   */
  getSources () {
    this.$http({
        method: 'GET',
        url: this.categoriesUrl,
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    }).success(data => {
      let currentId = 0;

      data.sources.forEach(category => {
        category.checked = false;
        category.id = currentId;
        this.sources.push(category);
        currentId++;
      });
    });
  }

  pullGroupData() {
    this.$http
      .get('/app/settings/data')
      .success(response => {
        this.groupMembers = response.data.group_members;
        this.userEmail = response.data.group_to_answer;
        this.groupMaster = response.data.group_master;
      })
      .error(err => this.MessagingService.danger(err));
  }

  addToUserGroup() {
    if (this.userGroup.new.trim()) {
      this.apiRequest('add_to_usergroup', {
        group_name: this.groupMaster,
        member_email: this.userGroup.new
      });
      this.groupMembers.push({
        user_email: this.userGroup.new.trim(),
        user_status: 'pending'
      });
    } else {
      const err = 'Please add an email to new usergroup member.';
      this.MessagingService.danger(err);
    }
  }

  /**
   * Call API with data.
   * @param {String} action The action to use.
   * @param {Object} data   The data to send.
   */
  apiRequest(action, data, url='/app/settings') {
    data.action = action;
    this.$http({
      method: 'POST',
      url: url,
      headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
      },
      data: data
    }).success((data) => {
      if (data.type === 'danger') {
        this.MessagingService.danger(data.message);
      } else if (data.type === 'success') {
        this.MessagingService.success(data.message);
      }
    }).error((err) => {
      this.MessagingService.danger(err);
    });
  }

  changePassword() {
    const firstPass = this.passwordChange.newPassword;
    if (firstPass === this.passwordChange.newPasswordAgain) {
      this.apiRequest('change_password', {
        'old_password': this.passwordChange.oldPassword,
        'new_password': this.passwordChange.newPassword
      });
      this.passwordChange.newPassword = '';
      this.passwordChange.newPasswordAgain = '';
      this.passwordChange.oldPassword = '';
    } else {
      this.MessagingService.danger('Your passwords don\'t match.');
    }
  }

  addNewSource() {
    if (this.newSource.link.trim() && this.newSource.description.trim()) {
      this.apiRequest('request_source', {
        url: this.newSource.link,
        description: this.newSource.description
      }, '/app/request_source');
      this.newSource.link = '';
      this.newSource.description = '';
    } else {
      const msg = 'Please add a link and description to your new source.';
      this.MessagingService.danger(msg);
    }
  }

  leaveUserGroup() {
    console.log(this.userGroup.name);
    if (this.userGroup.name.trim()) {
      this.apiRequest('remove_from_usergroup', {
        group_name: this.userGroup.name,
        member_email: false
      });
      this.userGroup.name = '';
    } else {
      this.MessagingService.danger('Please write a usergroup name');
    }
  }

  removeFromUserGroup(user) {
    this.groupMembers.splice(this.groupMembers.indexOf(user), 1);
    this.apiRequest('remove_from_usergroup', {
      group_name: this.groupMaster,
      member_email: user.user_email
    });
  }

  createUserGroup() {
    if (this.userGroup.name.trim()) {
      this.apiRequest('create_usergroup', {
       'group_name': this.userGroup.name
      });
      this.userGroup.name = '';
    } else {
      this.MessagingService.danger('Please write a usergroup name');
    }
  }

  extendPacket() {
    this.apiRequest('extend_usage', {
      months: this.packets.range,
      packet: parseInt(this.packets.packet)
    });
  }

  addEmailAlert() {
    if (this.emailAlerts.email) {
      // TODO: api request
      this.emailAlerts.email = '';
    } else {
      this.MessagingService.danger('Please write an email.');
    }
  }
}

SettingsController.$inject = ['MessagingService', '$http'];

export default SettingsController;