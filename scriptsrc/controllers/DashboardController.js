/**
 * Angular controller for app/dashboard
 */
/* global Chart */

'use strict';

import randomColor from 'randomcolor';

class DashboardController {
  constructor($http) {
    // Save dependencies
    this.$http = $http;
    this.loadingCharts = true;
    this.loadingResults = true;

    this.selectors = {
      pie: '#pie-chart-elem',
      line: '#line-chart-elem'
    };

    this.querywordColors = {};

    this.charts = {
      pie: null,
      line: null
    };

    this.results = [];

    // Retrieve charts data and render.
    this.getChartsFromApi();

    // Retrieve results
    this.getResultsFromApi();
  }

  getResultsFromApi() {
    this.$http.post('/app/results/data', {
      action: 'get_results',
      result_id: null
    }).success(response => {
      if (response.data.constructor === Array) {
        this.results = response.data;
      }

      this.loadingResults = false;
    }).error(error => {
      console.error(error);
      this.loadingResults = false;
    });
  }

  getChartsFromApi() {
    this.$http.get('/app/charts')
      .success(response => {

        if (response.charts.pie.length) {
          // Get unique querywords
          const querywords = response.charts.line.datasets
            .map(dataset => dataset.queryword)
            .filter((element, index, self) => self.indexOf(element) === index);

          // Generate colors for querywords
          querywords.forEach(queryword => {
            this.querywordColors[queryword] = randomColor({
              seed: Math.random()
            });
          });

          // Aggregate datasets from datapoints
          const lineDatasets = querywords.map(queryword => {
            return {
              label: queryword,
              strokeColor: this.querywordColors[queryword],
              pointColor: this.querywordColors[queryword],
              data: response.charts.line.labels
                .map(label => {
                  const potentialMatch = response.charts.line.datasets
                    .filter(dataset => {
                      return (
                        dataset.queryword === queryword &&
                        dataset.result_date === label 
                      );
                    });

                  if (potentialMatch.length) {
                    return potentialMatch[0].count; 
                  }

                  return 0;
                }).reverse()
            };
          });

          const chartData = {
            pie: response.charts.pie.map(dataset => {
              return {
                value: dataset.count,
                label: dataset.queryword,
                color: this.querywordColors[dataset.queryword]
              };
            }),

            line: {
              labels: response.charts.line.labels.reverse(),
              datasets: lineDatasets,
            }
          };

          this.loadingCharts = false;

          this.renderCharts(chartData);
        }

        this.loadingCharts = false;
      })
      .error(err => {
        this.loadingCharts = false;
        console.error(err);
      });
  }

  renderCharts(datasets) {
    const chartsContexts = {
      pie: $(this.selectors.pie).get(0).getContext('2d'),
      line: $(this.selectors.line).get(0).getContext('2d')
    };

    // Create the charts
    this.charts.pie = new Chart(chartsContexts.pie)
      .Pie(datasets.pie, {
        responsive: true
      });
      
    this.charts.line = new Chart(chartsContexts.line)
      .Line(datasets.line, {
        responsive: true,
        datasetFill: false,
        maintainAspectRatio: false,
        multiTooltipTemplate: '<%= datasetLabel %> - <%= value %>'
      });
  }
}

DashboardController.$inject = ['$http'];

export default DashboardController;