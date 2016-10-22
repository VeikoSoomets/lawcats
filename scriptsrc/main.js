/**
 * Main controller.
 *
 * Implements functions used in all pages.
 *
 * Author: Uku Tammet
 */

// Most is not used yet, so jshint should ignore this file.
/* jshint ignore:start */
(function ($) { 
  
  $(document).ready(function() {
    // Strict javascript
    'use strict';

    // Materialize select boxes
    $('select').material_select();

    // Login function
    var recordLogin = function() {
      $.ajax({
        type: 'POST',
        url: '/app/record_logout',
        dataType: 'json',
        data: JSON.stringify({ 'action': 'logout' }),
      });
    };

    var addWord = function() {
      var categories = ['delfi', 'postimees', 'reuters', 'äripäev', 'wsj_business'];
      $.ajax({
        type: 'POST',
        url:'/app/querywords',
        dataType: 'json',
        data: JSON.stringify({
          'queryword': 'apple, google, money, reform, ukraine, ukraina, venemaa',
          'categories': categories,
          'request_frequency': 24, 
          'action':'create_request'
        }),
      });
    };
  });

})(jQuery);
/* jshint ignore:end */