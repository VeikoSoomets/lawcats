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
  let month = '' + (date.getMonth() + 1);
  let day = '' + date.getDate();
  let year = date.getFullYear();

  if (month.length < 2) month = '0' + month;
  if (day.length < 2) day = '0' + day;

  return [year, month, day].join('-');
}

class LandingController {
  constructor($http) {
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

  /**
   * Get sources to search
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


  /**
   * Execute search with querywords and sources.
   */
  search () {
    this.hasSearched = true;
    this.loading = true;
    let queryDate = new Date();

    let filteredSources = this.sources
      .filter(source => source.checked)
      .map(source => source.category_name);
    console.log('Sources: ' + filteredSources);
    console.log('Querywords: ' + this.querywords);

    this.$http.post(this.searchUrl, {
      action: 'landing_search',
      queryword: this.querywords,
      date_algus: formatDate(queryDate),
      categories: filteredSources
    }).success(response => {
      let currentNum = 0;
      this.results = response.search_results.filter(() => {
        currentNum++;
        return currentNum < this.maxResultsNum;
      }).map(result => {
        if (result.name || result.programs) {
          let normalizedResult = {
            result_title: result.name,
            categories: result.programs,
            result_link: '#'
          };

          return normalizedResult;
        }

        return result;
      });
      console.log(response);
      this.querywords = '';
      this.sources.forEach(source => {
        source.checked = false;
      });
      this.loading = false;
    }).error(err => {
      console.error(err);
      this.loading = false;
    });
  }
}

LandingController.$inject = ['$http'];

export default LandingController;