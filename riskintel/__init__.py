"""riskintel: outline of a community risk intelligence platform.

Package layout (each sub-package is a bounded context):

- domain      shared entities, enums and value objects
- ingestion   bringing loss history, risk issues and IoT telemetry into the platform
- community   consent, peer cohorts and anonymised experience exchange
- analytics   experience statistics, development and benchmarking
- modelling   frequency/severity fitting and Monte Carlo aggregate loss
- decisions   self-insured retention (SIR) decision support
- storage     repository interfaces (in-memory for the outline)
- api         FastAPI surface
"""

__version__ = "0.1.0"
