- Each class should expose only those methods and attributes that are used in the other classes/functions. All other attributes and methods should be private (_method). Example:

    ```python
    class A:
        def __init__(self):
            self._x = 1 # should be private
            self.y = 2 # should be public

        def _private_method(self):
            pass # should be private

        def public_method(self):
            pass # should be public
    ```

- Unit tests are not allowed to access private attribute/methods of classes.

- Use uv to run python commands, e.g.

    ```shell
    uv run pytest
    ```

- Run prek on all files before each commit (stage all the files but do not commit):

    ```shell
    uv run prek run -v --show-diff-on-failure --all-files
    ```
