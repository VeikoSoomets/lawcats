/**
 * Main angular app and controller for app/search
 *
 * Author: Uku Tammet
 */
'use strict';

/**
 * Not used currently
 * Format a date to yyyy-mm-dd
 * @param  {Date}   date Date to format
 * @return {String}      Date in yyyy-mm-dd
 */
/*
function formatDate(date) {
  let month = '' + (date.getMonth() + 1);
  let day = '' + date.getDate();
  let year = date.getFullYear();

  if (month.length < 2) month = '0' + month;
  if (day.length < 2) day = '0' + day;

  return [year, month, day].join('-');
}
*/

class SearchController {
  constructor ($http) {
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

    this.getSources();
  }

  /**
   * Get sources to search
   */
  getSources () {
    this.$http({
        method: 'GET',
        url: this.baseUrl,
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    }).success(data => {
      let currentId = 0;
      this.sources = data.sources;
      data.sources.forEach(mainCategory => {
        mainCategory[1].forEach(subCategory => {
          subCategory[1].forEach(category => {
            this.searchSources.push({
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

  /**
   * Execute a search from sources.
   * @param  {String} where Where to search from.
   */
  searchFrom (where) {
    this.loading = true;
    this.results = [];
    this.hasSearched = true;
    this.searchedSanctions = false;
    let queryDate = new Date();
    let queryAction = '';
    let sources = [];

    this.searchSources.forEach(source => {
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

      default: // Should never enter, this is for future guys.
        console.error('Entered default case in searchFrom');
    }

    this.$http.post(this.baseUrl, {
      action: queryAction,
      queryword: this.querywords,
      date_algus: queryDate,
      // TODO: formatDate() requires date, but sometimes we are not giving date.
      categories: sources
    }).success(response => {
      this.results = response.search_results;
      this.querywords = '';
      this.searchSources.forEach(source => {
        source.checked = false;
      });
      this.loading = false;
    }).error(err => {
      console.error(err);
      this.loading = false;
    });
  }
}

SearchController.$inject = ['$http'];

export default SearchController;
