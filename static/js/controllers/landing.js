(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
'use strict';

var _interopRequireDefault = function (obj) { return obj && obj.__esModule ? obj : { 'default': obj }; };

/* global angular */

var _LandingController = require('../controllers/LandingController');

var _LandingController2 = _interopRequireDefault(_LandingController);

var _ngCategories = require('../directives/ngCategories');

var _ngCategories2 = _interopRequireDefault(_ngCategories);

'use strict';

angular.module('landingApp', []).directive('ngCategories', _ngCategories2['default']).controller('LandingController', _LandingController2['default']);

},{"../controllers/LandingController":2,"../directives/ngCategories":3}],2:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, '__esModule', {
  value: true
});

var _classCallCheck = function (instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError('Cannot call a class as a function'); } };

var _createClass = (function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ('value' in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; })();

/**
 * Controller for / - landing page.
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

var LandingController = (function () {
  function LandingController($http) {
    _classCallCheck(this, LandingController);

    this.$http = $http;

    // Maximum amount of results to show
    this.maxResultsNum = 10;

    // URL for api calls
    this.categoriesUrl = '/landing_cats';
    this.searchUrl = '/search';

    this.hasSearched = false;
    this.loading = false;
    this.results = [];

    this.sources = [];
    this.querywords = '';
    this.getSources();
  }

  _createClass(LandingController, [{
    key: 'getSources',

    /**
     * Get sources to search
     */
    value: function getSources() {
      var _this = this;

      this.$http({
        method: 'GET',
        url: this.categoriesUrl,
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json'
        }
      }).success(function (data) {
        var currentId = 0;

        data.sources.forEach(function (category) {
          category.checked = false;
          category.id = currentId;
          _this.sources.push(category);
          currentId++;
        });
      });
    }
  }, {
    key: 'search',

    /**
     * Execute search with querywords and sources.
     */
    value: function search() {
      var _this2 = this;

      this.hasSearched = true;
      this.loading = true;
      var queryDate = new Date();

      var filteredSources = this.sources.filter(function (source) {
        return source.checked;
      }).map(function (source) {
        return source.category_name;
      });
      console.log('Sources: ' + filteredSources);
      console.log('Querywords: ' + this.querywords);

      this.$http.post(this.searchUrl, {
        action: 'landing_search',
        queryword: this.querywords,
        date_algus: formatDate(queryDate),
        categories: filteredSources
      }).success(function (response) {
        var currentNum = 0;
        _this2.results = response.search_results.filter(function () {
          currentNum++;
          return currentNum < _this2.maxResultsNum;
        }).map(function (result) {
          if (result.name || result.programs) {
            var normalizedResult = {
              result_title: result.name,
              categories: result.programs,
              result_link: '#'
            };

            return normalizedResult;
          }

          return result;
        });
        console.log(response);
        _this2.querywords = '';
        _this2.sources.forEach(function (source) {
          source.checked = false;
        });
        _this2.loading = false;
      }).error(function (err) {
        console.error(err);
        _this2.loading = false;
      });
    }
  }]);

  return LandingController;
})();

LandingController.$inject = ['$http'];

exports['default'] = LandingController;
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
