# Component maintenance

This public deployment starts with a clean snapshot and pins three public submodules: [engine](https://github.com/aspose-core-mcp/context-engine), [Words plugin](https://github.com/aspose-words-mcp/cpp-plugin), and [TeX plugin](https://github.com/aspose-tex-mcp/cpp-plugin).

To update, fetch and check out reviewed commits in the relevant submodules. Stage their gitlinks before running setup, which restores indexed pins. Run setup, registration verification, and both plugin suites; review source commands if manifests change. Commit the resulting gitlinks with any required integration changes. Never initialize the engine's nested historical source submodules recursively.

The two member registrations and `aspose.total.cpp` composition belong to this deployment. Adding another product requires an explicit catalog/composition change, a compatible engine route and contract, separate source preparation, and integration tests. The Total name does not imply support for every Aspose product.

GitHub CI installs public pinned components and checks fixture extraction and mocked routing. It does not start a production service, prepare source corpora, or publish indexes. Preserve all component licenses and configure secrets outside Git.

All remote branches can be refreshed without changing pins using `git -C engine fetch origin '+refs/heads/*:refs/remotes/origin/*' --prune` (repeat for each plugin). Inspect `git -C engine branch -r`; fetch does not merge or select branches.
