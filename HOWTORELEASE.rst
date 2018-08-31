Here are the steps on how to make a new release.

1. Create a ``release-VERSION`` branch from ``upstream/master``.
2. Update ``CHANGELOG.rst``.
3. Push a branch with the changes.
4. Once all builds pass, push a tag named ``VERSION`` to ``upstream``.
5. After the deployment is complete, merge the PR.
