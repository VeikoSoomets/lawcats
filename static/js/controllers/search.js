(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
'use strict';

var _interopRequireDefault = function (obj) { return obj && obj.__esModule ? obj : { 'default': obj }; };

/* global angular */

var _SearchController = require('../controllers/search');

var _SearchController2 = _interopRequireDefault(_SearchController);

var _ngCategories = require('../directives/ngCategories');

var _ngCategories2 = _interopRequireDefault(_ngCategories);

'use strict';

angular.module('searchApp', []).directive('ngCategories', _ngCategories2['default']).controller('SearchController', _SearchController2['default']);

},{"../controllers/search":2,"../directives/ngCategories":3}],2:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, '__esModule', {
  value: true
});

var _classCallCheck = function (instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError('Cannot call a class as a function'); } };

var _createClass = (function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ('value' in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; })();

/**
 * Main angular app and controller for app/search
 *
 * Author: Uku Tammet
 */
'use strict';

/**
 * Format a date to yyyy-mm-dd
 * @param  {Date}   date Date to format
 * @return {String}      Date in yyyy-mm-dd
 */
function formatDate(date) {
  var month = '' + (date.getMonth() + 1);
  var day = '' + date.getDate();
  var year = date.getFullYear();

  if (month.length < 2) month = '0' + month;
  if (day.length < 2) day = '0' + day;

  return [year, month, day].join('-');
}

var SearchController = (function () {
  function SearchController($http) {
    _classCallCheck(this, SearchController);

    this.$http = $http;

    // URL for api calls
    this.baseUrl = '/app/search';

    // Setup scope globals.
    this.hasSearched = false;
    this.loading = false;
    this.results = [];
    this.searchSources = [];
    this.querywords = '';
    this.searchedSanctions = false;

    this.searchSources = [];
    this.sources = [];
    this.newSourceUrl = '';
    this.newSourceDescription = '';

    this.getSources();
  }

  _createClass(SearchController, [{
    key: 'getSources',

    /**
     * Get sources to search
     */
    value: function getSources() {
      var _this = this;

      this.$http({
        method: 'GET',
        url: this.baseUrl,
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json'
        }
      }).success(function (data) {
        var currentId = 0;
        _this.sources = data.sources;
        data.sources.forEach(function (mainCategory) {
          mainCategory[1].forEach(function (subCategory) {
            subCategory[1].forEach(function (category) {
              _this.searchSources.push({
                checked: false,
                name: category.category_name
              });
              category.id = currentId;
              currentId++;
            });
          });
        });
      });
    }
  }, {
    key: 'searchFrom',

    /**
     * Execute a search from sources.
     * @param  {String} where Where to search from.
     */
    value: function searchFrom(where) {
      var _this2 = this;

      this.loading = true;
      this.results = [];
      this.hasSearched = true;
      this.searchedSanctions = false;
      var queryDate = new Date();
      var queryAction = '';
      var sources = [];

      this.searchSources.forEach(function (source) {
        if (source.checked) {
          sources.push(source.name);
        }
      });

      switch (where.toLowerCase()) {
        case 'news': // Fallthrough
        case 'courts':
          queryAction = 'archive_search';
          queryDate = this.queryDate;
          break;

        case 'sanctions':
          this.searchedSanctions = true;
          queryAction = 'list_search';
          break;

        case 'custom':
          queryAction = 'custom_search';
          break;

        case 'monitoring':
          queryAction = 'search';
          break;

        default:
          // Should never enter, this is for future guys.
          console.error('Entered default case in searchFrom');
      }

      this.$http.post(this.baseUrl, {
        action: queryAction,
        queryword: this.querywords,
        date_algus: queryDate, // TODO! formatDate() requires date, which is sometimes unavailable
        categories: sources
      }).success(function (response) {
        _this2.results = response.search_results;
        _this2.loading = false;
        setTimeout(function(){
          $(".result-title-link").html(function(_, html) {
            function capitalizeFirstLetter(string) {
                return string.charAt(0).toUpperCase() + string.slice(1);
            }
            var words = _this2.querywords.split(" ");
            var returnHtml = html;
            for (var querywordIndex in words){
              var queryword = words[querywordIndex];
              var querywordCapitalized = capitalizeFirstLetter(_this2.querywords);
              returnHtml = returnHtml.replace(queryword, '<span class="highlight-text">'+queryword+'</span>');
              returnHtml = returnHtml.replace(querywordCapitalized , '<span class="highlight-text">'+querywordCapitalized+'</span>');
            }
            return returnHtml;
          });
        }, 1000);
      }).error(function (err) {
        console.error(err);
        _this2.loading = false;
      });
    }
  }, {
    key: 'sendNewSource',

    /**
     * Send request for new source
     */
    value: function sendNewSource() {
      var _this3 = this;
      _this3.loading = true;
      if (this.newSourceUrl && this.newSourceDescription) {
        this.$http.post('/app/request_source', {
          url: this.newSourceUrl,
          description: this.newSourceDescription
        }).success(function (data) {
		  _this3.loading = false;
          if (data.type === 'success') {
            _this3.sources[0][1][0][1].push({'category_link':data.link,'category_name':data.title});
            _this3.newSourceDescription = '';
            _this3.newSourceUrl = '';
          }
        });
      }
    }
  }, {
    value: function () {

    }
  }]);

  return SearchController;
})();

SearchController.$inject = ['$http'];

exports['default'] = SearchController;
module.exports = exports['default'];

},{}],3:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, '__esModule', {
  value: true
});

var _classCallCheck = function (instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError('Cannot call a class as a function'); } };

var _createClass = (function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ('value' in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; })();

'use strict';

var CategoriesController = (function () {
  function CategoriesController() {
    _classCallCheck(this, CategoriesController);

    this.idMap = {};
    this.currentId = 0;
  }

  _createClass(CategoriesController, [{
    key: 'isAllowedCategory',

    /**
     * Check if category is allowed.
     * @param  {String} category The maincategory to check.
     * @return {Boolean}         If it's allowed.
     */
    value: function isAllowedCategory(category) {
      if (typeof this.allowedCategories !== 'undefined') {
        return this.allowedCategories.indexOf(category) !== -1;
      } else if (typeof this.forbiddenCategories !== 'undefined') {
        return this.forbiddenCategories.indexOf(category) === -1;
      }

      return true;
    }
  }, {
    key: 'getIdFromCategory',

    /**
     * Nets an id from a category name.
     * @param  {String} category The category to get id from.
     * @return {String}          ID.
     */
    value: function getIdFromCategory(category) {
      if (category in this.idMap) {
        return this.idMap[category];
      } else {
        var newCat = 'category' + category.replace(/\W+/g, '') + this.currentId;
        this.idMap[category] = newCat;
        this.currentId++;
        return newCat;
      }
    }
  }, {
    key: 'checkAll',

    /**
     * Check all the sources under a given subcategory.
     * @param  {Array} subcategory All categories under subcategory.
     */
    value: function checkAll(subcategory) {
      var counter = 0;

      this.ngModel.forEach(function (category) {
        var shouldBeChecked = false;

        subcategory.forEach(function (subcat) {
          if (subcat.category_name === category.name) {
            shouldBeChecked = true;
          }
        });

        if (shouldBeChecked) {
          if (category.checked) counter++;
          category.checked = false;
        }
      });

      if (counter !== subcategory.length) {
        this.ngModel.forEach(function (category) {
          subcategory.forEach(function (subcat) {
            if (subcat.category_name === category.name) {
              category.checked = true;
            }
          });
        });
      }
    }
  }, {
    key: 'areAllChecked',

    /**
     * Check if all categories in a subcategory are checked.
     * @param  {Array} subcategory The subcategory to check.
     * @return {Boolean}            If all are checked.
     */
    value: function areAllChecked(subcategory) {
      var _this = this;

      return subcategory.reduce(function (accumulator, category) {
        if (!accumulator) {
          return false;
        }
        var isChecked = _this.ngModel.reduce(function (accumulator, ngCat) {
          if (accumulator) {
            return true;
          }
          if (category.category_name === ngCat.name && ngCat.checked) {
            return true;
          }
          return false;
        }, false);
        return isChecked;
      }, true);
    }
  }]);

  return CategoriesController;
})();

exports['default'] = function () {
  return {
    restrict: 'E',
    scope: {
      ngModel: '=',
      categories: '=',
      allowedCategories: '=?',
      forbiddenCategories: '=?'
    },
    controller: CategoriesController,
    controllerAs: 'catCtrl',
    bindToController: true,
    templateUrl: '/static/js/templates/categories.html' };
};

module.exports = exports['default'];

},{}]},{},[1]);
