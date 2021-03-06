# Copyright (c) 2021 SUSE LLC
# Licensed under the terms of the MIT license.
#
# If you this feature, then comment out sle_ssh_minion.feature in
# testsuite/run_sets/init_clients.yml and set
# $service_pack_migration_enabled = false at
# testsuite/features/support/env.rb

@ssh_minion
@scope_salt_ssh
@scope_sp_migration
@service_pack_migration
Feature: Service pack migration for SSH minion
  In order to update my systems
  As an authorized user
  I want to migrate from one service pack to the other on SSH managed minions

  Scenario: Register this SSH minion for service pack migration
    Given I am authorized
    When I go to the bootstrapping page
    Then I should see a "Bootstrap Minions" text
    When I check "manageWithSSH"
    And I enter the hostname of "ssh_spack_migrated_minion" as "hostname"
    And I enter "linux" as "password"
    And I select "1-SUSE-SSH-SP-MIGRATION-x86_64" from "activationKeys"
    And I select the hostname of "proxy" from "proxies"
    And I click on "Bootstrap"
    And I wait until I see "Successfully bootstrapped host!" text
    And I am on the System Overview page
    And I wait until I see the name of "ssh_spack_migrated_minion", refreshing the page
    And I wait until onboarding is completed for "ssh_spack_migrated_minion"

  Scenario: Migrate this SSH minion to SLE 15 SP2
    Given I am on the Systems overview page of this "ssh_spack_migrated_minion"
    When I follow "Software" in the content area
    And I follow "SP Migration" in the content area
    And I wait until I see "Target Products:" text, refreshing the page
    And I click on "Select Channels"
    And I wait until I see "SUSE Linux Enterprise Server 15 SP2 x86_64" text
    And I click on "Schedule Migration"
    And I should see a "Service Pack Migration - Confirm" text
    And I click on "Confirm"
    Then I should see a "This system is scheduled to be migrated to" text

  Scenario: Check the migration status for this SSH minion
    Given I am on the Systems overview page of this "ssh_spack_migrated_minion"
    When I follow "Events"
    And I follow "History"
    And I wait at most 600 seconds until event "Service Pack Migration scheduled by admin" is completed

  Scenario: Check the migration is successful for this SSH minion
    Given I am on the Systems overview page of this "ssh_spack_migrated_minion"
    When I follow "Details" in the content area
    Then I should see a "SUSE Linux Enterprise Server 15 SP2" text

  Scenario: Subscribe the service pack migrated SSH minion to a base channel
    Given I am on the Systems overview page of this "ssh_spack_migrated_minion"
    When I follow "Software" in the content area
    And I follow "Software Channels" in the content area
    And I wait until I do not see "Loading..." text
    And I check radio button "Test-Channel-x86_64"
    And I wait until I do not see "Loading..." text
    And I click on "Next"
    Then I should see a "Confirm Software Channel Change" text
    When I click on "Confirm"
    Then I should see a "Changing the channels has been scheduled." text
    And I wait until event "Subscribe channels scheduled by admin" is completed
