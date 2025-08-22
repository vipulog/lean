{pkgs, ...}:
pkgs.writeText "init" ''
  session.screen0.workspaces: 1
  session.screen0.workspacewarping: false
  session.screen0.edgeSnapThreshold: 0
  session.screen0.titlebar.left:
  session.screen0.titlebar.right:
  session.screen0.windowPlacement: RowMinOverlapPlacement
  session.configVersion: 13
  session.appsFile: ${./apps}
  session.keyFile: ${./keys}
  session.menuFile: ${./menu}
  session.slitlistFile: ${./slitlist}
  session.styleFile: ${./styles/draggable-window}
  session.styleOverlay: ${./overlay}
  session.screen0.windowMenu: ${./windowmenu}
''
