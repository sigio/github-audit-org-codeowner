# github-check-codeowners.py

Check CODEOWNERS files in all repositories of a github-organisation.

This will check for presence of a CODEOWNERS file, and check if all listed
users and groups in the file have actual write-permissions to the specified
repository.

You can either check all repositories in the organisation, or limit checking
to a single repository by specifying this with `--repo org/reponame` argument.

Optionally a `--quiet` argument can be speficied to limit verbose output
to just the warning messages/findings

This script was mostly written by AI, so I do not claim any copyright on
this, after the initial version any modifications were made by me to get
it to a state that fit my purpose.
