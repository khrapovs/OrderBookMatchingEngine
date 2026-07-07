- Use uv to run python commands, e.g.

    ```shell
    uv run pytest
    ```

- Run prek on all files before each commit:

    ```shell
    uv run prek run -v --show-diff-on-failure --all-files
    ```
