# SOX Copilot Lab - Solution

## Setup

1. **Install dependencies**

   ```bash
   pipenv install
   ```

2. **Set up environment variables**
   Create a `.env` file in this directory:

   ```
   OPENAI_API_KEY=your_key_here
   ```

3. **Activate the virtual environment and register Jupyter kernel**

   ```bash
   pipenv shell
   python -m ipykernel install --user --name soxlab-1 --display-name "Python (soxlab-1)"
   ```

4. **Select kernel in Cursor / Jupyter Notebook**

   * Open the notebook (`sox_copilot_lab.ipynb`).
   * Click **Select Kernel** in the top-right.
   * Choose **Jupyter Kernel → Python (soxlab-1)**.
   * (If you don’t see it, hit the refresh button and look under “Jupyter Kernel.”)

---

## Troubleshooting

* **Kernel not showing up in Cursor**

  * Make sure you installed the kernel with a display name:

    ```bash
    python -m ipykernel install --user --name soxlab --display-name "Python (soxlab)"
    ```
  * Reload Cursor (Cmd+Shift+P → *Developer: Reload Window*).
  * Reopen the notebook and select **Jupyter Kernel → Python (soxlab)**.

* **Multiple environments active**
  If your shell shows both `(base)` and `(lightswitch-reporting)` or similar, deactivate the extra one:

  ```bash
  conda deactivate
  ```

  Then re-run `pipenv shell`.

* **OPENAI_API_KEY not found**

  * Ensure `.env` exists in the project root.
  * Cursor/VS Code may require a reload to pick up environment variables.
  * You can also export it directly in your shell:

    ```bash
    export OPENAI_API_KEY=your_key_here
    ```

* **Notebook cells fail to import modules**

  * Confirm dependencies are installed inside your Pipenv environment:

    ```bash
    pipenv install
    ```
  * If you added new packages, restart the kernel after installation.

---

## Running the Lab

Once your environment is set up and the kernel is selected:

1. Open `sox_copilot_lab.ipynb`
2. Run cells sequentially from top to bottom
3. The agent should automatically orchestrate tool calls and produce a structured JSON report

See the parent directory's main README.md for detailed implementation guidance and architectural explanations.
