/**
 * :copyright (c) 2014 - 2019, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.
 * :author
 */
angular.module('BE.seed.controller.column_mappings', [])
  .controller('column_mappings_controller', [
    '$scope',
    '$state',
    '$uibModal',
    'Notification',
    'auth_payload',
    'column_mapping_presets_payload',
    'column_mappings_service',
    'inventory_service',
    'mappable_property_columns_payload',
    'mappable_taxlot_columns_payload',
    'organization_payload',
    'urls',
    function (
      $scope,
      $state,
      $uibModal,
      Notification,
      auth_payload,
      column_mapping_presets_payload,
      column_mappings_service,
      inventory_service,
      mappable_property_columns_payload,
      mappable_taxlot_columns_payload,
      organization_payload,
      urls
    ) {
      $scope.org = organization_payload.organization;
      $scope.auth = auth_payload.auth;

      $scope.state = $state.current;

      $scope.mappable_property_columns = mappable_property_columns_payload;
      $scope.mappable_taxlot_columns = mappable_taxlot_columns_payload;

      // Helpers to convert to and from DB column names and column display names
      var mapping_db_to_display = function(mapping) {
        var mappable_column;

        if (mapping.to_table_name === "PropertyState") {
          mappable_column = _.find($scope.mappable_property_columns, {column_name: mapping.to_field});
        } else {
          mappable_column = _.find($scope.mappable_taxlot_columns, {column_name: mapping.to_field});
        }

        if (mappable_column) {
          mapping.to_field = mappable_column.displayName;
        }
      };

      var mapping_display_to_db = function(mapping) {
        var mappable_column;
        if (mapping.to_table_name === "PropertyState") {
          mappable_column = _.find($scope.mappable_property_columns, {displayName: mapping.to_field});
        } else {
          mappable_column = _.find($scope.mappable_taxlot_columns, {displayName: mapping.to_field});
        }

        if (mappable_column) {
          mapping.to_field = mappable_column.column_name;
        }
      };

      // On page load, convert DB field names to display names
      _.forEach(column_mapping_presets_payload, function(preset) {
        _.forEach(preset.mappings, mapping_db_to_display);
      });

      $scope.presets = column_mapping_presets_payload;

      $scope.dropdown_selected_preset = $scope.current_preset = $scope.presets[0] || {};

      // Inventory Types
      $scope.setAllFields = '';
      $scope.setAllFieldsOptions = [{
        name: 'Property',
        value: 'PropertyState'
      }, {
        name: 'Tax Lot',
        value: 'TaxLotState'
      }];

      var analyze_chosen_inventory_types = function () {
        var chosenTypes = _.uniq(_.map($scope.dropdown_selected_preset.mappings, 'to_table_name'));

        if (chosenTypes.length === 1) {
          $scope.setAllFields = _.find($scope.setAllFieldsOptions, {value: chosenTypes[0]});
        } else {
          $scope.setAllFields = '';
        }
      };

      // On load...
      analyze_chosen_inventory_types()

      $scope.updateSingleInventoryTypeDropdown = function () {
        analyze_chosen_inventory_types();

        $scope.flag_change();
      };

      $scope.setAllInventoryTypes = function () {
        _.forEach($scope.dropdown_selected_preset.mappings, function (mapping) {
          if (mapping.to_table_name !== $scope.setAllFields.value) {
            mapping.to_table_name = $scope.setAllFields.value;
            $scope.flag_change();
          }
        });
      };

      // Preset-level CRUD modal-rending actions
      $scope.new_preset = function () {
        var modalInstance = $uibModal.open({
          templateUrl: urls.static_url + 'seed/partials/column_mapping_preset_modal.html',
          controller: 'column_mapping_preset_modal_controller',
          resolve: {
            action: _.constant('new'),
            data: _.constant($scope.dropdown_selected_preset),
            org_id: _.constant($scope.org.id),
          }
        });

        modalInstance.result.then(function (new_preset) {
          $scope.presets.push(new_preset);
          $scope.dropdown_selected_preset = $scope.current_preset = _.last($scope.presets);

          $scope.changes_possible = false;
          Notification.primary('Saved ' + $scope.dropdown_selected_preset.name);
        });
      };

      $scope.rename_preset = function () {
        var old_name = $scope.dropdown_selected_preset.name;

        var modalInstance = $uibModal.open({
          templateUrl: urls.static_url + 'seed/partials/column_mapping_preset_modal.html',
          controller: 'column_mapping_preset_modal_controller',
          resolve: {
            action: _.constant('rename'),
            data: _.constant($scope.dropdown_selected_preset),
            org_id: _.constant($scope.org.id),
          }
        });

        modalInstance.result.then(function (new_name) {
          var preset_index = _.findIndex($scope.presets, ['id', $scope.dropdown_selected_preset.id]);
          $scope.presets[preset_index].name = new_name;

          Notification.primary('Renamed ' + old_name + ' to ' + new_name);
        });
      };

      $scope.remove_preset = function () {
        var old_preset = angular.copy($scope.dropdown_selected_preset);

        var modalInstance = $uibModal.open({
          templateUrl: urls.static_url + 'seed/partials/column_mapping_preset_modal.html',
          controller: 'column_mapping_preset_modal_controller',
          resolve: {
            action: _.constant('remove'),
            data: _.constant($scope.dropdown_selected_preset),
            org_id: _.constant($scope.org.id),
          }
        });

        modalInstance.result.then(function () {
          _.remove($scope.presets, old_preset);
          $scope.dropdown_selected_preset = $scope.current_preset = $scope.presets[0] || {};
          $scope.changes_possible = false;
        });
      };

      $scope.save_preset = function () {
        var preset_id = $scope.dropdown_selected_preset.id;
        var preset_index = _.findIndex($scope.presets, ['id', preset_id]);

        _.forEach($scope.presets[preset_index].mappings, mapping_display_to_db);
        var updated_data = {mappings: $scope.presets[preset_index].mappings};

        column_mappings_service.update_column_mapping_preset($scope.org.id, preset_id, updated_data).then(function (result) {
          _.forEach($scope.presets[preset_index].mappings, mapping_db_to_display);
          $scope.presets[preset_index].updated = result.data.updated;

          $scope.changes_possible = false;
          Notification.primary('Saved ' + $scope.dropdown_selected_preset.name);
        });
      };

      // Track changes to help prevent losing changes when data could be lost
      $scope.changes_possible = false;

      $scope.flag_change = function () {
        $scope.changes_possible = true;
      };

      $scope.check_for_changes = function () {
        if ($scope.changes_possible) {
          $uibModal.open({
            template: '<div class="modal-header"><h3 class="modal-title" translate>You have unsaved changes</h3></div><div class="modal-body" translate>You will lose your unsaved changes if you switch presets without saving. Would you like to continue?</div><div class="modal-footer"><button type="button" class="btn btn-warning" ng-click="$dismiss()" translate>Cancel</button><button type="button" class="btn btn-primary" ng-click="$close()" autofocus translate>Switch Presets</button></div>'
          }).result.then(function () {
            $scope.changes_possible = false;
          }).catch(function () {
            $scope.dropdown_selected_preset = $scope.current_preset;
            return;
          });
        }

        $scope.current_preset = $scope.dropdown_selected_preset;
        analyze_chosen_inventory_types();
      };

      // Add and remove column methods
      $scope.add_new_column = function () {
        if ($scope.dropdown_selected_preset.mappings[0]) {
          $scope.dropdown_selected_preset.mappings.push(
            {from_field: "", from_units: null, to_field: "", to_table_name: ""}
          );
        } else {
          $scope.dropdown_selected_preset.mappings = [
            {from_field: "", from_units: null, to_field: "", to_table_name: ""}
          ];
        }
        $scope.flag_change();
      };

      $scope.remove_column = function (index) {
        $scope.dropdown_selected_preset.mappings.splice(index, 1);
        $scope.flag_change();
      };
    }]);
