import 'helpers.justfile'

# Stage tracked file changes and commit with a message
[group('gitflow')]
commit MESSAGE:
    git add -u
    git commit -m "{{ MESSAGE }}"

# Pushes all tags to the remote repository
[group('gitflow')]
push-tags:
    git push --tags

# Create PR for current branch
[group('gitflow')]
pr:
    @git push

    @branch=$(git rev-parse --abbrev-ref HEAD) && \
    gh pr create \
      --base main \
      --title "$branch" \
      --body "$(git log origin/main..HEAD --pretty=format:'- %s')"

# Merge PR using squash
[group('gitflow')]
merge:
    gh pr merge --squash --delete-branch
