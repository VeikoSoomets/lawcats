/**
 * Dashboard angular app
 */
'use strict';
/* global angular */
import DashboardController from '../controllers/DashboardController';

angular.module('dashboardApp', [])
  .controller('DashboardController', DashboardController);