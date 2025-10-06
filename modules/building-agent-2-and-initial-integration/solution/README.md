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
   python -m ipykernel install --user --name soxlab-2 --display-name "Python (soxlab-2)"
   ```

4. **Select kernel in Cursor / Jupyter Notebook**

   * Open the notebook (`sox_copilot_lab.ipynb`).
   * Click **Select Kernel** in the top-right.
   * Choose **Jupyter Kernel → Python (soxlab-2)**.
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

Do you want me to also add a short **“Next Steps”** section (like extending the lab to other SOX controls or scaling to multi-agent orchestration), or should we keep it lean and only about setup + troubleshooting?
