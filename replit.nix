{ pkgs }: {
  deps = [
    pkgs.python310Full
    pkgs.python310Packages.flask
    pkgs.python310Packages.flask_cors
    pkgs.python310Packages.sqlite3
  ];
}
