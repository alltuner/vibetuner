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

# Create PR for current branch (title must be conventional commit format, e.g. "feat: add login")
[group('gitflow')]
pr TITLE:
    @git push
    @gh pr create \
      --base main \
      --title "{{ TITLE }}" \
      --body "$(git log origin/main..HEAD --pretty=format:'- %s')"

# Merge PR using squash
[group('gitflow')]
merge:
    gh pr merge --squash --delete-branch
