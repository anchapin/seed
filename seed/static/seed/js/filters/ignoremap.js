/**
 * :copyright (c) 2014 - 2022, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.
 * :author
 */
angular.module('ignoremap', []).filter('ignoremap', function () {

  return function (input) {
    if (_.isEmpty(input)) return '------ Ignore Row ------';
    return input;
  };

});
