(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
'use strict';
/* global angular */

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { 'default': obj }; }

var _controllersResults = require('../controllers/results');

var _controllersResults2 = _interopRequireDefault(_controllersResults);

angular.module('resultsApp', []).controller('ResultsController', _controllersResults2['default']);

},{"../controllers/results":2}],2:[function(require,module,exports){
/**
 * Main angular app and controller for app/results.
 *
 * Author: Uku Tammet
 */

'use strict';
Object.defineProperty(exports, '__esModule', {
  value: true
});

var _createClass = (function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ('value' in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; })();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError('Cannot call a class as a function'); } }

var ResultsController = (function () {
  function ResultsController($http) {
    _classCallCheck(this, ResultsController);

    this.$http = $http;
    this.baseURL = '/app/results/data';

    // Selectors
    this.$modal = $('#result-modal');

    // Globals
    this.results = [];
    this.archive = [];
    this.loaded = false;
    this.resultOrder = '';
    this.archiveOrder = '';
    this.hasPulledArchives = false;
    this.tags = '';
    this.pullResultsData();
  }

  _createClass(ResultsController, [{
    key: 'pullArchiveDataIfNotPulled',
    value: function pullArchiveDataIfNotPulled() {
      this.loaded = false;
      if (!this.hasPulledArchives) {
        this.pullArchiveData();
        this.hasPulledArchives = true;
      }
    }

    /**
     * Pull results data page by page.
     * @param {String} cursor The current cursor to pull by.
     */
  }, {
    key: 'pullResultsData',
    value: function pullResultsData(cursor) {
      var _this = this;

      var requestData = {
        action: 'get_results',
        'archived': false,
        result_id: null
      };
      if (cursor) {
        requestData.bookmark = cursor;
      }
      this.$http.post(this.baseURL, requestData).success(function (data) {
        if (data.data.constructor === Array) {
          data.data.forEach(function (result) {
            _this.results.push(result);
          });
          if (data.bookmark !== null) {
            _this.pullResultsData(data.bookmark);
          } else {
            _this.loaded = true;
          }
        }
      });
    }

    /**
     * Pull archive data page by page.
     * @param {String} cursor The current cursor to pull by.
     */
  }, {
    key: 'pullArchiveData',
    value: function pullArchiveData(cursor) {
      var _this2 = this;

      var requestData = {
        action: 'get_results',
        'archived': true,
        result_id: null
      };
      if (cursor) {
        requestData.bookmark = cursor;
      }
      this.$http.post(this.baseURL, requestData).success(function (data) {
        if (data.data.constructor === Array) {
          data.data.forEach(function (result) {
            _this2.archive.push(result);
          });
          if (data.bookmark !== null) {
            _this2.pullArchiveData(data.bookmark);
          } else {
            _this2.loaded = true;
          }
        }
      });
    }

    /**
     * Open a modal, filling it with a result.
     * @param {Object} result The result to fill the modal with.
     */
  }, {
    key: 'openModal',
    value: function openModal(result) {
      this.modalResult = result;
      this.$modal.modal();
    }

    /**
     * Unarchives and archives results.
     * @param {Object} result The result to deal with.
     */
  }, {
    key: 'archiveResult',
    value: function archiveResult(result) {
      if (result.archived) {
        result.archived = false;
        this.archive.splice(this.archive.indexOf(result), 1);
        this.results.unshift(result);
      } else {
        result.archived = true;
        this.results.splice(this.results.indexOf(result), 1);
        this.archive.unshift(result);
      }
      this.$http.post(this.baseURL, {
        'action': 'archive_result',
        'result_id': result.result_id,
        'archived': result.archived
      });
    }

    /**
     * Removes a result.
     * @param {Object}  result The result to remove.
     */
  }, {
    key: 'removeResult',
    value: function removeResult(result) {
      if (result.archived) {
        this.archive.splice(this.archive.indexOf(result), 1);
      } else {
        this.results.splice(this.results.indexOf(result), 1);
      }
      this.$http.post(this.baseURL, {
        'action': 'remove_result',
        'result_id': result.result_id
      });
    }

    /**
     * Sets the order of results by expression.
     * @param {String} order What to order by.
     */
  }, {
    key: 'setResultOrder',
    value: function setResultOrder(order) {
      if (this.resultOrder === order) {
        this.resultOrder = '-' + order;
      } else if (this.resultOrder === '-' + order) {
        this.resultOrder = '';
      } else {
        this.resultOrder = order;
      }
    }

    /**
     * Sets the order of archive by expression.
     * @param {String} order What to order by.
     */
  }, {
    key: 'setArchiveOrder',
    value: function setArchiveOrder(order) {
      if (this.archiveOrder === order) {
        this.archiveOrder = '-' + order;
      } else if (this.archiveOrder === '-' + order) {
        this.archiveOrder = '';
      } else {
        this.archiveOrder = order;
      }
    }

    /**
     * Add tags to current selected result.
     * @param {String} tags The tags to add.
     */
  }, {
    key: 'addTags',
    value: function addTags() {
      var _this3 = this;

      var indexOfResult = this.results.indexOf(this.modalResult);
      var actualResult = undefined;

      if (indexOfResult === -1) {
        indexOfResult = this.archive.indexOf(this.modalResult);
        actualResult = this.archive[indexOfResult];
      } else {
        actualResult = this.results[indexOfResult];
      }

      var splitTags = this.tags.split(',').map(function (tag) {
        return tag.trim();
      });

      this.$http.post(this.baseURL, {
        'action': 'add_tags',
        'result_id': actualResult.result_id,
        'tags': splitTags
      }).success(function () {
        splitTags.forEach(function (currentTag) {
          actualResult.tags.push(currentTag);
        });
        _this3.tags = '';
      });
    }

    /**
     * Remove a tag from the currently selected result.
     * @param {String} tag The tag to remove.
     */
  }, {
    key: 'removeTag',
    value: function removeTag(tag) {
      var indexOfResult = this.results.indexOf(this.modalResult);
      var actualResult = undefined;

      if (indexOfResult === -1) {
        indexOfResult = this.archive.indexOf(this.modalResult);
        actualResult = this.archive[indexOfResult];
      } else {
        actualResult = this.results[indexOfResult];
      }

      this.$http.post(this.baseURL, {
        'action': 'remove_tag',
        'result_id': actualResult.result_id,
        'tags': tag
      }).success(function () {
        actualResult.tags.splice(actualResult.tags.indexOf(tag), 1);
      });
    }
  }]);

  return ResultsController;
})();

ResultsController.$inject = ['$http'];

exports['default'] = ResultsController;
module.exports = exports['default'];

},{}]},{},[1]);
