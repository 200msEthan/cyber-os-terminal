# Passing arguments through shell shortcuts

The Bash/zsh and PowerShell shortcuts keep their documented positional arguments and forward
additional arguments to the underlying Python CLI without splitting quoted values.

```sh
cyber-kill 8000                # graceful termination (SIGTERM on POSIX)
cyber-kill 8000 --force        # explicit hard kill (SIGKILL on POSIX, /F on Windows)
cyber-ports localhost 22,80 --help
cyber-find "some file" "directory with spaces" --help
```

`cyber-ports` still defaults to `127.0.0.1` and the `common` port range; pass the target and
range before extra flags. `cyber-find` likewise takes a query and directory before extra flags.
Other fixed-positional tools such as `cyber-hash` take their value before extra flags.
Forwarded flags must be supported by the underlying CLI; this does not add `--json` or `--timeout`.

The multi-word query shortcuts (`cyber-search`, `cyber-history`, `cyber-web`) retain their
existing query handling. Their PowerShell multi-word behavior is tracked separately in #50.

Run `python -m unittest discover -s tests -v` to verify argument forwarding. Tests source the
profiles in installed Bash, zsh, or PowerShell instances and record Python arguments. They do
not scan remote hosts or stop any processes. Tests for unavailable shell families are skipped;
run on both a POSIX host and Windows for coverage of all profiles.
