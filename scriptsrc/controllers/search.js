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
  constructor (MessagingService, $http) {
    this.$http = $http;
    this.MessagingService = MessagingService;

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
    let self = this;

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
      setTimeout(function(){
        $('.result-title-link').html(function(_, html) {
          function capitalizeFirstLetter(string) {
              return string.charAt(0).toUpperCase() + string.slice(1);
          }
          var words = self.querywords.split(' ');
          var returnHtml = html;
          debugger;
          for (var querywordIndex in words){
            var queryword = words[querywordIndex];
            var querywordCapitalized = capitalizeFirstLetter(queryword);
            returnHtml = returnHtml.replace(queryword,
                '<span class="highlight-text">'+queryword+'</span>');
            returnHtml = returnHtml.replace(querywordCapitalized ,
                '<span class="highlight-text">'+querywordCapitalized+'</span>');
          }
          return returnHtml;
        });
      }, 500);
      this.loading = false;
    }).error(err => {
      console.error(err);
      this.loading = false;
    });
  }
}

SearchController.$inject = ['MessagingService', '$http'];

export default SearchController;
