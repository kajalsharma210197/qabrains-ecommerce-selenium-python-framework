# Selenium Python Test Automation Framework (TDD)

## Overview

Python Selenium automation framework for the QA Brains practice e-commerce site using **Test-Driven Development (TDD)** with pytest:

- Selenium WebDriver 4
- **pytest** — plain Python tests (no Gherkin/BDD)
- Page Object Model (POM)
- webdriver-manager for driver binaries
- **Allure Report** — rich HTML reports with steps, attachments, and environment metadata

## Project Structure

```
allure/
  categories.json       # Defect categories (product vs test vs infra)
config/                 # Environment settings (config.properties)
framework/
  base/                 # Driver factory and base page
  config/               # Config reader
  pages/                # Page objects (login, home, cart)
  utils/                # Waits, screenshots, Allure helpers
scripts/
  view_allure_report.ps1
  serve_allure_report.ps1
tests/
  conftest.py           # pytest fixtures, Allure hooks
  test_data.py          # Test inputs and constants
  test_login.py         # Login TDD tests (@smoke)
  test_cart.py          # Cart TDD tests (@cart)
reports/
  allure-results/       # Latest Allure run data (view with Allure CLI)
  screenshots/          # Screenshots from the latest run
  videos/               # Videos from the latest run
```

## Prerequisites

- Python 3.10+
- Google Chrome (default browser)

No global Allure or Java install is required — project scripts download them automatically into `tools/` on first use.

## Setup

```bash
pip install -r requirements.txt
```

## Run Tests

Run the full suite (writes latest results to `reports/allure-results`):

```bash
pytest
```

Run login tests only:

```bash
pytest -m smoke
```

Run cart tests only:

```bash
pytest -m cart
```

## Allure Reports

### What's included (advanced details)

| Feature | Description |
|---------|-------------|
| **Epic / Feature / Story** | Test hierarchy in Behaviors tab |
| **Severity & Tags** | Priority and filtering (smoke, cart, regression) |
| **Steps** | Nested steps from tests and page objects |
| **Parameters** | Username shown; password masked |
| **Environment** | Browser, URL, headless, timeout, OS, Python version |
| **Attachments** | Screenshots, **MP4 video recording**, page source, browser logs, capabilities |
| **Categories** | Login, cart, assertion, timeout, infrastructure, skipped — see **Categories** tab |
| **Video recording** | Full test session captured and playable inside each test result |
| **Dynamic titles** | Readable names per parametrized login user |

### View Allure report

After `pytest` finishes, open the report from `reports/allure-results`:

```powershell
.\scripts\view_allure_report.ps1
```

Or:

```powershell
.\scripts\serve_allure_report.ps1
```

On the **first run**, the script downloads Allure CLI and a portable Java runtime (~80 MB) into `tools/`. Later runs are instant.

Each new `pytest` run clears previous `allure-results`, screenshots, and videos so only the latest execution is kept.

## TDD Workflow

1. Write or update a test in `tests/test_*.py` (red).
2. Implement or adjust page objects in `framework/pages/` (green).
3. Refactor shared logic into `framework/` utilities (refactor).

Test data lives in `tests/test_data.py` — update credentials and parametrized rows there.

## Configuration

Edit `config/config.properties`:

| Key | Description |
|-----|-------------|
| `qa.url` | Application login URL |
| `browser` | `chrome`, `firefox`, or `edge` |
| `headless` | `true` / `false` |
| `timeout` | Page-load and script timeout (seconds) |
| `videoRecording` | `true` / `false` — record MP4 per test |
| `videoPath` | Folder for saved videos (`reports/videos`) |
| `videoFps` | Frames per second for recording (default `8`) |
| `saveScreenshots` | `true` / `false` — save PNG per test to `reports/screenshots` |
| `allureResultsPath` | Allure results directory (`reports/allure-results`) |
