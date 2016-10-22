/**
 * Main angular app and controller for app/results.
 *
 * Author: Uku Tammet
 */

'use strict';
class ResultsController {
  constructor ($http) {
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

  pullArchiveDataIfNotPulled() {
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
  pullResultsData(cursor) {
    const requestData = {
      action: 'get_results',
      'archived': false,
      result_id: null
    };
    if (cursor) {
      requestData.bookmark = cursor;
    }
    this.$http.post(this.baseURL, requestData).success(data => {
      if (data.data.constructor === Array) {
        data.data.forEach(result => {
          this.results.push(result);
        });
        if (data.bookmark !== null) {
          this.pullResultsData(data.bookmark);
        } else {
          this.loaded = true;
        }
      }
    });
  }

  /**
   * Pull archive data page by page.
   * @param {String} cursor The current cursor to pull by.
   */
  pullArchiveData(cursor) {
    const requestData = {
      action: 'get_results',
      'archived': true,
      result_id: null
    };
    if (cursor) {
      requestData.bookmark = cursor;
    }
    this.$http.post(this.baseURL, requestData).success(data => {
      if (data.data.constructor === Array) {
        data.data.forEach(result => {
          this.archive.push(result);
        });
        if (data.bookmark !== null) {
          this.pullArchiveData(data.bookmark);
        } else {
          this.loaded = true;
        }
      }
    });
  }

  /**
   * Open a modal, filling it with a result.
   * @param {Object} result The result to fill the modal with.
   */
  openModal (result) {
    this.modalResult = result;
    this.$modal.modal();
  }

  /**
   * Unarchives and archives results.
   * @param {Object} result The result to deal with.
   */
  archiveResult (result) {
    if (result.archived) {
      result.archived = false;
      this.archive.splice(this.archive.indexOf(result),1);
      this.results.unshift(result);
    } else {
      result.archived = true;
      this.results.splice(this.results.indexOf(result),1);
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
  removeResult(result) {
    if (result.archived) {
      this.archive.splice(this.archive.indexOf(result),1);
    } else {
      this.results.splice(this.results.indexOf(result),1);
    }
    this.$http.post(this.baseURL, {
      'action': 'remove_result',
      'result_id': result.result_id,
    });
  }

  /**
   * Sets the order of results by expression.
   * @param {String} order What to order by.
   */
  setResultOrder (order) {
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
  setArchiveOrder (order) {
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
  addTags () {
    let indexOfResult = this.results.indexOf(this.modalResult);
    let actualResult;

    if (indexOfResult === -1) {
      indexOfResult = this.archive.indexOf(this.modalResult);
      actualResult = this.archive[indexOfResult];
    } else {
      actualResult = this.results[indexOfResult];
    }

    let splitTags = this.tags.split(',').map(tag => {
      return tag.trim();
    });

    this.$http.post(this.baseURL, {
      'action': 'add_tags',
      'result_id': actualResult.result_id,
      'tags': splitTags
    }).success(() => {
      splitTags.forEach(currentTag => {
        actualResult.tags.push(currentTag);
      });
      this.tags = '';
    });
  }

  /**
   * Remove a tag from the currently selected result.
   * @param {String} tag The tag to remove.
   */
  removeTag (tag) {
    let indexOfResult = this.results.indexOf(this.modalResult);
    let actualResult;

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
    }).success(() => {
      actualResult.tags.splice(actualResult.tags.indexOf(tag),1);
    });
  }
}

ResultsController.$inject = ['$http'];

export default ResultsController;
