'use strict';
/* global angular */
import SearchController from '../controllers/search';
import MessagingService from '../services/MessagingService';
import ngCategories from '../directives/ngCategories';

angular.module('searchApp', [])
  .service('MessagingService', MessagingService)
  .directive('ngCategories', ngCategories)
  .controller('SearchController', SearchController);