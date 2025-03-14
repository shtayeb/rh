from django.conf import settings
from django.urls import path

from .views import (
    activity_plans as activity_plans,
)
from .views import (
    budget_progress as budget_progress,
)
from .views import (
    clusters as clusters_views,
)
from .views import (
    exports as export_views,
)
from .views import (
    organizations as organizations,
)
from .views import (
    projects as projects,
)
from .views import (
    target_locations as target_locations,
)
from .views.views import (
    get_activity_domain_types,
    get_activity_type_indicators,
    get_locations_details,
    home,
    landing_page,
    load_activity_domains,
    load_facility_sites,
    test_email,
)

urlpatterns = [
    path("", landing_page, name="landing"),
    path("home", home, name="home"),
    # Organization CRUD
    path("organizations/search", organizations.search, name="organizations-search"),
    path("organizations/create", organizations.organization_register, name="organizations-create"),
    path(
        "donor/register",
        organizations.donor_register,
        name="donor-register",
    ),
    path("organizations/<str:code>", organizations.show, name="organizations-show"),
    path(
        "organizations/<int:org_pk>/target-locations",
        organizations.target_locations,
        name="organizations-target-locations",
    ),
    # Projects CRUD
    path("projects", projects.org_projects_list, name="projects-list"),
    path(
        "projects/export-ap-import-template/<int:pk>",
        projects.export_activity_plans_import_template,
        name="projects-ap-import-template",
    ),
    path(
        "projects/import-activity-plans/<int:pk>", projects.import_activity_plans, name="projects-import-activity-plans"
    ),
    path("projects/clusters", projects.users_clusters_projects_list, name="user-clusters-projects-list"),
    path("projects/clusters/<str:cluster>", projects.cluster_projects_list, name="cluster-projects-list"),
    path("users/clusters/<str:cluster>", projects.cluster_users, name="cluster-users"),
    # cluster
    path("clusters/<str:cluster>", clusters_views.cluster_home, name="clusters-home"),
    path("clusters/<str:cluster>/reports", clusters_views.pending_reports, name="clusters-reports"),
    #
    path("projects/create", projects.create_project, name="projects-create"),
    path(
        "projects/<int:pk>",
        projects.projects_detail,
        name="projects-detail",
    ),
    path(
        "projects/<int:pk>/update",
        projects.update_project,
        name="projects-update",
    ),
    path(
        "projects/<int:pk>/delete",
        projects.delete_project,
        name="projects-delete",
    ),
    path(
        "projects/<int:pk>/complete",
        projects.complete_project,
        name="complete_project",
    ),
    path(
        "projects/project-plan/<int:pk>/archive",
        projects.archive_project,
        name="archive_project",
    ),
    path(
        "projects/project-plan/<int:pk>/unarchive",
        projects.unarchive_project,
        name="unarchive_project",
    ),
    path(
        "projects/project-plan/<int:pk>/copy",
        projects.copy_project,
        name="copy_project",
    ),
    path(
        "projects/<int:pk>/submit",
        projects.submit_project,
        name="projects-submit",
    ),
    # load
    path(
        "activity-domains/activity-types",
        get_activity_domain_types,
        name="activity-domains-types",
    ),
    path(
        "activity-types/indicators",
        get_activity_type_indicators,
        name="activity-types-indicators",
    ),
    path(
        "indicator/types",
        activity_plans.update_indicator_type,
        name="update-indicator-type",
    ),
    path(
        "transfer-mechanism/types",
        activity_plans.get_transfer_mechanism_types,
        name="get-transfer-mechanism-types",
    ),
    path(
        "unit/types",
        activity_plans.get_unit_types,
        name="get-unit-types",
    ),
    path(
        "show/indicator/detail",
        activity_plans.hx_show_indicator_details,
        name="hx-show-indicator-details",
    ),
    # Projects Activity Plannings CRUD
    path(
        "activity-plans/<int:pk>/update",
        activity_plans.update_activity_plan,
        name="activity-plans-update",
    ),
    path(
        "activity-plans/<int:pk>/state/update",
        activity_plans.update_activity_plan_state,
        name="activity-plans-update-state",
    ),
    path(
        "activity-plans/<int:pk>/delete",
        activity_plans.delete_activity_plan,
        name="activity-plans-delete",
    ),
    path(
        "activity-plans/project/<int:project>/create",
        activity_plans.create_activity_plan,
        name="activity-plans-create",
    ),
    path(
        "activity-plans/<int:pk>/copy",
        activity_plans.copy_activity_plan,
        name="activity-plans-copy",
    ),
    path(
        "projects/<int:project>/target-locations",
        target_locations.list_target_locations,
        name="target-locations-list",
    ),
    path(
        "projects/<int:project>/activity-plans",
        activity_plans.list_activity_plans,
        name="activity-plans-list",
    ),
    # Projects Target Locations CRUD
    path(
        "target-locations/<int:pk>/state/update",
        target_locations.update_target_location_state,
        name="target-locations-update-state",
    ),
    path(
        "target-locations/<int:pk>/update",
        target_locations.update_target_location,
        name="target-locations-update",
    ),
    path(
        "target-locations/activity-plan/<int:activity_plan>/create",
        target_locations.create_target_location,
        name="target-locations-create",
    ),
    path(
        "projects/<int:project>/target_location/<str:location>/copy",
        target_locations.copy_target_location,
        name="copy_location",
    ),
    path(
        "target-locations/<int:pk>/delete",
        target_locations.delete_target_location,
        name="target-locations-delete",
    ),
    # Financial Reporting
    path(
        "projects/<int:project>/financials/budget_progress",
        budget_progress.create_project_budget_progress_view,
        name="create_project_budget_progress",
    ),
    path(
        "projects/<int:project>/budget_progress/<int:pk>/update",
        budget_progress.update_budget_progress,
        name="update-budget-progress",
    ),
    path(
        "projects/budget_progress/<int:project>/<int:budget>/copy",
        budget_progress.copy_budget_progress,
        name="copy-budget-progress",
    ),
    path(
        "projects/budget_progress/<int:pk>/delete",
        budget_progress.delete_budget_progress,
        name="delete_budget",
    ),
    # Ajax for data load
    path(
        "ajax/load-activity_domains",
        load_activity_domains,
        name="ajax-load-activity_domains",
    ),
    path(
        "ajax/load-locations-details",
        get_locations_details,
        name="get-locations-details",
    ),
    path(
        "ajax/load-facility_sites",
        load_facility_sites,
        name="ajax-load-facility_sites",
    ),
    # Bulk Exports
    path(
        "project/export-excel/<str:format>/",
        export_views.project_export_excel_view,
        name="export_project_excel",
    ),
    # single project export
    path(
        "project/export/<str:pk>/<str:format>",
        export_views.single_project_export,
        name="single-project-export",
    ),
]

if settings.DEBUG:
    urlpatterns.append(path(route="test-email/<str:template_name>", view=test_email, name="test-email"))
