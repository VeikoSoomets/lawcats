'use strict';

class CategoriesController {

  constructor() {
    this.idMap = {};
    this.currentId = 0;
  }

  /**
   * Check if category is allowed.
   * @param  {String} category The maincategory to check.
   * @return {Boolean}         If it's allowed.
   */
  isAllowedCategory(category) {
    if (typeof this.allowedCategories !== 'undefined') {
      return (this.allowedCategories.indexOf(category) !== -1);
    } else if (typeof this.forbiddenCategories !== 'undefined') {
      return (this.forbiddenCategories.indexOf(category) === -1);
    }

    return true;
  }

  /**
   * Nets an id from a category name.
   * @param  {String} category The category to get id from.
   * @return {String}          ID.
   */
  getIdFromCategory(category) {
    if (category in this.idMap) {
      return this.idMap[category];
    } else {
      const newCat = 'category' + category.replace(/\W+/g, '') + this.currentId;
      this.idMap[category] = newCat;
      this.currentId++;
      return newCat;
    }
  }

  /**
   * Check all the sources under a given subcategory.
   * @param  {Array} subcategory All categories under subcategory.
   */
  checkAll(subcategory) {
    let counter = 0;
    
    this.ngModel.forEach(category => {
      let shouldBeChecked = false;
      
      subcategory.forEach(subcat => {
        if (subcat.category_name === category.name) {
          shouldBeChecked = true;
        }
      });
      
      if (shouldBeChecked) {
        if (category.checked) counter++;
        category.checked = false;
      }
    });

    if (counter !== subcategory.length) {
      this.ngModel.forEach(category => {
        subcategory.forEach(subcat => {
          if (subcat.category_name === category.name) {
            category.checked = true;
          }
        });
      });
    }
  }

  /**
   * Check if all categories in a subcategory are checked.
   * @param  {Array} subcategory The subcategory to check.
   * @return {Boolean}            If all are checked.
   */
  areAllChecked(subcategory) {
    return subcategory.reduce((accumulator, category) => {
      if (!accumulator) {
        return false;
      }
      const isChecked = this.ngModel.reduce((accumulator, ngCat) => {
        if (accumulator) {
          return true;
        }
        if (category.category_name === ngCat.name && ngCat.checked) {
          return true;
        }
        return false;
      }, false);
      return isChecked;
    }, true);
  }
}

export default function () {
  return {
    restrict: 'E',
    scope: {
      ngModel: '=',
      categories: '=',
      allowedCategories: '=?',
      forbiddenCategories: '=?'
    },
    controller: CategoriesController,
    controllerAs: 'catCtrl',
    bindToController: true,
    templateUrl: '/static/js/templates/categories.html',
  };
}