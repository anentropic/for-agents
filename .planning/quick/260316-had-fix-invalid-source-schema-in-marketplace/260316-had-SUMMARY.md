# Quick Task 260316-had: Fix invalid source schema in marketplace.json

## What was done

Removed 8 plugins with unsupported `git-subdir` source type from the installed official Claude Code marketplace at `~/.claude/plugins/marketplaces/claude-plugins-official/.claude-plugin/marketplace.json`.

The `git-subdir` source type was added to the upstream marketplace but is not recognized by the current Claude Code schema validator, causing the entire marketplace to fail to load.

## Plugins removed

1. **semgrep** - security
2. **railway** - deployment
3. **legalzoom** - productivity
4. **amazon-location-service** - location
5. **aws-serverless** - development
6. **migration-to-aws** - migration
7. **deploy-on-aws** - deployment
8. **zapier** - productivity

## Notes

- This is a local fix to an installed marketplace file outside the repo
- The marketplace may re-pull from GitHub and reintroduce these entries
- A Claude Code update that supports `git-subdir` source type would be the permanent fix
- No repo files were modified (fix applied to `~/.claude/` directory)
