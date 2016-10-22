/**
 * Main angular app and controller for app/querywords.
 *
 * Author: Uku Tammet
 */
'use strict';

// Extend date prototype to get good format.
Date.prototype.yyyymmdd = function() {
  let yyyy = this.getFullYear().toString();
  let mm = (this.getMonth()+1).toString(); // getMonth() is zero-based
  let dd  = this.getDate().toString();
  let ans = yyyy + '-';
  ans += (mm[1] ? mm : '0' + mm[0]) + '-';
  ans += (dd[1] ? dd: '0' + dd[0]);
  return ans;
};

class QuerywordsController {
  constructor (MessagingService, $http) {
    this.$http = $http;
    this.MessagingService = MessagingService;

    // URL for api calls
    this.baseURL = '/app/querywords/data';

    // Selectors
    this.$modal = $('#queryword-modal');
    this.$requestSourceModal = $('#request-source-modal');

    // Globals
    this.loaded = false;
    this.querywords = [];
    this.sources = [];
    this.querywordOrder = '';

    this.newSourceUrl = '';
    this.newSourceDescription = '';

    // Set up new queryword
    this.newQueryword = {
      sources: [],
      queryword: '',
      frequency: 1
    };

    this.newFrequency = 1;

    this.pullCategories();
  }

  /**
   * Get categories.
   */
  pullCategories() {
    this.$http({
      method: 'GET',
      url: this.baseURL,
      headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
      }
    }).success(data => {
      this.sources = data.sources;
      let currentId = 0;
      data.sources.forEach(mainCategory => {
        mainCategory[1].forEach(subCategory => {
          subCategory[1].forEach(category => {
            this.newQueryword.sources.push({
              checked: false,
              name: category.category_name
            });
            category.id = currentId;
            currentId++;
          });
        });
      });

      this.querywords = data.querywords;
      this.loaded = true;
    });
  }

  /**
   * Remove a queryword.
   * @param {Object} queryword The queryword to remove.
   */
  removeQueryword (queryword) {
    let querywordIndex = this.querywords.indexOf(queryword);
    this.querywords.splice(querywordIndex,1);
    this.$http.post(this.baseURL, {
      'action': 'remove_request',
      'queryword': queryword.queryword
    });
  }

  /**
   * Create a new queryword.
   */
  createQueryword () {
    let sources = [];

    // Get the sources
    this.newQueryword.sources.forEach(source => {
      if (source.checked) {
        sources.push(source.name);
      }
    });

    // Send request to create.
    this.$http.post(this.baseURL, {
      'action': 'create_request',
      'queryword': this.newQueryword.queryword,
      'request_frequency': this.newQueryword.frequency,
      'categories': sources
    }).success(data => {
      if (data.type === 'danger') {
        this.MessagingService.danger(data.message);
      } else if (data.type === 'success') {
        this.MessagingService.success(data.message);
      }
    });

    // Get current date in YYYY-MM-DD format.
    let currentDate = new Date();
    currentDate = currentDate.yyyymmdd();

    // Add querywords locally.
    if (this.newQueryword.queryword.length > 0) {
      this.newQueryword.queryword.split(',').forEach(queryword => {
        if (queryword[0] === ' ') {
          queryword = queryword.replace(' ', '');
        }

        this.querywords.unshift({
          queryword: queryword,
          categories: sources,
          request_frequency: this.newQueryword.frequency*60,
          request_start: currentDate
        });
      });
    } else {
      this.querywords.unshift({
        queryword: '',
        categories: sources,
        request_frequency: this.newQueryword.frequency*60,
        request_start: currentDate
      });
    }

    // Reset fields.
    this.newQueryword.queryword = '';
    this.newQueryword.sources.forEach(source => {
      source.checked = false;
    });
  }

  /**
   * Remove a source from current queryword.
   * @param {String} source The source to remove.
   */
  removeSource (source) {
    let querywordIndex = this.querywords.indexOf(this.modalQueryword);
    let queryword = this.querywords[querywordIndex];
    queryword.categories.splice(queryword.categories.indexOf(source),1);
    this.$http.post(this.baseURL, {
      'action': 'remove_category',
      'queryword': queryword.queryword,
      'single_cat': source
    });
  }

  /**
   * Sets the order of results by expression.
   * @param {String} order What to order by.
   */
  setQuerywordOrder (order) {
    if (this.querywordOrder === order) {
      this.querywordOrder = '-' + order;
    } else if (this.querywordOrder === '-' + order) {
      this.querywordOrder = '';
    } else {
      this.querywordOrder = order;
    }
  }

  /**
   * Open a modal, filling it with a queryword.
   * @param {Object} queryword The queryword to fill the modal with.
   */
  openModal (queryword) {
    this.modalQueryword = queryword;
    this.newFrequency = queryword.request_frequency / 60;
    this.$modal.modal();
  }

  /**
   * Update the frequency of a queryword.
   */
  updateFrequency () {
    if (this.newFrequency*60 !== this.modalQueryword.request_frequency) {
      let querywordIndex = this.querywords.indexOf(this.modalQueryword);
      let queryword = this.querywords[querywordIndex];
      queryword.request_frequency = this.newFrequency*60;
      this.$http.post(this.baseURL, {
        'action': 'change_frequency',
        'queryword': queryword.queryword,
        'request_frequency': this.newFrequency
      });
    }
  }

  /**
   * Open modal for user to request source
   */
  requestSource() {
    this.$requestSourceModal.modal();
  }

  /**
   * Send request for new source
   */
  sendNewSource () {
    if (this.newSourceUrl && this.newSourceDescription) {
      this.$http.post('/app/request_source', {
        url: this.newSourceUrl,
        description: this.newSourceDescription
      }).success(data => {
        if (data.type === 'danger') {
          this.MessagingService.danger(data.message);
        } else if (data.type === 'success') {
          this.newSourceDescription = '';
          this.newSourceUrl = '';
          this.MessagingService.success(data.message);
        }
      });
    } else {
      this.MessagingService.danger('Please input a url and description.');
    }
  }
}

// Dependency injection
QuerywordsController.$inject = ['MessagingService', '$http'];

export default QuerywordsController;