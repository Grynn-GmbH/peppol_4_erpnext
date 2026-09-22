### Peppol 4 Erpnext

ERPNext client for sending and receiving e-invoices via TAPR.ch. 

Sign up here: https://cloud.tapr.ch/dashboard/create-site/inflow/setup


### Compatibility

| | Supported |
|---|---|
| Frappe | v15, v16 |
| ERPNext | v15, v16 |
| Python | 3.10 – 3.14 (a v15 bench runs 3.10–3.14, a v16 bench runs 3.14) |

One codebase covers both framework versions — there is no v15/v16 branch. `bench
install-app` refuses to install on anything older than v15 and prints a warning
(but still installs) on anything newer than v16.

Runtime dependencies beyond the framework are `dnspython` (BDXL/NAPTR resolution)
and `requests` (SMP queries); `bench get-app` installs them from `pyproject.toml`.

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app peppol_4_erpnext
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/peppol_4_erpnext
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

mit
