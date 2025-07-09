# Repository Migration Checklist

## GitHub Migration
- [ ] Transfer repository ownership on GitHub from personal account to `longevitycoach` organization
- [ ] Accept transfer in the longevitycoach organization (requires org admin)
- [ ] Verify repository is accessible at: https://github.com/longevitycoach/bloodtest-mcp-server

## Local Repository Update
- [ ] Update git remote URL:
  ```bash
  git remote set-url origin git@github.com:longevitycoach/bloodtest-mcp-server.git
  git remote -v  # Verify the change
  ```

## Railway Update
- [ ] Go to Railway dashboard: https://railway.com/project/f90e5f23-8158-4045-a552-e3e18e7cd64d
- [ ] Navigate to Service Settings → Source
- [ ] Click "Update Repository" or "Reconnect GitHub"
- [ ] Select `longevitycoach/Bloodtest-mcp-server` from the repository list
- [ ] Verify automatic deployment triggers are working
- [ ] Check deployment logs for any issues

## Verification Steps
- [ ] Push a test commit to verify Railway auto-deployment
- [ ] Check production URL still works: https://supplement-therapy.up.railway.app/health
- [ ] Verify SSE endpoint: https://supplement-therapy.up.railway.app/sse
- [ ] Test Claude Desktop integration still works

## Documentation Updates
- [x] Updated repository URL in README.md (line 320)
- [x] Updated clone command in README.md (line 1706)
- [x] Updated package name in pyproject.toml
- [ ] Update any CI/CD badges if present
- [ ] Update any documentation that references the old repository URL

## Additional Considerations
- [ ] Update any webhooks that point to the old repository
- [ ] Update any API keys or secrets if needed
- [ ] Notify team members of the new repository location
- [ ] Update any external services that reference the repository

## Post-Migration
- [ ] Archive or delete the old repository (optional)
- [ ] Update any bookmarks or shortcuts to the new repository URL