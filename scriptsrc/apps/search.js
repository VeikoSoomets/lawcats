'use strict';
/* global angular */
import SearchController from '../controllers/search';
import ngCategories from '../directives/ngCategories';

angular.module('searchApp', [])
  .directive('ngCategories', ngCategories)
  .controller('SearchController', SearchController);