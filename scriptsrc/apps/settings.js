/* global angular */

import MessagingService from '../services/MessagingService';
import SettingsController from '../controllers/SettingsController';
import ngCategories from '../directives/ngCategories';

angular.module('settingsApp', [])
  .service('MessagingService', MessagingService)
  .directive('ngCategories', ngCategories)
  .controller('SettingsController', SettingsController);
/**
(function($, document, undefined) {
  'use strict';

  $(document).ready(function() {

    let messagingService = new MessagingService();

    // Setup selectors
    let $languageSelect = $('#language-select');
    let $languageChanger = $('#change-language');
    let $createUsergroup = $('#create_usergroup');
    let $removeFromUsergroup = $('#remove_from_usergroup');
    let $addToUsergroup = $('#add_to_usergroup');
    let $requestSource = $('#add_source');
    let $answerUsergroup = $('#answer_usergroup');

    let $packetRange = $('#packet-range');
    let $packetPrice = $('#packet-price');
    let $packetChanger = $('#change-packet');
    let $packets = $('input[name="packet-selection"]');
    let $groupName = $('input[name="group_name"]');
    let $memberEmail = $('input[name="member_email"]');
    let $sourceRequestURL = $('#src_request_link');
    let $sourceRequestDescription = $('#src_request_desc');
    let $groupAnswer = $('input[name="group_answer"]');

    let $passwordChanger = $('#change-password');
    let $oldPassword = $('#old-password');
    let $newPassword1 = $('#new-password-1');
    let $newPassword2 = $('#new-password-2');

    // Prices of packets for maths.
    let packetPrices = [
      49,
      99,
      499,
    ];

    /**
     * Call API with data.
     * @param {String} action The action to use.
     * @param {Object} data   The data to send.
     *
    let apiRequest = (url, action, data) => {
      data.action = action;
      $.ajax({
        type: 'POST',
        url: url,
        dataType: 'json',
        data: JSON.stringify(data)
      }).success((data) => {
        if (data.type === 'danger') {
          messagingService.danger(data.message);
        } else if (data.type === 'success') {
          messagingService.success(data.message);
        }
      });
    };/

    /**
     * Get the currently selected packet
     * @return {Integer} Currently selected packet number.
     *
    let getCurrentlySelectedPacket = () => {
      let selectedPacket = 1;

      $packets.each(function () {
        let $packet = $( this );
        if ($packet.is(':checked')) {
          selectedPacket = parseInt($packet.data('packet'));
          return false;
        }
      });

      return selectedPacket;
    };/

    /**
     * Calculate the price and update the selector.
     *
    let calculatePrice = () => {
      let packetPrice = packetPrices[getCurrentlySelectedPacket() - 1];
      let months = $packetRange.val();
      $packetPrice.html(packetPrice*months);
    };/

    /**
    // Change passwords.
    $passwordChanger.click(() => {
      let oldPass = $oldPassword.val();
      let newPass = $newPassword1.val();
      let newPass2 = $newPassword2.val();

      if (newPass === newPass2) {
        apiRequest('/app/settings', 'change_password', {
          'old_password': oldPass,
          'new_password': newPass
        });
      }
    });
    
    // change the language and reload
    $languageChanger.click(() => {
      let language = $languageSelect.val();
      apiRequest('/app/settings', 'set_lang', {
        'lang': language
      });
      //location.reload();
    });

  	// create usergroup
  	$createUsergroup.click(function() {
  	  apiRequest('/app/settings', 'create_usergroup', {
  		'group_name': $groupName.val()
  	  });
  	});

	// add to usergroup
    $addToUsergroup.click(function() {
      apiRequest('/app/settings', 'add_to_usergroup', {
        group_name: $groupName.val(),
        member_email: $memberEmail.val()
      });
    });

    // remove from usergroup
    $removeFromUsergroup.click(function() {
      apiRequest('/app/settings', 'remove_from_usergroup', {
        group_name: $groupName.val(),
        member_email: $memberEmail.val()
      });
    });

    // request source
    $requestSource.click(function() {
      apiRequest('/app/request_source', 'request_source', {
        url: $sourceRequestURL.val(),
        description: $sourceRequestDescription.val()
      });
    });

    // answer usergroup
    $answerUsergroup.click(function() {
      apiRequest('/app/settings', 'answer_usergroup', {
        group_name: $groupName.val(),
        group_answer: $groupAnswer.val()
      });
    });

    // Calculate price when packetrange changes
    $packetRange.change(calculatePrice);
    $packets.change(calculatePrice);

    // Extend packet
    $packetChanger.click(() => {
      let selectedPacket = getCurrentlySelectedPacket();

      if (selectedPacket > 0) {
        apiRequest('/app/settings', 'extend_usage',{
          months: $packetRange.val(),
          packet: selectedPacket
        });
      }
    });

    // Things to do on startup
    calculatePrice();
  });
})(jQuery, document);
*/