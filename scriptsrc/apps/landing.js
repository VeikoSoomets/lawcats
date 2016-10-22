'use strict';
/* global angular */

import LandingController from '../controllers/LandingController';
import ngCategories from '../directives/ngCategories';

angular.module('landingApp', [])
  .directive('ngCategories', ngCategories)
  .controller('LandingController', LandingController);