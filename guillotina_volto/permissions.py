from guillotina import configure


configure.role("Contributor", "Contributor", "Can add content", False)
configure.role("Editor", "Editor", "Can modify content", False)
configure.role("Reader", "Reader", "Can view content", False)
configure.role("Reviewer", "Reviewer", "Can review content", False)
configure.role("SiteAdministrator", "Site Administrator", "Can manage all content", False)
configure.role("Manager", "Manager", "Can manage content", False)

configure.permission("guillotina.ManageVersioning", "Ability to modify versioning on an object")
configure.permission("guillotina.ManageConstraints", "Allow to check and change type constraints")

configure.permission("guillotina.AccessControlPanel", "Access control panel")

configure.permission("guillotina.ViewComments", "View comments")
configure.permission("guillotina.ModifyComments", "Modify comments")
configure.permission("guillotina.AddComments", "Add comments")
configure.permission("guillotina.DeleteComments", "Delete comments")
configure.permission("guillotina.DeleteAllComments", "Delete all comments")

configure.grant(permission="guillotina.ManageVersioning", role="guillotina.Manager")

configure.grant(permission="guillotina.ManageConstraints", role="guillotina.Manager")

configure.grant(permission="guillotina.ManageConstraints", role="guillotina.ContainerAdmin")

configure.grant(permission="guillotina.ReviewContent", role="guillotina.Reviewer")

configure.grant(permission="guillotina.ReviewContent", role="guillotina.Manager")

configure.grant(permission="guillotina.RequestReview", role="guillotina.Manager")

configure.grant(permission="guillotina.RequestReview", role="guillotina.Owner")

configure.grant(permission="guillotina.RequestReview", role="guillotina.ContainerAdmin")
configure.grant(permission="guillotina.AccessControlPanel", role="guillotina.ContainerAdmin")

configure.grant(permission="guillotina.SearchContent", role="guillotina.Manager")

configure.grant(permission="guillotina.ViewComments", role="guillotina.Manager")

configure.grant(permission="guillotina.AddComments", role="guillotina.Manager")

configure.grant(permission="guillotina.ModifyComments", role="guillotina.Manager")

configure.grant(permission="guillotina.DeleteComments", role="guillotina.Manager")

configure.grant(permission="guillotina.DeleteAllComments", role="guillotina.Manager")

configure.grant(permission="guillotina.ViewComments", role="guillotina.Owner")

configure.grant(permission="guillotina.AddComments", role="guillotina.Owner")

configure.grant(permission="guillotina.ModifyComments", role="guillotina.Owner")

configure.grant(permission="guillotina.DeleteComments", role="guillotina.Owner")

configure.grant(permission="guillotina.DeleteAllComments", role="guillotina.Owner")

# Contributor
configure.grant(permission="guillotina.AddContent", role="Contributor")
configure.grant(permission="guillotina.AccessContent", role="Contributor")
configure.grant(permission="guillotina.ViewContent", role="Contributor")

# Reader
configure.grant(permission="guillotina.ViewContent", role="Reader")
configure.grant(permission="guillotina.AccessContent", role="Reader")
configure.grant(permission="guillotina.DuplicateContent", role="Reader")

# Reviewer
configure.grant(permission="guillotina.ViewContent", role="Reviewer")
configure.grant(permission="guillotina.AccessContent", role="Reviewer")
configure.grant(permission="guillotina.ReviewContent", role="Reviewer")


# Editor
configure.grant(permission="guillotina.ViewContent", role="Editor")
configure.grant(permission="guillotina.AccessContent", role="Editor")
configure.grant(permission="guillotina.ModifyContent", role="Editor")
configure.grant(permission="guillotina.MoveContent", role="Editor")
configure.grant(permission="guillotina.DuplicateContent", role="Editor")
configure.grant(permission="guillotina.ReindexContent", role="Editor")

# Manager
configure.grant(permission="guillotina.ManageVersioning", role="Manager")
configure.grant(permission="guillotina.ManageConstraints", role="Manager")
configure.grant(permission="guillotina.ReviewContent", role="Manager")
configure.grant(permission="guillotina.RequestReview", role="Manager")
configure.grant(permission="guillotina.SearchContent", role="Manager")
configure.grant(permission="guillotina.ViewComments", role="Manager")
configure.grant(permission="guillotina.AddComments", role="Manager")
configure.grant(permission="guillotina.ModifyComments", role="Manager")
configure.grant(permission="guillotina.DeleteComments", role="Manager")
configure.grant(permission="guillotina.DeleteAllComments", role="Manager")

# Site Administrator
configure.grant(permission="guillotina.ViewContent", role="SiteAdministrator")
configure.grant(permission="guillotina.AddContent", role="SiteAdministrator")
configure.grant(permission="guillotina.AccessContent", role="SiteAdministrator")
configure.grant(permission="guillotina.ModifyContent", role="SiteAdministrator")
configure.grant(permission="guillotina.MoveContent", role="SiteAdministrator")
configure.grant(permission="guillotina.DuplicateContent", role="SiteAdministrator")
configure.grant(permission="guillotina.DeleteContent", role="SiteAdministrator")
configure.grant(permission="guillotina.ReindexContent", role="SiteAdministrator")
configure.grant(permission="guillotina.SearchContent", role="SiteAdministrator")
configure.grant(permission="guillotina.ChangePermissions", role="SiteAdministrator")
configure.grant(permission="guillotina.SeePermissions", role="SiteAdministrator")

configure.grant(permission="guillotina.ManageAddons", role="SiteAdministrator")
configure.grant(permission="guillotina.ReadConfiguration", role="SiteAdministrator")
configure.grant(permission="guillotina.WriteConfiguration", role="SiteAdministrator")
configure.grant(permission="guillotina.RegisterConfigurations", role="SiteAdministrator")
configure.grant(permission="guillotina.ManageCatalog", role="SiteAdministrator")
configure.grant(permission="guillotina.RawSearchContent", role="SiteAdministrator")
configure.grant(permission="guillotina.CacheManage", role="SiteAdministrator")
configure.grant(permission="guillotina.Manage", role="SiteAdministrator")
configure.grant(permission="guillotina.GetDatabases", role="SiteAdministrator")

configure.grant(permission="guillotina.ReviewContent", role="SiteAdministrator")
configure.grant(permission="guillotina.RequestReview", role="SiteAdministrator")
configure.grant(permission="guillotina.ViewComments", role="SiteAdministrator")
configure.grant(permission="guillotina.AddComments", role="SiteAdministrator")
configure.grant(permission="guillotina.ModifyComments", role="SiteAdministrator")
configure.grant(permission="guillotina.DeleteComments", role="SiteAdministrator")
configure.grant(permission="guillotina.DeleteAllComments", role="SiteAdministrator")
configure.grant(permission="guillotina.ManageUsers", role="SiteAdministrator")
configure.grant(permission="guillotina.AccessControlPanel", role="SiteAdministrator")
