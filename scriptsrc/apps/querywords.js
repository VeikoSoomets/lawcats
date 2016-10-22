'use strict';
/* global angular */
import QuerywordsController from '../controllers/querywords';
import MessagingService from '../services/MessagingService';
import ngCategories from '../directives/ngCategories';

// Setup angular app
angular.module('querywordsApp', [])
  .service('MessagingService', MessagingService)
  .directive('ngCategories', ngCategories)
  .controller('QuerywordsController', QuerywordsController);